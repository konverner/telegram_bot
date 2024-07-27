""" Application that provides functionality for the Telegram bot. """
import os
import logging.config

from dotenv import load_dotenv, find_dotenv
from omegaconf import OmegaConf

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(OmegaConf.load("./src/telegram_bot/conf/logging_config.yaml"), resolve=True)

# Apply the logging configuration
logging.config.dictConfig(logging_config)

# Configure logging
logger = logging.getLogger(__name__)

class FireworksLLM:
    def __init__(self):
        import fireworks.client
        API_KEY = os.getenv("API_KEY")
        self.client = fireworks.client
        fireworks.client.api_key = API_KEY
        self.prompt = lambda query, document_name, document_text: f"Твоя задача ответить на ВОПРОС опираясь на ДОКУМЕНТ. Процитируй название документа. ВОПРОС: {query} Название ДОКУМЕНТА: {document_name} Содержание ДОКУМЕНТа: {document_text}"

    def run(self, query: str, document_text: str, document_name: str):
        completion = self.client.ChatCompletion.create(
            model="accounts/fireworks/models/llama-v3-70b-instruct",
            messages=[
                {
                    "role": "user",
                    "content": self.prompt(query, document_name[0], document_text[0])
                }
            ],
            max_tokens=200,
            temperature=0.6,
            presence_penalty=0,
            frequency_penalty=0,
            top_p=1,
            top_k=40
        )
        return completion.choices[0].message.content
