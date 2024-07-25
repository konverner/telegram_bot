import os
import telebot
import logging
import logging.config
from dotenv import load_dotenv, find_dotenv
from omegaconf import OmegaConf

from telegram_bot.service.app import App
from telegram_bot.db.database import log_message, add_user

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
def start(message):
    bot.send_message(message.chat.id, "Загрузите документы")

## Function to load documents into ChromaDB
@bot.message_handler(content_types=['document'])
def load_document(message):
    global idx
    document = message.document
    if document.mime_type == 'text/plain':
        file_info = bot.get_file(document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        document_text = downloaded_file.decode('utf-8')

        embedding = embedding_func.model.encode(document_text)
        # upsert to chromadb
        collection.upsert(
            ids=[str(idx)],
            documents=document_text,
            embeddings=embedding.tolist(),
        )
        idx += 1
        bot.send_message(message.chat.id, "Документ загружен.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, загрузите текстовый файл (txt).")

# Function to ask question about documents
@bot.message_handler(func=lambda message: True, content_types=['text'])
def ask_question(message):
    question = message.text
    retriever_results = collection.query(query_texts=question, n_results=2)
    document_text = retriever_results["documents"][0]
    response = llm.run(question, document_text)
    bot.send_message(message.chat.id, response)

def start_bot():
    logger.info(f"bot `{str(bot.get_me().username)}` has started")
    bot.infinity_polling()
