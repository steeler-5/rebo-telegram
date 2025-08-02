import os
import time
import requests
from agent_core import chat_with_bot

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset=None):
    params = {"timeout": 60}
    if offset:
        params["offset"] = offset
    response = requests.get(f"{API_URL}/getUpdates", params=params)
    return response.json()["result"]

def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text}
    requests.post(f"{API_URL}/sendMessage", data=payload)

def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    print(f"📩 Message from {chat_id}: {text}")
    reply = chat_with_bot(text)
    print(f"🤖 Rebo says: {reply}")
    send_message(chat_id, reply)

def poll():
    print("🚀 Polling started...")
    last_update_id = None
    while True:
        try:
            updates = get_updates(offset=last_update_id)
            for update in updates:
                last_update_id = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])
        except Exception as e:
            print("🔥 Polling error:", e)
        time.sleep(2)

if __name__ == "__main__":
    poll()
