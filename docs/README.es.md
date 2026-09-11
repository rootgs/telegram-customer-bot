# Bot de Soporte al Cliente para Telegram

[English README](../README.md)

Un bot ligero de Telegram para atender clientes por mensajes privados. El cliente escribe al bot, el bot reenvía el mensaje al chat de soporte, y el equipo responde al mensaje reenviado para que el bot envíe la respuesta al cliente correcto.

## Funciones

- Atención privada de clientes
- Reenvío automático a un usuario o grupo de soporte
- Respuesta al cliente usando la función de responder de Telegram
- Tarjeta de cliente en el chat de soporte
- Botones de administración: historial, nota, ver nota, bloquear y desbloquear
- No repite la tarjeta si el mismo cliente envía varios mensajes seguidos
- Almacenamiento con SQLite
- Historial de chat para análisis posterior
- Mensaje de bienvenida personalizable
- Botones de bienvenida para clientes
- Modo polling y modo webhook
- Instalador interactivo para Linux
- Textos del panel de soporte mediante `locales/*.json`

## Instalación rápida en Linux

```bash
chmod +x install.sh
./install.sh
```

Después de instalar:

```bash
.venv/bin/python bot.py
```

## Configuración

```env
BOT_TOKEN=123456789:replace_with_your_bot_token
SUPPORT_CHAT_ID=-1001234567890
DB_FILE=data/bot.sqlite3
LANGUAGE=es
LOCALES_DIR=locales
BOT_MODE=polling
```

## Modos de ejecución

Polling es la opción más sencilla y no requiere dominio público.

Webhook es recomendable para producción:

```env
BOT_MODE=webhook
WEBHOOK_URL=https://bot.example.com
WEBHOOK_LISTEN=0.0.0.0
WEBHOOK_PORT=7024
WEBHOOK_PATH=telegram-webhook
WEBHOOK_SECRET_TOKEN=replace_with_a_random_secret
```

El instalador valida que el dominio HTTPS resuelva correctamente. Si usas un nodo edge, túnel o proxy inverso, reenvía el tráfico público a:

```text
http://127.0.0.1:7024/telegram-webhook
```

## Comandos principales

```text
/whoami
/welcome
/setwelcome Hola, ¿cómo podemos ayudarte?
/buttons
/setbuttons Precios|Compra|FAQ|Soporte humano
/note CUSTOMER_ID texto
/shownote CUSTOMER_ID
/block CUSTOMER_ID
/unblock CUSTOMER_ID
/customer CUSTOMER_ID
/history CUSTOMER_ID
/help
```

## Idiomas

Los textos se cargan desde `locales/`. Para agregar un idioma, copia `locales/en.json`, traduce los valores y cambia `LANGUAGE` en `.env`.

## Seguridad

No publiques `.env`, tokens, bases de datos, historiales ni copias locales. Estos archivos están cubiertos por `.gitignore`.
