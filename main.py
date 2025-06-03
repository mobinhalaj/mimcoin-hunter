import requests
import time
import os
import threading
import http.server
import socketserver
from datetime import datetime

# باز کردن یک پورت فیک برای فریب Render
def keep_alive():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 10000), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=keep_alive).start()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = None
SENT_TOKENS = set()

def get_chat_id():
    global CHAT_ID
    try:
        updates = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates").json()
        if updates["result"]:
            CHAT_ID = updates["result"][-1]["message"]["chat"]["id"]
    except:
        pass

def send_message(text):
    if not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
    except:
        pass

def fetch_tokens():
    url = "https://public-api.birdeye.so/public/token/overview?sort=volume_24h&order=desc&offset=0&limit=30"
    headers = {"X-API-KEY": "demo"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return []
        return res.json().get("data", [])
    except:
        return []

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
                    f"🚀 <b>{name} ({symbol.upper()})</b>\n"
                    f"💧 Liquidity: ${liquidity:,.0f}\n"
                    f"👥 Holders: {holders}\n"
                    f"🕒 Created: {created}\n"
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
