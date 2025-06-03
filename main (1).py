
import os
import time
import requests
import threading
import http.server
import socketserver

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
HEADERS = {"X-API-KEY": "demo"}
SENT_TOKENS = set()

def get_chat_id():
    try:
        updates = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates").json()
        if updates["result"]:
            return updates["result"][-1]["message"]["chat"]["id"]
    except:
        return None

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def keep_alive():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 10000), handler) as httpd:
        httpd.serve_forever()

def filter_and_send(chat_id):
    while True:
        try:
            res = requests.get(API_URL, headers=HEADERS).json()
            tokens = res.get("data", [])[:50]
            good_tokens = []

            for token in tokens:
                name = token.get("name", "")
                symbol = token.get("symbol", "")
                liquidity = token.get("liquidity", 0)
                market_cap = token.get("mc", 0)
                holders = token.get("holders", 0)
                address = token.get("address", "")

                if (
                    address not in SENT_TOKENS and
                    market_cap < 500000 and
                    liquidity > 3000 and
                    holders < 1000 and
                    any(x in name.lower() for x in ["doge", "pepe", "elon", "ai"])
                ):
                    SENT_TOKENS.add(address)
                    good_tokens.append(f"🚀 <b>{name} ({symbol.upper()})</b>\n💧 Liquidity: ${liquidity}\n💰 Market Cap: ${market_cap}\n👥 Holders: {holders}\n🔗 <a href='https://birdeye.so/token/{address}?chain=solana'>View on Birdeye</a>")

            if good_tokens:
                for msg in good_tokens:
                    send_message(chat_id, msg)

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=keep_alive).start()
    chat_id = get_chat_id()
    if chat_id:
        send_message(chat_id, "✅ ربات شکارچی فعال شد و در حال بررسی میم‌کوین‌هاست...")
        filter_and_send(chat_id)
    else:
        print("❌ chat_id پیدا نشد. لطفاً یک پیام به ربات بفرستید.")
