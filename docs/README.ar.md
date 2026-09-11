# بوت دعم العملاء لتليجرام

[English README](../README.md)

بوت خفيف لتليجرام لاستقبال العملاء عبر الرسائل الخاصة. يرسل العميل رسالة إلى البوت، فيقوم البوت بتحويلها إلى محادثة الدعم، ثم يرد فريق الدعم على الرسالة المحولة ليقوم البوت بإرسال الرد إلى العميل الصحيح.

## الميزات

- استقبال العملاء عبر الرسائل الخاصة
- تحويل الرسائل إلى مستخدم أو مجموعة دعم
- الرد على العميل عبر خاصية الرد في تليجرام
- بطاقة معلومات العميل في محادثة الدعم
- أزرار إدارية: السجل، تعيين ملاحظة، عرض الملاحظة، حظر وإلغاء الحظر
- لا تتكرر بطاقة العميل إذا أرسل العميل نفسه عدة رسائل متتالية
- تخزين SQLite
- حفظ سجل المحادثات للتحليل لاحقًا
- رسالة ترحيب قابلة للتخصيص
- أزرار ترحيب للعميل
- وضع polling ووضع webhook
- مثبت تفاعلي لنظام Linux
- دعم لغات الإدارة عبر `locales/*.json`

## التثبيت السريع على Linux

```bash
chmod +x install.sh
./install.sh
```

بعد التثبيت:

```bash
.venv/bin/python bot.py
```

## الإعداد

```env
BOT_TOKEN=123456789:replace_with_your_bot_token
SUPPORT_CHAT_ID=-1001234567890
DB_FILE=data/bot.sqlite3
LANGUAGE=ar
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

يتحقق المثبت من أن نطاق HTTPS قابل للحل عبر DNS. عند استخدام edge node أو نفق أو reverse proxy، قم بالتحويل إلى:

```text
http://127.0.0.1:7024/telegram-webhook
```

## الأوامر

```text
/whoami
/welcome
/setwelcome مرحبًا، كيف يمكننا مساعدتك؟
/buttons
/setbuttons الأسعار|طريقة الشراء|الأسئلة الشائعة|دعم بشري
/note CUSTOMER_ID text
/shownote CUSTOMER_ID
/block CUSTOMER_ID
/unblock CUSTOMER_ID
/customer CUSTOMER_ID
/history CUSTOMER_ID
/help
```

## اللغات

يتم تحميل النصوص من `locales/`. لإضافة لغة جديدة، انسخ `locales/en.json`، ترجم القيم، ثم عيّن `LANGUAGE` في `.env`.

## الأمان

لا تنشر `.env` أو الرموز أو قاعدة البيانات أو سجل المحادثات أو النسخ الاحتياطية المحلية. هذه الملفات مضافة إلى `.gitignore`.
