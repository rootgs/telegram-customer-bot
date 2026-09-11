# Telegram Customer Support Bot

[English README](../README.md)

Легкий Telegram-бот для приема клиентов в личных сообщениях. Клиент пишет боту, бот пересылает сообщение в чат поддержки, а оператор отвечает на пересланное сообщение, чтобы бот отправил ответ нужному клиенту.

## Возможности

- Прием клиентов в личных сообщениях
- Пересылка сообщений пользователю или группе поддержки
- Ответ клиенту через функцию ответа Telegram
- Карточка клиента в чате поддержки
- Кнопки администратора: история, заметка, просмотр заметки, блокировка и разблокировка
- Карточка не повторяется, если один клиент отправляет несколько сообщений подряд
- Хранение данных в SQLite
- История сообщений для последующего анализа
- Настраиваемое приветствие
- Кнопки приветствия для клиентов
- Режим polling и режим webhook
- Интерактивная установка для Linux
- Локализация через `locales/*.json`

## Быстрая установка Linux

```bash
chmod +x install.sh
./install.sh
```

Запуск:

```bash
.venv/bin/python bot.py
```

## Конфигурация

```env
BOT_TOKEN=123456789:replace_with_your_bot_token
SUPPORT_CHAT_ID=-1001234567890
DB_FILE=data/bot.sqlite3
LANGUAGE=ru
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

Установщик проверяет, что HTTPS-домен корректно резолвится. Для edge node, туннеля или reverse proxy направьте трафик на:

```text
http://127.0.0.1:7024/telegram-webhook
```

## Команды

```text
/whoami
/welcome
/setwelcome Здравствуйте, чем мы можем помочь?
/buttons
/setbuttons Цены|Покупка|FAQ|Оператор
/note CUSTOMER_ID text
/shownote CUSTOMER_ID
/block CUSTOMER_ID
/unblock CUSTOMER_ID
/customer CUSTOMER_ID
/history CUSTOMER_ID
/help
```

## Языки

Тексты загружаются из `locales/`. Чтобы добавить язык, скопируйте `locales/en.json`, переведите значения и задайте `LANGUAGE` в `.env`.

## Безопасность

Не публикуйте `.env`, токены, базу данных, историю сообщений или локальные резервные копии. Эти файлы уже указаны в `.gitignore`.
