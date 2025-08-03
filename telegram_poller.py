import os
import requests
from time import sleep

try:
    print("🐍 Rebo Telegram Poller Starting...")

    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    print("🧪 Loaded TELEGRAM_BOT_TOKEN:", BOT_TOKEN)

    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set!")

    # Check Telegram connection
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
    print("🔗 Telegram check:", response.text)

    # Start polling loop
    offset = None
    print("🚀 Polling started...")
    while True:
        res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", params={"offset": offset, "timeout": 10})
        updates = res.json()

        if updates.get("ok") and updates.get("result"):
            for update in updates["result"]:
                offset = update["update_id"] + 1
                chat_id = update["message"]["chat"]["id"]
                message_text = update["message"]["text"]

                print(f"📩 Message from {chat_id}: {message_text}")

                reply_text = f"🧠 Rebo here! You said: {message_text}"
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": chat_id, "text": reply_text},
                )
        sleep(1)

except Exception as e:
    print("❌ ERROR in telegram_poller.py:", e)
