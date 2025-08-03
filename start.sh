#!/bin/bash

echo "🔥 start.sh triggered"

python << END
print("🐍 Rebo Inline Python Starting...")
import os
import requests

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
print("🧪 Token:", bot_token)

res = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
print("🔗 Response:", res.text)
END

echo "✅ Reached end of script"
