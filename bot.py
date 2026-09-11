import json
import logging
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ChatType
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPPORT_CHAT_ID = os.getenv("SUPPORT_CHAT_ID")
DB_FILE = Path(os.getenv("DB_FILE", "data/bot.sqlite3"))
BOT_MODE = os.getenv("BOT_MODE", "polling").lower()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_LISTEN = os.getenv("WEBHOOK_LISTEN", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "7024"))
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "telegram-webhook")
WEBHOOK_SECRET_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN", "")
LANGUAGE = os.getenv("LANGUAGE", "en")
LOCALES_DIR = Path(os.getenv("LOCALES_DIR", "locales"))
LEGACY_DATA_FILE = Path("data/message_map.json")
LEGACY_SETTINGS_FILE = Path("data/settings.json")
DEFAULT_WELCOME_MESSAGE = "Hello, please send your question. Support will reply as soon as possible."
DEFAULT_LOCALE = {
    "welcome_message": DEFAULT_WELCOME_MESSAGE,
    "support_start": "Support mode is enabled. Reply directly to a customer message and the bot will send it back to that customer.",
    "no_permission": "No permission",
    "queried": "Done",
    "send_note": "Send note",
    "customer_note_prompt": "Please send the note for customer {customer_id}. Your next text message will be saved as an internal note and will not be sent to the customer.",
    "customer_note_saved": "Note saved for customer {customer_id}.",
    "note_saved": "Customer note saved.",
    "text_note_required": "Please send a text note.",
    "blocked_done": "Customer {customer_id} has been blocked.",
    "unblocked_done": "Customer {customer_id} has been unblocked.",
    "customer_profile_title": "Customer Profile",
    "customer": "Customer",
    "username": "Username",
    "customer_id": "Customer ID",
    "first_seen": "First seen",
    "last_seen": "Last seen",
    "message_count": "Message count",
    "blocked": "Blocked",
    "note": "Note",
    "yes": "Yes",
    "no": "No",
    "none": "None",
    "no_username": "No username",
    "unknown_customer": "Unknown customer",
    "btn_history": "History",
    "btn_set_note": "Set note",
    "btn_show_note": "View note",
    "btn_block": "Block",
    "btn_unblock": "Unblock",
    "history_title": "Recent history for customer {customer_id}:",
    "no_history": "No chat history for this customer yet.",
    "speaker_customer": "Customer",
    "speaker_support": "Support",
    "support_not_configured": "Please configure SUPPORT_CHAT_ID in .env first.",
    "bot_configuring": "The bot is being configured. Please try again later.",
    "reply_customer_message": "Please reply to a customer message so I know which customer to contact.",
    "mapping_not_found": "I could not find the customer for this message. Please reply to the original forwarded customer message.",
    "current_chat_id": "Current chat ID: {chat_id}",
    "help_text": "Admin commands:\n/whoami Show current chat ID\n/welcome Show welcome message\n/setwelcome text Set /start welcome message\n/buttons Show welcome buttons\n/setbuttons Button 1|Button 2|Button 3 Set welcome buttons\n/note customer_id text Add an internal note, also works by replying to a customer message\n/shownote customer_id Show note, also works by replying\n/block customer_id Block customer, also works by replying\n/unblock customer_id Unblock customer\n/customer customer_id Show customer profile, also works by replying\n/history customer_id Show recent history, also works by replying\nUse the buttons under customer cards to view history, view notes, set notes, block or unblock.",
    "current_welcome": "Current welcome message:\n{welcome_message}",
    "setwelcome_usage": "Usage: /setwelcome Hello, how can we help?",
    "welcome_updated": "Welcome message updated.",
    "current_buttons": "Current welcome buttons:\n{buttons}",
    "buttons_empty": "Not set",
    "buttons_updated": "Welcome buttons updated.",
    "note_usage": "Use: /note customer_id note, or reply to a customer message with /note note.",
    "note_required": "Please enter note content.",
    "shownote_usage": "Use: /shownote customer_id, or reply to a customer message with /shownote.",
    "customer_note": "Customer {customer_id} note:\n{note}",
    "block_usage": "Use: /block customer_id, or reply to a customer message with /block.",
    "unblock_usage": "Use: /unblock customer_id.",
    "customer_usage": "Use: /customer customer_id, or reply to a customer message with /customer.",
    "customer_missing": "No profile for this customer yet.",
    "history_usage": "Use: /history customer_id, or reply to a customer message with /history.",
    "reply_sent": "Reply sent to customer.",
}

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def load_locale(language: str) -> dict:
    locale = DEFAULT_LOCALE.copy()
    for locale_file in (LOCALES_DIR / "en.json", LOCALES_DIR / f"{language}.json"):
        if locale_file.exists():
            with locale_file.open("r", encoding="utf-8") as file:
                locale.update(json.load(file))
    return locale


