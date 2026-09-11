import os
import secrets
import socket
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
ENV_FILE = ROOT / ".env"
DEFAULT_WEBHOOK_PORT = 7024


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def ask_choice(prompt: str, choices: list[str], default: str) -> str:
    choices_text = "/".join(choices)
    while True:
        value = ask(f"{prompt} ({choices_text})", default).lower()
        if value in choices:
            return value
        print(f"Please choose one of: {choices_text}")


def run(command: list[str]) -> None:
    print(f"> {' '.join(command)}")
    subprocess.check_call(command, cwd=ROOT)


def venv_python() -> Path:
    return VENV_DIR / "bin" / "python"


def ensure_venv() -> None:
    if not VENV_DIR.exists():
        run([sys.executable, "-m", "venv", str(VENV_DIR)])

    python = str(venv_python())
    run([python, "-m", "pip", "install", "--upgrade", "pip"])
    run([python, "-m", "pip", "install", "-r", "requirements.txt"])


def validate_webhook_url(url: str) -> tuple[str, list[str]]:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("Webhook URL must start with https://")
    if not parsed.hostname:
        raise ValueError("Webhook URL must include a domain name")

    records = socket.getaddrinfo(parsed.hostname, None)
    addresses = sorted({record[4][0] for record in records})
    if not addresses:
        raise ValueError("Domain did not resolve to any IP address")

    return parsed.hostname, addresses


def is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def ask_available_port(host: str) -> str:
    while True:
        raw_port = ask("Local webhook port", str(DEFAULT_WEBHOOK_PORT))
        try:
            port = int(raw_port)
        except ValueError:
            print("Port must be a number.")
            continue

        if not 1 <= port <= 65535:
            print("Port must be between 1 and 65535.")
            continue

        if not is_port_available(port, host):
            print(f"Port {port} is already in use. Please choose another one.")
            continue

        return str(port)


def write_env(values: dict[str, str]) -> None:
    lines = [f"{key}={value}" for key, value in values.items()]
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    print("Telegram Customer Support Bot Installer")
    print("---------------------------------------")

    bot_token = ask("Bot token")
    support_chat_id = ask("Support/admin chat ID")
    language = ask("Language", "en")
    bot_mode = ask_choice("Install mode", ["polling", "webhook"], "polling")

    values = {
        "BOT_TOKEN": bot_token,
        "SUPPORT_CHAT_ID": support_chat_id,
        "DB_FILE": "data/bot.sqlite3",
        "LANGUAGE": language,
        "LOCALES_DIR": "locales",
        "BOT_MODE": bot_mode,
    }

    use_proxy = ask_choice("Use proxy for Telegram API", ["no", "yes"], "no")
    if use_proxy == "yes":
        proxy_url = ask("Proxy URL, for example http://127.0.0.1:7890 or socks5://127.0.0.1:1080")
        get_updates_proxy_url = ask("Proxy URL for polling getUpdates, leave empty to use the same proxy", proxy_url)
        values["PROXY_URL"] = proxy_url
        values["GET_UPDATES_PROXY_URL"] = get_updates_proxy_url
    else:
        values["PROXY_URL"] = ""
        values["GET_UPDATES_PROXY_URL"] = ""

    if bot_mode == "webhook":
        while True:
            webhook_url = ask("Edge public HTTPS URL, for example https://bot.example.com")
            try:
                hostname, addresses = validate_webhook_url(webhook_url)
            except ValueError as error:
                print(f"Webhook URL check failed: {error}")
                continue
            except socket.gaierror:
                print("Webhook domain check failed: domain does not resolve.")
                continue

            print(f"Domain resolved: {hostname} -> {', '.join(addresses)}")
            break

        listen_host = ask("Local webhook listen host", "0.0.0.0")
        local_port = ask_available_port(listen_host)
        webhook_path = ask("Webhook path", "telegram-webhook")

        values.update(
            {
                "WEBHOOK_URL": webhook_url.rstrip("/"),
                "WEBHOOK_LISTEN": listen_host,
                "WEBHOOK_PORT": local_port,
                "WEBHOOK_PATH": webhook_path,
                "WEBHOOK_SECRET_TOKEN": ask(
                    "Webhook secret token", secrets.token_urlsafe(32)
                ),
            }
        )

        print("")
        print("Edge node forwarding target:")
        print(f"  http://127.0.0.1:{local_port}/{webhook_path}")

    write_env(values)
    ensure_venv()

    print("")
    print("Installation complete.")
    print(f"Config file: {ENV_FILE}")
    print("Start bot: .venv/bin/python bot.py")


if __name__ == "__main__":
    main()
