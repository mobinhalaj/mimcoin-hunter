import requests
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def get_chat_id():
    try:
        updates = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates").json()
        if updates["result"]:
            return updates["result"][-1]["message"]["chat"]["id"]
    except:
        return None

def send_test_message(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": "✅ تست موفق بود. ربات شکارچی آماده است!",
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

if __name__ == "__main__":
    chat_id = get_chat_id()
    if chat_id:
        send_test_message(chat_id)
    else:
        print("❌ chat_id پیدا نشد. لطفاً یک پیام به ربات بفرستید.")
