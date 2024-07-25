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
        self.prompt = lambda query, document: f"Твоя задача ответить на ВОПРОС опираясь на ДОКУМЕНТ. ВОПРОС: {query} ДОКУМЕНТ: {document}"

    def run(self, query: str, document_text: str):
        completion = self.client.Completion.create(
            model="accounts/fireworks/models/mixtral-8x22b-instruct",
            prompt=self.prompt(query, document_text[0]),
            max_tokens=200,
            temperature=0.0,
            presence_penalty=0,
            frequency_penalty=0,
            top_p=1,
            top_k=40
        )
        logger.info(self.prompt(query, document_text[0]))
        logger.info(completion)
        return completion.choices[0].text