LOCALE = load_locale(LANGUAGE)


def tr(key: str, **kwargs) -> str:
    text = LOCALE.get(key, DEFAULT_LOCALE.get(key, key))
    return text.format(**kwargs) if kwargs else text


def require_bot_token() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("Missing BOT_TOKEN in environment.")


def require_support_chat_id() -> int:
    if not SUPPORT_CHAT_ID:
        raise RuntimeError("Missing SUPPORT_CHAT_ID in environment.")
    return int(SUPPORT_CHAT_ID)


def db_connect() -> sqlite3.Connection:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with db_connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS message_map (
                support_message_id INTEGER PRIMARY KEY,
                customer_chat_id INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS customers (
                customer_chat_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                message_count INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS blocked_customers (
                customer_chat_id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS customer_notes (
                customer_chat_id INTEGER PRIMARY KEY,
                note TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_chat_id INTEGER NOT NULL,
                direction TEXT NOT NULL,
                telegram_message_id INTEGER NOT NULL,
                support_message_id INTEGER,
                sender_user_id INTEGER,
                sender_name TEXT,
                sender_username TEXT,
                message_type TEXT NOT NULL,
                text TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_messages_customer_created
            ON messages (customer_chat_id, created_at);
            """
        )
        db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            ("welcome_message", tr("welcome_message")),
        )
        db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            ("welcome_buttons", "[]"),
        )
    migrate_legacy_json()


def migrate_legacy_json() -> None:
    if LEGACY_DATA_FILE.exists():
        with LEGACY_DATA_FILE.open("r", encoding="utf-8") as file:
            message_map = json.load(file)
        with db_connect() as db:
            for support_message_id, customer_chat_id in message_map.items():
                db.execute(
                    """
                    INSERT OR IGNORE INTO message_map (support_message_id, customer_chat_id)
                    VALUES (?, ?)
                    """,
                    (int(support_message_id), int(customer_chat_id)),
                )

    if not LEGACY_SETTINGS_FILE.exists():
        return

    with LEGACY_SETTINGS_FILE.open("r", encoding="utf-8") as file:
        settings = json.load(file)

    if settings.get("welcome_message"):
        set_setting("welcome_message", settings["welcome_message"])
    if settings.get("welcome_buttons"):
        set_welcome_buttons(settings["welcome_buttons"])

    with db_connect() as db:
        for customer_id, note in settings.get("customer_notes", {}).items():
            db.execute(
                """
                INSERT OR IGNORE INTO customer_notes (customer_chat_id, note)
                VALUES (?, ?)
                """,
                (int(customer_id), note),
            )
        for customer_id in settings.get("blocked_customers", {}):
            db.execute(
                "INSERT OR IGNORE INTO blocked_customers (customer_chat_id) VALUES (?)",
                (int(customer_id),),
            )
        for customer_id, profile in settings.get("customers", {}).items():
            db.execute(
                """
                INSERT OR IGNORE INTO customers (
                    customer_chat_id, full_name, username, first_seen, last_seen, message_count
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    int(customer_id),
                    profile.get("full_name", tr("unknown_customer")),
                    profile.get("username", ""),
                    profile.get("first_seen", ""),
                    profile.get("last_seen", ""),
                    int(profile.get("message_count", 0)),
                ),
            )


def get_setting(key: str, default: str = "") -> str:
    with db_connect() as db:
        row = db.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with db_connect() as db:
        db.execute(
            """
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )


def get_welcome_buttons() -> list[str]:
    return json.loads(get_setting("welcome_buttons", "[]"))


def set_welcome_buttons(buttons: list[str]) -> None:
    set_setting("welcome_buttons", json.dumps(buttons, ensure_ascii=False))


def should_show_customer_card(customer_chat_id: int) -> bool:
    last_customer_id = get_setting("last_visible_customer_chat_id", "")
    return last_customer_id != str(customer_chat_id)


def set_last_visible_customer(customer_chat_id: int) -> None:
    set_setting("last_visible_customer_chat_id", str(customer_chat_id))


def save_message_map(support_message_id: int, customer_chat_id: int) -> None:
    with db_connect() as db:
        db.execute(
            """
            INSERT INTO message_map (support_message_id, customer_chat_id)
            VALUES (?, ?)
            ON CONFLICT(support_message_id) DO UPDATE SET
                customer_chat_id = excluded.customer_chat_id
            """,
            (support_message_id, customer_chat_id),
        )


def get_customer_id_by_support_message(support_message_id: int) -> int | None:
    with db_connect() as db:
        row = db.execute(
            "SELECT customer_chat_id FROM message_map WHERE support_message_id = ?",
            (support_message_id,),
        ).fetchone()
    return int(row["customer_chat_id"]) if row else None


def get_message_text(message) -> str:
    return message.text or message.caption or ""


def get_message_type(message) -> str:
    if message.text:
        return "text"
    if message.photo:
        return "photo"
    if message.video:
        return "video"
    if message.document:
        return "document"
    if message.voice:
        return "voice"
    if message.audio:
        return "audio"
    if message.sticker:
        return "sticker"
    if message.animation:
        return "animation"
    if message.contact:
        return "contact"
    if message.location:
        return "location"
    return "other"


def save_chat_message(
    *,
    customer_chat_id: int,
    direction: str,
    telegram_message_id: int,
    created_at: str,
    message,
    support_message_id: int | None = None,
    user=None,
) -> None:
    with db_connect() as db:
        db.execute(
            """
            INSERT INTO messages (
                customer_chat_id, direction, telegram_message_id, support_message_id,
                sender_user_id, sender_name, sender_username, message_type, text, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_chat_id,
                direction,
                telegram_message_id,
                support_message_id,
                user.id if user else None,
                user.full_name if user else "",
                user.username if user and user.username else "",
                get_message_type(message),
                get_message_text(message),
                created_at,
            ),
        )


def get_customer_history(customer_chat_id: int, limit: int = 10) -> list[dict]:
    with db_connect() as db:
        rows = db.execute(
            """
            SELECT direction, sender_name, message_type, text, created_at
            FROM messages
            WHERE customer_chat_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (customer_chat_id, limit),
        ).fetchall()
    return [dict(row) for row in reversed(rows)]


def is_support_chat(update: Update) -> bool:
    return bool(
        SUPPORT_CHAT_ID
        and update.effective_chat
        and update.effective_chat.id == int(SUPPORT_CHAT_ID)
    )


def resolve_customer_id(update: Update, args: list[str]) -> int | None:
    if args and args[0].lstrip("-").isdigit():
        try:
            return int(args[0])
        except ValueError:
            return None

    message = update.effective_message
    if not message or not message.reply_to_message:
        return None

    return get_customer_id_by_support_message(message.reply_to_message.message_id)


def build_welcome_keyboard() -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    buttons = get_welcome_buttons()
    if not buttons:
        return ReplyKeyboardRemove()

    rows = [[KeyboardButton(text=button)] for button in buttons]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=False)


def update_customer_profile(update: Update) -> dict:
    chat = update.effective_chat
    user = update.effective_user
    now = update.effective_message.date.isoformat()

    with db_connect() as db:
        db.execute(
            """
            INSERT INTO customers (
                customer_chat_id, full_name, username, first_seen, last_seen, message_count
            )
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(customer_chat_id) DO UPDATE SET
                full_name = excluded.full_name,
                username = excluded.username,
                last_seen = excluded.last_seen,
                message_count = customers.message_count + 1
            """,
            (
                chat.id,
                user.full_name if user else tr("unknown_customer"),
                user.username if user and user.username else "",
                now,
                now,
            ),
        )
    return get_customer_profile(chat.id)


def get_customer_profile(customer_chat_id: int) -> dict | None:
    with db_connect() as db:
        row = db.execute(
            "SELECT * FROM customers WHERE customer_chat_id = ?",
            (customer_chat_id,),
        ).fetchone()
    return dict(row) if row else None


def get_customer_note(customer_chat_id: int) -> str:
    with db_connect() as db:
        row = db.execute(
            "SELECT note FROM customer_notes WHERE customer_chat_id = ?",
            (customer_chat_id,),
        ).fetchone()
    return row["note"] if row else tr("none")


def is_blocked(customer_chat_id: int) -> bool:
    with db_connect() as db:
        row = db.execute(
            "SELECT 1 FROM blocked_customers WHERE customer_chat_id = ?",
            (customer_chat_id,),
        ).fetchone()
    return bool(row)


def build_customer_card(profile: dict) -> str:
    customer_id = profile["customer_chat_id"]
    username = f"@{profile['username']}" if profile.get("username") else tr("no_username")
    note = get_customer_note(customer_id)
    blocked = tr("yes") if is_blocked(customer_id) else tr("no")
    return (
        f"{tr('customer_profile_title')}\n"
        f"{tr('customer')}：{profile.get('full_name', tr('unknown_customer'))}\n"
        f"{tr('username')}：{username}\n"
        f"{tr('customer_id')}：{customer_id}\n"
        f"{tr('first_seen')}：{profile.get('first_seen', '-')}\n"
        f"{tr('last_seen')}：{profile.get('last_seen', '-')}\n"
        f"{tr('message_count')}：{profile.get('message_count', 0)}\n"
        f"{tr('blocked')}：{blocked}\n"
        f"{tr('note')}：{note}"
    )


def build_customer_actions(customer_chat_id: int) -> InlineKeyboardMarkup:
    block_text = tr("btn_unblock") if is_blocked(customer_chat_id) else tr("btn_block")
    block_action = "unblock" if is_blocked(customer_chat_id) else "block"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(tr("btn_history"), callback_data=f"history:{customer_chat_id}"),
                InlineKeyboardButton(tr("btn_set_note"), callback_data=f"setnote:{customer_chat_id}"),
            ],
            [
                InlineKeyboardButton(tr("btn_show_note"), callback_data=f"note:{customer_chat_id}"),
                InlineKeyboardButton(block_text, callback_data=f"{block_action}:{customer_chat_id}"),
            ],
        ]
    )


def format_history(customer_chat_id: int, limit: int = 10) -> str:
    history = get_customer_history(customer_chat_id, limit=limit)
    if not history:
        return tr("no_history")

    lines = [tr("history_title", customer_id=customer_chat_id)]
    for item in history:
        speaker = tr("speaker_customer") if item["direction"] == "customer_to_support" else tr("speaker_support")
        content = item["text"] or f"[{item['message_type']}]"
        lines.append(f"{item['created_at']} {speaker}：{content}")
    return "\n".join(lines)


async def customer_action_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    if not query or not query.message:
        return

    if not SUPPORT_CHAT_ID or query.message.chat.id != int(SUPPORT_CHAT_ID):
        await query.answer(tr("no_permission"))
        return

    action, raw_customer_id = query.data.split(":", 1)
    customer_id = int(raw_customer_id)

    if action == "history":
        await query.answer(tr("queried"))
        await query.message.reply_text(format_history(customer_id))
        return

    if action == "note":
        await query.answer(tr("queried"))
        await query.message.reply_text(tr("customer_note", customer_id=customer_id, note=get_customer_note(customer_id)))
        return

    if action == "setnote":
        context.user_data["pending_note_customer_id"] = customer_id
        await query.answer(tr("send_note"))
        await query.message.reply_text(
            tr("customer_note_prompt", customer_id=customer_id)
        )
        return

    if action == "block":
        with db_connect() as db:
            db.execute(
                "INSERT OR IGNORE INTO blocked_customers (customer_chat_id) VALUES (?)",
                (customer_id,),
            )
        await query.answer(tr("blocked_done", customer_id=customer_id))
        await query.edit_message_reply_markup(reply_markup=build_customer_actions(customer_id))
        await query.message.reply_text(tr("blocked_done", customer_id=customer_id))
        return

    if action == "unblock":
        with db_connect() as db:
            db.execute(
                "DELETE FROM blocked_customers WHERE customer_chat_id = ?",
                (customer_id,),
            )
        await query.answer(tr("unblocked_done", customer_id=customer_id))
        await query.edit_message_reply_markup(reply_markup=build_customer_actions(customer_id))
        await query.message.reply_text(tr("unblocked_done", customer_id=customer_id))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        return

    support_chat_id = int(SUPPORT_CHAT_ID) if SUPPORT_CHAT_ID else None
    if update.effective_chat.id == support_chat_id:
        await update.effective_message.reply_text(
            tr("support_start")
        )
        return

    await update.effective_message.reply_text(
        get_setting("welcome_message", tr("welcome_message")),
        reply_markup=build_welcome_keyboard(),
    )


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        return
    await update.effective_message.reply_text(tr("current_chat_id", chat_id=update.effective_chat.id))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    await update.effective_message.reply_text(tr("help_text"))


async def show_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    await update.effective_message.reply_text(
        tr("current_welcome", welcome_message=get_setting("welcome_message", tr("welcome_message")))
    )


async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    welcome_message = " ".join(context.args).strip()
    if not welcome_message:
        await update.effective_message.reply_text(
            tr("setwelcome_usage")
        )
        return

    set_setting("welcome_message", welcome_message)
    await update.effective_message.reply_text(tr("welcome_updated"))


async def show_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    buttons = get_welcome_buttons()
    text = tr("current_buttons", buttons=("\n".join(buttons) if buttons else tr("buttons_empty")))
    await update.effective_message.reply_text(text)


async def set_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    raw_text = " ".join(context.args).strip()
    buttons = [button.strip() for button in raw_text.split("|") if button.strip()]
    set_welcome_buttons(buttons[:8])
    await update.effective_message.reply_text(tr("buttons_updated"))


async def set_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    customer_id = resolve_customer_id(update, context.args)
    if not customer_id:
        await update.effective_message.reply_text(tr("note_usage"))
        return

    note_parts = context.args[1:] if context.args and context.args[0].lstrip("-").isdigit() else context.args
    note = " ".join(note_parts).strip()
    if not note:
        await update.effective_message.reply_text(tr("note_required"))
        return

    with db_connect() as db:
        db.execute(
            """
            INSERT INTO customer_notes (customer_chat_id, note, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(customer_chat_id) DO UPDATE SET
                note = excluded.note,
                updated_at = CURRENT_TIMESTAMP
            """,
            (customer_id, note),
        )
    await update.effective_message.reply_text(tr("note_saved"))


async def show_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    customer_id = resolve_customer_id(update, context.args)
    if not customer_id:
        await update.effective_message.reply_text(tr("shownote_usage"))
        return

    note = get_customer_note(customer_id)
    await update.effective_message.reply_text(tr("customer_note", customer_id=customer_id, note=note))


async def block_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    customer_id = resolve_customer_id(update, context.args)
    if not customer_id:
        await update.effective_message.reply_text(tr("block_usage"))
        return

    with db_connect() as db:
        db.execute(
            "INSERT OR IGNORE INTO blocked_customers (customer_chat_id) VALUES (?)",
            (customer_id,),
        )
    await update.effective_message.reply_text(tr("blocked_done", customer_id=customer_id))


async def unblock_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    customer_id = resolve_customer_id(update, context.args)
    if not customer_id:
        await update.effective_message.reply_text(tr("unblock_usage"))
        return

    with db_connect() as db:
        db.execute(
            "DELETE FROM blocked_customers WHERE customer_chat_id = ?",
            (customer_id,),
        )
    await update.effective_message.reply_text(tr("unblocked_done", customer_id=customer_id))


async def show_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    customer_id = resolve_customer_id(update, context.args)
    if not customer_id:
        await update.effective_message.reply_text(tr("customer_usage"))
        return

    profile = get_customer_profile(customer_id)
    if not profile:
        await update.effective_message.reply_text(tr("customer_missing"))
        return

    await update.effective_message.reply_text(
        build_customer_card(profile),
        reply_markup=build_customer_actions(customer_id),
    )


async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_support_chat(update):
        return

    customer_id = resolve_customer_id(update, context.args)
    if not customer_id:
        await update.effective_message.reply_text(tr("history_usage"))
        return

    await update.effective_message.reply_text(format_history(customer_id))


async def handle_customer_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not message or not chat or chat.type != ChatType.PRIVATE:
        return

    if not SUPPORT_CHAT_ID:
        await message.reply_text(tr("bot_configuring"))
        return

    support_chat_id = require_support_chat_id()
    if chat.id == support_chat_id:
        return

    if is_blocked(chat.id):
        return

    profile = update_customer_profile(update)
    if should_show_customer_card(chat.id):
        await context.bot.send_message(
            chat_id=support_chat_id,
            text=build_customer_card(profile),
            reply_markup=build_customer_actions(chat.id),
        )
        set_last_visible_customer(chat.id)

    forwarded = await message.forward(chat_id=support_chat_id)

    save_message_map(forwarded.message_id, chat.id)
    save_chat_message(
        customer_chat_id=chat.id,
        direction="customer_to_support",
        telegram_message_id=message.message_id,
        support_message_id=forwarded.message_id,
        created_at=message.date.isoformat(),
        message=message,
        user=user,
    )


async def handle_support_reply(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = update.effective_message
    chat = update.effective_chat
    if not message or not chat:
        return

    if not SUPPORT_CHAT_ID:
        await message.reply_text(tr("support_not_configured"))
        return

    support_chat_id = require_support_chat_id()
    if chat.id != support_chat_id:
        return

    pending_note_customer_id = context.user_data.pop("pending_note_customer_id", None)
    if pending_note_customer_id:
        note = get_message_text(message).strip()
        if not note:
            context.user_data["pending_note_customer_id"] = pending_note_customer_id
            await message.reply_text(tr("text_note_required"))
            return

        with db_connect() as db:
            db.execute(
                """
                INSERT INTO customer_notes (customer_chat_id, note, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(customer_chat_id) DO UPDATE SET
                    note = excluded.note,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (pending_note_customer_id, note),
            )
        await message.reply_text(tr("customer_note_saved", customer_id=pending_note_customer_id))
        return

    if not message.reply_to_message:
        await message.reply_text(tr("reply_customer_message"))
        return

    customer_chat_id = get_customer_id_by_support_message(message.reply_to_message.message_id)
    if not customer_chat_id:
        await message.reply_text(tr("mapping_not_found"))
        return

    await context.bot.copy_message(
        chat_id=customer_chat_id,
        from_chat_id=chat.id,
        message_id=message.message_id,
    )
    save_chat_message(
        customer_chat_id=customer_chat_id,
        direction="support_to_customer",
        telegram_message_id=message.message_id,
        created_at=message.date.isoformat(),
        message=message,
        user=update.effective_user,
    )
    await message.reply_text(tr("reply_sent"))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)


def main() -> None:
    require_bot_token()
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("welcome", show_welcome))
    app.add_handler(CommandHandler("setwelcome", set_welcome))
    app.add_handler(CommandHandler("buttons", show_buttons))
    app.add_handler(CommandHandler("setbuttons", set_buttons))
    app.add_handler(CommandHandler("note", set_note))
    app.add_handler(CommandHandler("shownote", show_note))
    app.add_handler(CommandHandler("block", block_customer))
    app.add_handler(CommandHandler("unblock", unblock_customer))
    app.add_handler(CommandHandler("customer", show_customer))
    app.add_handler(CommandHandler("history", show_history))
    app.add_handler(CallbackQueryHandler(customer_action_callback, pattern="^(history|note|setnote|block|unblock):"))
    app.add_handler(MessageHandler(~filters.COMMAND, handle_support_reply), group=0)
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, handle_customer_message), group=1)
    app.add_error_handler(error_handler)

    logger.info("Bot started with %s mode", BOT_MODE)
    if BOT_MODE == "webhook":
        if not WEBHOOK_URL:
            raise RuntimeError("WEBHOOK_URL is required when BOT_MODE=webhook.")

        app.run_webhook(
            listen=WEBHOOK_LISTEN,
            port=WEBHOOK_PORT,
            url_path=WEBHOOK_PATH,
            webhook_url=f"{WEBHOOK_URL.rstrip('/')}/{WEBHOOK_PATH}",
            secret_token=WEBHOOK_SECRET_TOKEN or None,
            allowed_updates=Update.ALL_TYPES,
        )
        return

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
