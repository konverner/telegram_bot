import datetime
import logging.config
import os

from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Message, User, Document

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(OmegaConf.load("./src/telegram_bot/conf/logging_config.yaml"), resolve=True)

# Apply the logging configuration
logging.config.dictConfig(logging_config)

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(usecwd=True))

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
	logger.error("DATABASE_URL is not set in the environment variables.")
	exit(1)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def create_tables():
	Base.metadata.create_all(engine)


def log_message(user_id, message_text):
	session = Session()
	new_message = Message(
		timestamp=datetime.datetime.now(),
		user_id=user_id,
		message_text=message_text
	)
	session.add(new_message)
	session.commit()


def add_user(user_id, first_name, last_name, username, phone_number):
	session = Session()
	new_user = User(
		user_id=user_id,
		first_message_timestamp=datetime.datetime.now(),
		first_name=first_name,
		last_name=last_name,
		username=username,
		phone_number=phone_number
	)
	# add only if the user is not already in the database
	if not session.query(User).filter(User.user_id == user_id).first():
		session.add(new_user)
	session.commit()


def add_document(user_id, document_text, document_name):
	session = Session()
	new_document = Document(
		document_text=document_text,
		document_name=document_name,
		user_id=user_id,
		upload_timestamp=datetime.datetime.now()
	)
	session.add(new_document)
	session.commit()

