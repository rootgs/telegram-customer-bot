# Bot de Support Client Telegram

[English README](../README.md)

Un bot Telegram léger pour recevoir les clients en message privé. Le client écrit au bot, le bot transfère le message au support, puis le support répond au message transféré afin que le bot renvoie la réponse au bon client.

## Fonctionnalités

- Réception privée des clients
- Transfert automatique vers un utilisateur ou groupe de support
- Réponse via la fonction répondre de Telegram
- Fiche client dans le chat de support
- Boutons admin : historique, définir une note, voir la note, bloquer et débloquer
- La fiche client n'est pas répétée si le même client envoie plusieurs messages à la suite
- Stockage SQLite
- Historique des conversations pour analyse ultérieure
- Message de bienvenue personnalisable
- Boutons de bienvenue côté client
- Mode polling et mode webhook
- Installateur interactif Linux
- Localisation des textes admin via `locales/*.json`

## Installation rapide Linux

```bash
chmod +x install.sh
./install.sh
```

Puis :

```bash
.venv/bin/python bot.py
```

## Configuration

```env
BOT_TOKEN=123456789:replace_with_your_bot_token
SUPPORT_CHAT_ID=-1001234567890
DB_FILE=data/bot.sqlite3
LANGUAGE=fr
LOCALES_DIR=locales
BOT_MODE=polling
```

## Webhook

```env
BOT_MODE=webhook
WEBHOOK_URL=https://bot.example.com
WEBHOOK_LISTEN=0.0.0.0
WEBHOOK_PORT=7024
WEBHOOK_PATH=telegram-webhook
WEBHOOK_SECRET_TOKEN=replace_with_a_random_secret
```

L'installateur vérifie que le domaine HTTPS se résout correctement. Avec un edge node, tunnel ou proxy inverse, transférez vers :

```text
http://127.0.0.1:7024/telegram-webhook
```

## Proxy

Si le serveur ne peut pas se connecter directement à Telegram, configurez `PROXY_URL`, par exemple `http://127.0.0.1:7890` ou `socks5://127.0.0.1:1080`.

## Commandes

```text
/whoami
/welcome
/setwelcome Bonjour, comment pouvons-nous vous aider ?
/buttons
/setbuttons Tarifs|Achat|FAQ|Support humain
/note CUSTOMER_ID texte
/shownote CUSTOMER_ID
/block CUSTOMER_ID
/unblock CUSTOMER_ID
/customer CUSTOMER_ID
/history CUSTOMER_ID
/help
```

## Langues

Les textes sont chargés depuis `locales/`. Pour ajouter une langue, copiez `locales/en.json`, traduisez les valeurs et définissez `LANGUAGE` dans `.env`.

## Sécurité

Ne publiez pas `.env`, les tokens, la base de données, l'historique ou les sauvegardes locales. Ces fichiers sont couverts par `.gitignore`.
