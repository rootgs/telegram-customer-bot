# systemd Deployment

This example keeps the bot running on a Linux server and restarts it after failures or reboot.

## Install

Run the installer first:

```bash
chmod +x install.sh
./install.sh
```

Assume the project path is:

```text
/opt/telegram-customer-bot
```

Create a service file:

```bash
sudo nano /etc/systemd/system/telegram-customer-bot.service
```

Example service:

```ini
[Unit]
Description=Telegram Customer Support Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/telegram-customer-bot
ExecStart=/opt/telegram-customer-bot/.venv/bin/python /opt/telegram-customer-bot/bot.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-customer-bot
sudo systemctl start telegram-customer-bot
```

Check status:

```bash
sudo systemctl status telegram-customer-bot
```

View logs:

```bash
journalctl -u telegram-customer-bot -f
```
