import os
import telebot
import logging
import logging.config
import json
from dotenv import load_dotenv, find_dotenv
from omegaconf import OmegaConf
import requests

from telegram_bot.service.app import App
from telegram_bot.db.database import log_message, add_user


config = OmegaConf.load("src/telegram_bot/conf/config.yaml")

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(OmegaConf.load("./src/telegram_bot/conf/logging_config.yaml"), resolve=True)

# Apply the logging configuration
logging.config.dictConfig(logging_config)

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file
TOKEN = os.getenv("BOT_TOKEN")

if TOKEN is None:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    exit(1)

cfg = OmegaConf.load("./src/telegram_bot/conf/config.yaml")
bot = telebot.TeleBot(TOKEN, parse_mode=None)
app = App("parameter")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f"Received message: {message.text} from chat {message.from_user.username} ({message.chat.id})")
    response = app.run(message.text)
    bot.reply_to(message, response)
    log_message(message.chat.id, message.text)
    add_user(
        message.chat.id, message.from_user.first_name,
        message.from_user.last_name, message.from_user.username,
        message.contact.phone_number if message.contact else None
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    logger.info(f"Received message: {message.text} from chat {message.from_user.username} ({message.chat.id})")
    bot.send_message(message.chat.id, "Запрос получен. Обработка ...")
    api_response = requests.post(config.endpoints.normalize, json={"user_input": message.text}, verify=False)
    api_response.raise_for_status()  # Raise an exception for HTTP errors
    response = api_response.json().get("response", "Error: Invalid response from the API")
    bot.send_message(
        message.chat.id,
        f"```json\n{str(json.dumps(response, indent=4, ensure_ascii=False))}\n```",
        parse_mode="markdown"
    )

    log_message(message.chat.id, message.text)
    add_user(
        message.chat.id, message.from_user.first_name,
        message.from_user.last_name, message.from_user.username,
        message.contact.phone_number if message.contact else None
    )

def start_bot():
    logger.info(f"bot `{str(bot.get_me().username)}` has started")
    bot.infinity_polling()
