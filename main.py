import requests
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging with a file path
LOG_FILE_PATH = "event_checker.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)
def send_telegram_messages(bot_token, chat_ids, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payloads = [{"chat_id": chat_id, "text": message} for chat_id in chat_ids]
    
    with requests.Session() as session:
        responses = [session.post(url, json=payload) for payload in payloads]
    
    return [response.json() for response in responses]

def fetch_event_data(bot_token, chat_ids):
    url = "https://rcbmpapi.ticketgenie.in/ticket/eventlist/O"
    headers = {
        "accept": "application/json, text/plain, */*",
        "origin": "https://shop.royalchallengers.com",
        "referer": "https://shop.royalchallengers.com/",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching event data: {e}"
        logging.error(error_message)
        send_telegram_messages(bot_token, chat_ids, error_message)
        return None

def main(bot_token, chat_ids):
    data = fetch_event_data(bot_token, chat_ids)
    if data is None:
        return
    
    if data.get("status") == "Success" and len(data.get("result", [])) == 4:
        send_telegram_messages(bot_token, chat_ids, "Ticket Found")
        logging.info(f"Notification sent to chat ID: {chat_ids}")
    else:
        logging.info("No tickets found.")

if __name__ == "__main__":
    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_ids = [617361892]
        if not bot_token:
            error_message = "TELEGRAM_BOT_TOKEN is not set in environment variables."
            logging.error(error_message)
            send_telegram_messages(bot_token, chat_ids, error_message)
        else:
            logging.info("Pinging RCB Website")
            main(bot_token, chat_ids)
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logging.critical(error_message, exc_info=True)
        send_telegram_messages(bot_token, chat_ids, error_message)
