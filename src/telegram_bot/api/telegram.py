import os
import telebot
import logging.config
from dotenv import load_dotenv, find_dotenv
from omegaconf import OmegaConf

from telegram_bot.service.llm import FireworksLLM
from telegram_bot.service.vector_store import VectorStore
from telegram_bot.db.database import log_message, add_user


load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file

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

idx = 1
cfg = OmegaConf.load("./src/telegram_bot/conf/config.yaml")
bot = telebot.TeleBot(TOKEN, parse_mode=None)
llm = FireworksLLM()
vector_store = VectorStore()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Загрузите документы")

## Function to load documents into ChromaDB
@bot.message_handler(content_types=['document'])
def load_document(message):
    global idx
    document = message.document
    logger.info(f"Received document: {document.file_name} with type {document.mime_type} from chat {message.from_user.username} ({message.chat.id})")
    if document.mime_type == 'text/plain':
        file_info = bot.get_file(document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        document_text = downloaded_file.decode('utf-8')

        vector_store.upsert_document(document_text=document_text, idx=idx)

        logger.info(f"Document {document.file_name} has been upserted to ChromaDB with idx {idx}")
        idx += 1
        bot.send_message(message.chat.id, "Документ загружен.")
    else:
        logger.error(f"Document {document.file_name} has NOT been upserted to ChromaDB with idx {idx}")
        bot.send_message(message.chat.id, "Пожалуйста, загрузите текстовый файл (txt).")

# Function to ask question about documents
@bot.message_handler(func=lambda message: True, content_types=['text'])
def ask_question(message):
    question = message.text
    logger.info(f"Received message: '{message.text}' from chat {message.from_user.username} ({message.chat.id})")
    retriever_results = vector_store.query(question, 1)
    document_text = retriever_results["documents"][0]
    response = llm.run(question, document_text)
    bot.send_message(message.chat.id, response)

    log_message(message.chat.id, message.text)
    add_user(
        message.chat.id, message.from_user.first_name,
        message.from_user.last_name, message.from_user.username,
        message.contact.phone_number if message.contact else None
    )

def start_bot():
    logger.info(f"bot `{str(bot.get_me().username)}` has started")
    bot.polling()
