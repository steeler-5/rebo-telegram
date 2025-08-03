#!/bin/bash

echo "🔥 start.sh triggered"

BOT_TOKEN=$TELEGRAM_BOT_TOKEN

echo "🧪 Loaded TELEGRAM_BOT_TOKEN: $BOT_TOKEN"

if [ -z "$BOT_TOKEN" ]; then
  echo "❌ TELEGRAM_BOT_TOKEN is not set!"
  exit 1
fi

echo "🔗 Telegram check:"
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe"

echo "✅ Shell script complete"
