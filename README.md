# Telegram Customer Support Bot

Documentation:
[English](README.md) |
[简体中文](docs/README.zh-CN.md) |
[Español](docs/README.es.md) |
[Português](docs/README.pt-BR.md) |
[Français](docs/README.fr.md) |
[Русский](docs/README.ru.md) |
[العربية](docs/README.ar.md)

A lightweight Telegram customer support bot for one-to-one customer reception.

Customers message the bot privately. The bot forwards customer messages to a support chat. Support staff reply to the forwarded message, and the bot sends that reply back to the correct customer.

## Features

- Private customer reception
- Forward customer messages to a support user or support group
- Reply-to-forwarded-message workflow
- Customer profile cards in the support chat
- Inline admin actions: view history, set note, view note, block and unblock
- Consecutive messages from the same customer do not repeat the profile card
- SQLite storage
- Chat history storage for later customer analysis
- Custom welcome message
- Custom customer-side welcome buttons
- Polling mode for simple deployment
- Webhook mode for production deployment
- Linux interactive installer
- Admin-side localization through `locales/*.json`

## Requirements

- Linux server
- Python 3.11 or newer
- Telegram bot token from `@BotFather`
- A support/admin Telegram chat ID
- For webhook mode: a public HTTPS domain that resolves correctly

## Quick Install On Linux

```bash
chmod +x install.sh
./install.sh
```

After installation:

```bash
.venv/bin/python bot.py
```

## Docker

```bash
cp .env.example .env
docker compose up -d --build
```

## systemd

For long-running Linux deployments, see [systemd deployment](docs/systemd.md).

## Configuration

The installer writes `.env`. You can also create it manually from `.env.example`.

```env
BOT_TOKEN=123456789:replace_with_your_bot_token
SUPPORT_CHAT_ID=-1001234567890
DB_FILE=data/bot.sqlite3
LANGUAGE=en
LOCALES_DIR=locales
BOT_MODE=polling
```

## Getting The Support Chat ID

1. Create the bot with `@BotFather`.
2. Start the bot in polling mode.
3. Send `/whoami` to the bot from the support account, or send `/whoami` inside the support group.
4. Use the returned chat ID as `SUPPORT_CHAT_ID`.

Group and supergroup IDs are usually negative numbers. Supergroup IDs often start with `-100`.

## Polling Mode

```env
BOT_MODE=polling
```

Polling is the easiest mode. It does not need a public domain, HTTPS, reverse proxy, or edge node.

## Webhook Mode

```env
BOT_MODE=webhook
WEBHOOK_URL=https://bot.example.com
WEBHOOK_LISTEN=0.0.0.0
WEBHOOK_PORT=7024
WEBHOOK_PATH=telegram-webhook
WEBHOOK_SECRET_TOKEN=replace_with_a_random_secret
```

The final Telegram webhook URL will be:

```text
https://bot.example.com/telegram-webhook
```

The Linux installer validates that the webhook URL starts with `https://`, contains a domain name, and resolves to at least one IP address.

The default local webhook port is `7024`, representing 7x24 availability. Users can enter another port during installation. If the chosen port is already in use, the installer asks for another one.

For an edge node, tunnel, or reverse proxy, forward public HTTPS traffic to:

```text
http://127.0.0.1:7024/telegram-webhook
```

## Support Workflow

1. A customer sends a private message to the bot.
2. The bot sends a customer profile card to support unless this customer is already the current consecutive customer.
3. The bot forwards the customer message to support.
4. Support replies directly to the forwarded message.
5. The bot copies the support reply back to the customer.

Support staff must use Telegram's reply feature on the forwarded customer message. A standalone support message cannot be matched to a customer.

## Admin Buttons

Customer profile cards include inline buttons:

- History
- Set note
- View note
- Block / Unblock

The set-note button starts a two-step flow. After clicking it, the next text message from the admin is saved as an internal note and is not sent to the customer.

## Admin Commands

```text
/whoami
/welcome
/setwelcome Hello, how can we help?
/buttons
/setbuttons Pricing|Purchase flow|FAQ|Human support
/note CUSTOMER_ID note text
/shownote CUSTOMER_ID
/block CUSTOMER_ID
/unblock CUSTOMER_ID
/customer CUSTOMER_ID
/history CUSTOMER_ID
/help
```

Most customer-specific commands also work by replying to a forwarded customer message.

## Data Storage

The bot uses SQLite by default:

```text
data/bot.sqlite3
```

Stored data includes settings, customer profiles, message mappings, customer notes, block list, and chat history.

Media files are not downloaded by default. The database stores message type and text/caption metadata.

## Localization

Admin-side text is loaded from:

```text
locales/
```

Built-in locale files:

- `zh-CN.json`
- `en.json`
- `es.json`
- `pt-BR.json`
- `fr.json`
- `ru.json`
- `ar.json`

To add a new language, copy `locales/en.json`, rename it, translate the values, and set `LANGUAGE` in `.env`.

Missing translation keys fall back to English, then to built-in defaults.

## Do Not Commit

- `.env`
- `.venv/`
- `data/`
- `__pycache__/`
- `*.sqlite3`
- logs or local backups

These are covered by `.gitignore`.

## Security Notes

- Never publish your bot token.
- Rotate the token immediately if it was exposed.
- Keep `.env` private.
- Use a strong `WEBHOOK_SECRET_TOKEN` in webhook mode.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
