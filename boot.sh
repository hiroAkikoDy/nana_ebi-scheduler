#!/bin/sh

# boot.sh
# GOROman/nullevi03のboot.shを参考にして、ナナエビちゃん用に調整した起動スクリプト。
# 本ファイルはPOSIX sh (#!/bin/sh) 準拠です。
# 参考：https://github.com/GOROman/nullevi03/blob/main/boot.sh

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-00000000:xxxxxxxxxxxxxxxxxxxxxxxxxxxx}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-xxxxxxxxxxx}"

notify_telegram() {
  text="$1"
  if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      --data-urlencode "text=${text}" \
      > /dev/null 2>&1 || true
  fi
}

FIRST=1
while true; do
  if [ "$FIRST" = "1" ]; then
    notify_telegram "🦐 boot.sh起動: ナナエビちゃんを起動します🌅"
    FIRST=0
  else
    notify_telegram "🦐 ナナエビちゃんが終了 → 5秒後に再起動します🔄"
    sleep 5
    notify_telegram "🦐 ナナエビちゃんを再起動します🌅"
  fi
  claude --dangerously-skip-permissions --channels plugin:telegram@claude-plugins-official -c
  echo "ナナエビちゃんが終了しました。5秒後に再起動します..."
done