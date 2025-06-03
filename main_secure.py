import requests
import time
import os
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = None
SENT_TOKENS = set()

def get_chat_id():
    global CHAT_ID
    updates = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates").json()
    if updates["result"]:
        CHAT_ID = updates["result"][-1]["message"]["chat"]["id"]

def send_message(text):
    if not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def fetch_tokens():
    url = "https://public-api.birdeye.so/public/token/overview?sort=volume_24h&order=desc&offset=0&limit=30"
    headers = {"X-API-KEY": "demo"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return []
    return res.json().get("data", [])

def analyze_and_send():
    tokens = fetch_tokens()
    for token in tokens:
        try:
            address = token["address"]
            if address in SENT_TOKENS:
                continue
            market_cap = float(token.get("market_cap", 0))
            liquidity = float(token.get("liquidity_usd", 0))
            holders = int(token.get("holders", 0))
            symbol = token.get("symbol", "").lower()
            name = token.get("name", "")
            if (
                market_cap < 500_000
                and liquidity > 3000
                and holders < 1000
                and any(kw in symbol for kw in ["doge", "pepe", "elon", "ai"])
            ):
                url = f"https://birdeye.so/token/{address}?chain=solana"
                created = datetime.fromtimestamp(token["created_at"]).strftime("%Y-%m-%d %H:%M")
                msg = (
                    f"🚀 <b>{name} ({symbol.upper()})</b>
"
                    f"💧 Liquidity: ${liquidity:,.0f}
"
                    f"👥 Holders: {holders}
"
                    f"🕒 Created: {created}
"
                    f"🔗 <a href='{url}'>View on Birdeye</a>"
                )
                send_message(msg)
                SENT_TOKENS.add(address)
        except:
            continue

if __name__ == "__main__":
    get_chat_id()
    while True:
        analyze_and_send()
        time.sleep(30)
