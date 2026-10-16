#!/usr/bin/env python3
"""CleanerBot — paid Telegram bot for the Excel/CSV cleaner.

Flow: user sends CSV/XLSX → bot cleans → returns .xlsx in seconds.
First 3 files FREE, then crypto credits: user pays, sends /paid TXID,
admin (Baran) approves with /approve → credits added.

Runs on YOUR machine (long polling, no hosting). Secrets ONLY from
environment (.env file, never committed):
    CLEANER_TG_TOKEN=...   (a NEW bot from @BotFather, not the IP-logger one)
    ADMIN_ID=...           (your numeric Telegram user id)

Run:  python3 bot.py
"""
import json
import os
import time

import requests

import clean
import quota

HERE = os.path.dirname(os.path.abspath(__file__))


def _load_dotenv():
    p = os.path.join(HERE, ".env")
    if not os.path.exists(p):
        return
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()
TOKEN = os.environ.get("CLEANER_TG_TOKEN", "")
ADMIN_ID = os.environ.get("ADMIN_ID", "")
BASE = "https://api.telegram.org/bot" + TOKEN
USERS = os.path.join(HERE, "users.json")
WORK = os.path.join(HERE, "work")
MAX_MB = 10
CREDITS_PER_APPROVAL = 10

PAY_TEXT = (
    "💰 انتهت ملفاتك المجانية (3).\n"
    "للاستمرار: حوّل 5$ USDT إلى:\n"
    "`TLWdTjqqogkXNEXGiPWsGdjFP6ioycxeWW`\n"
    "(شبكة TRC20)\n"
    "ثم أرسل: /paid رقم_العملية\n"
    "مثال: /paid a1b2c3...\n\n"
    "🔒 تفضل الخصوصية؟ ادفع BTC:\n"
    "`bc1q8dhtdrndxsl70e97t8grydfe6pjue37zrhzf6c`\n"
    "تحصل على 10 ملفات لكل 5$."
)
START_TEXT = (
    "🧹 أهلاً بك في بوت تنظيف الملفات!\n\n"
    "أرسل ملف CSV أو Excel وسأعيده نظيفاً مع تقرير خلال ثوانٍ.\n"
    "🎁 أول 3 ملفات مجاناً — بعدها 10 ملفات لكل 5$ USDT."
)


def api(method, **kw):
    r = requests.post(BASE + "/" + method, json=kw, timeout=40)
    return r.json()


def send_text(chat, text):
    return api("sendMessage", chat_id=chat, text=text, parse_mode="Markdown")


def send_file(chat, path, caption=""):
    with open(path, "rb") as f:
        r = requests.post(BASE + "/sendDocument",
                          data={"chat_id": chat, "caption": caption[:900]},
                          files={"document": f}, timeout=60)
    return r.json()


def handle_update(u):
    msg = u.get("message") or {}
    chat = (msg.get("chat") or {}).get("id")
    if not chat:
        return
    text = (msg.get("text") or "").strip()

    if text.startswith("/start"):
        send_text(chat, START_TEXT)
        return

    if text.startswith("/paid"):
        txid = text[5:].strip() or "—"
        user = msg.get("from") or {}
        if ADMIN_ID:
            api("sendMessage", chat_id=int(ADMIN_ID),
                text="💸 طلب تفعيل جديد\nuser=%s (@%s)\ntxid=%s" % (
                    user.get("id"), user.get("username"), txid))
        send_text(chat, "✅ استلمنا طلبك، تتم المراجعة ويُفعّل رصيدك قريباً.")
        return

    if text.startswith("/approve") and str(chat) == str(ADMIN_ID):
        parts = text.split()
        if len(parts) >= 2:
            n = int(parts[2]) if len(parts) >= 3 else CREDITS_PER_APPROVAL
            left = quota.add_credits(USERS, parts[1], n)
            send_text(int(parts[1]),
                      "✅ تم تفعيل رصيدك: %d ملفات. أرسل ملفك!" % left)
            send_text(chat, "done.")
        return

    doc = msg.get("document")
    if not doc:
        send_text(chat, "📎 أرسل ملف CSV أو Excel لأبدأ. /start للتعليمات.")
        return

    name = doc.get("file_name", "file")
    ext = os.path.splitext(name)[1].lower()
    if ext not in (".csv", ".xlsx", ".xls"):
        send_text(chat, "⚠️ أقبل فقط CSV و Excel.")
        return
    if (doc.get("file_size") or 0) > MAX_MB * 1024 * 1024:
        send_text(chat, "⚠️ الحد %dMB لكل ملف." % MAX_MB)
        return

    ok, free_left, credits = quota.check_allow(USERS, chat)
    if not ok:
        send_text(chat, PAY_TEXT)
        return

    os.makedirs(WORK, exist_ok=True)
    meta = api("getFile", file_id=doc["file_id"])
    fpath = (meta.get("result") or {}).get("file_path", "")
    dl = requests.get("https://api.telegram.org/file/bot%s/%s" % (TOKEN, fpath),
                      timeout=60)
    src = os.path.join(WORK, "%s_%s" % (chat, name))
    with open(src, "wb") as f:
        f.write(dl.content)

    out = clean.process(src, WORK)
    if not out:
        send_text(chat, "❌ تعذر تنظيف الملف. تأكد أنه CSV/Excel سليم.")
        return
    quota.consume(USERS, chat)
    note = ("متبقٍ %d مجانية" % free_left) if credits == 0 else ("رصيدك: %d" % (credits - 1))
    send_file(chat, out, "✅ تم التنظيف! (%s)" % note)


def main():
    if not TOKEN:
        print("Set CLEANER_TG_TOKEN env var (see .env.example).")
        raise SystemExit(1)
    me = api("getMe")
    print("bot: @%s — polling..." % (me.get("result") or {}).get("username"))
    offset = 0
    while True:
        try:
            r = requests.post(BASE + "/getUpdates",
                              json={"offset": offset, "timeout": 30},
                              timeout=40).json()
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                try:
                    handle_update(u)
                except Exception as ex:
                    print("update error:", ex)
        except KeyboardInterrupt:
            print("\nstopped.")
            return
        except Exception as ex:
            print("poll error:", type(ex).__name__, "— retry in 5s")
            time.sleep(5)


if __name__ == "__main__":
    main()
