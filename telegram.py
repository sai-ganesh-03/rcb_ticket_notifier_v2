import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_chat_ids(bot_token):
    response = requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates")
    data = response.json()
    chat_ids = []
    if data["ok"] and data["result"]:
        for result in data["result"]:
            chat_id = result["message"]["chat"]["id"]
            if chat_id not in chat_ids:
                chat_ids.append(chat_id)
    return chat_ids

def send_telegram_messages(bot_token, chat_ids, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payloads = [{"chat_id": chat_id, "text": message} for chat_id in chat_ids]
    
    with requests.Session() as session:
        responses = [session.post(url, json=payload) for payload in payloads]
    
    return [response.json() for response in responses]

if __name__=="__main__":
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_ids=get_chat_ids(bot_token)
    print(chat_ids)