# Telegram 客户接待机器人

[English README](../README.md)

一个轻量级 Telegram 客户接待机器人。客户私聊机器人发送消息，机器人自动转发到客服账号或客服群。客服直接回复被转发的客户消息，机器人会把回复发回对应客户。

## 功能

- 客户私聊接待
- 自动转发客户消息到客服账号或客服群
- 客服回复客户消息后自动回传给客户
- 客服端客户资料卡
- 客服端按钮操作：查看历史、设置备注、查看备注、拉黑、解除拉黑
- 同一客户连续发消息时不重复显示资料卡
- SQLite 数据库存储
- 保存聊天记录，方便后期分析客户画像
- 自定义欢迎语
- 自定义客户欢迎按钮
- 支持 polling 模式
- 支持 webhook 模式
- Linux 交互式一键安装
- 管理端多语言，支持通过 `locales/*.json` 扩展新语言

## 环境要求

- Linux 服务器
- Python 3.11 或更高版本
- 从 `@BotFather` 获取 Telegram Bot Token
- 一个客服/管理员 Telegram chat ID
- 如果使用 webhook：需要一个能正常解析的公网 HTTPS 域名

## Linux 一键安装

```bash
chmod +x install.sh
./install.sh
```

安装完成后启动：

```bash
.venv/bin/python bot.py
```

## 配置

安装脚本会生成 `.env`。也可以复制 `.env.example` 手动创建。

```env
BOT_TOKEN=123456789:replace_with_your_bot_token
SUPPORT_CHAT_ID=-1001234567890
DB_FILE=data/bot.sqlite3
LANGUAGE=zh-CN
LOCALES_DIR=locales
BOT_MODE=polling
```

## 获取客服 Chat ID

1. 使用 `@BotFather` 创建机器人。
2. 先用 polling 模式启动机器人。
3. 用客服账号私聊机器人发送 `/whoami`，或在客服群里发送 `/whoami`。
4. 机器人返回的 ID 就是 `SUPPORT_CHAT_ID`。

群和超级群 ID 通常是负数，超级群 ID 常以 `-100` 开头。

## Polling 模式

```env
BOT_MODE=polling
```

Polling 是最简单的运行方式，不需要公网域名、HTTPS、反向代理或边缘节点。

## Webhook 模式

```env
BOT_MODE=webhook
WEBHOOK_URL=https://bot.example.com
WEBHOOK_LISTEN=0.0.0.0
WEBHOOK_PORT=7024
WEBHOOK_PATH=telegram-webhook
WEBHOOK_SECRET_TOKEN=replace_with_a_random_secret
```

最终 Telegram webhook 地址是：

```text
https://bot.example.com/telegram-webhook
```

Linux 安装脚本会校验 webhook URL 必须以 `https://` 开头、包含域名，并且域名能解析到至少一个 IP。

Webhook 默认本地端口是 `7024`，表示应用可以 7x24 小时运行。用户安装时可以输入其他端口。如果端口已被占用，脚本会提示重新输入。

如果使用边缘节点、隧道或反向代理，把公网 HTTPS 地址转发到：

```text
http://127.0.0.1:7024/telegram-webhook
```

## 客服工作流

1. 客户私聊机器人发送消息。
2. 机器人向客服端发送客户资料卡；如果同一客户连续发消息，则不重复发送资料卡。
3. 机器人把客户原消息转发到客服端。
4. 客服直接回复被转发的客户消息。
5. 机器人把客服回复复制发送给对应客户。

客服必须使用 Telegram 的“回复”功能回复客户原消息。客服端单独发送的新消息无法匹配到客户。

## 客服端按钮

客户资料卡下方有按钮：

- 查看历史
- 设置备注
- 查看备注
- 拉黑 / 解除拉黑

点击“设置备注”后，客服下一条文字消息会保存为内部备注，不会发送给客户。

## 管理员命令

```text
/whoami
/welcome
/setwelcome 您好，请问有什么可以帮您？
/buttons
/setbuttons 查看价格|购买流程|常见问题|联系人工
/note 客户ID 备注内容
/shownote 客户ID
/block 客户ID
/unblock 客户ID
/customer 客户ID
/history 客户ID
/help
```

大多数客户相关命令也可以通过回复客户消息使用。

## 数据存储

机器人默认使用 SQLite：

```text
data/bot.sqlite3
```

保存的数据包括设置、客户资料、消息映射、客户备注、黑名单和聊天记录。

默认不下载媒体文件，只保存消息类型和文字/说明信息，避免数据库过大。

## 多语言

管理端文案从 `locales/` 的 JSON 文件加载。内置语言：

- `zh-CN.json`
- `en.json`
- `es.json`
- `pt-BR.json`
- `fr.json`
- `ru.json`
- `ar.json`

添加新语言时，复制 `locales/en.json`，改名并翻译字段，然后在 `.env` 设置 `LANGUAGE`。

缺失的翻译字段会回退到英文，再回退到程序内置默认文案。

## 不要提交的文件

- `.env`
- `.venv/`
- `data/`
- `__pycache__/`
- `*.sqlite3`
- 日志或本地备份

这些已经写入 `.gitignore`。

## 安全建议

- 不要公开 Bot Token。
- 如果 Token 泄露，立刻在 `@BotFather` 重新生成。
- `.env` 只保存在服务器本地。
- webhook 模式请使用强随机 `WEBHOOK_SECRET_TOKEN`。

## 开源协议

发布前请选择开源协议，例如 MIT、Apache-2.0 或 AGPL-3.0。
