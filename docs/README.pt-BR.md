# Bot de Atendimento ao Cliente para Telegram

[English README](../README.md)

Um bot leve de Telegram para atendimento privado. O cliente envia mensagem ao bot, o bot encaminha para o chat de suporte, e a equipe responde à mensagem encaminhada para que o bot envie a resposta ao cliente correto.

## Recursos

- Atendimento privado de clientes
- Encaminhamento automático para usuário ou grupo de suporte
- Fluxo de resposta usando a função responder do Telegram
- Cartão do cliente no chat de suporte
- Botões administrativos: histórico, definir nota, ver nota, bloquear e desbloquear
- Não repete o cartão quando o mesmo cliente envia mensagens seguidas
- Armazenamento em SQLite
- Histórico de conversas para análise posterior
- Mensagem de boas-vindas personalizável
- Botões de boas-vindas para clientes
- Modo polling e modo webhook
- Instalador interativo para Linux
- Textos administrativos via `locales/*.json`

## Instalação rápida no Linux

```bash
chmod +x install.sh
./install.sh
```

Depois:

```bash
.venv/bin/python bot.py
```

## Configuração

```env
BOT_TOKEN=123456789:replace_with_your_bot_token
SUPPORT_CHAT_ID=-1001234567890
DB_FILE=data/bot.sqlite3
LANGUAGE=pt-BR
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

O instalador valida se o domínio HTTPS resolve corretamente. Para edge node, túnel ou proxy reverso, encaminhe para:

```text
http://127.0.0.1:7024/telegram-webhook
```

## Comandos

```text
/whoami
/welcome
/setwelcome Olá, como podemos ajudar?
/buttons
/setbuttons Preços|Compra|FAQ|Atendimento humano
/note CUSTOMER_ID texto
/shownote CUSTOMER_ID
/block CUSTOMER_ID
/unblock CUSTOMER_ID
/customer CUSTOMER_ID
/history CUSTOMER_ID
/help
```

## Idiomas

Os textos vêm de `locales/`. Para adicionar idioma, copie `locales/en.json`, traduza os valores e defina `LANGUAGE` em `.env`.

## Segurança

Não publique `.env`, tokens, banco de dados, histórico ou backups locais. Esses arquivos já estão no `.gitignore`.
