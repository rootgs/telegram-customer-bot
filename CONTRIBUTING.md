# Contributing

Thanks for helping improve Telegram Customer Support Bot.

## Development Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`, then run:

```bash
.venv/bin/python bot.py
```

## Checks

Before opening a pull request:

```bash
.venv/bin/python -m py_compile bot.py install.py
.venv/bin/python -m unittest discover -s tests
```

## Translation Updates

Admin-side messages live in `locales/*.json`.

To add a language:

1. Copy `locales/en.json`.
2. Rename it to the new language code, such as `locales/de.json`.
3. Translate the values, keeping the keys unchanged.
4. Add the language to the README language list if you also add docs.

## Security

Never commit:

- Bot tokens
- GitHub tokens
- `.env`
- SQLite databases
- Chat history
- Local logs

If a token is exposed, revoke it immediately.
