from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'llm_normalizer_messages'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    user_id = Column(Integer)
    message_text = Column(String)


class User(Base):
    __tablename__ = 'llm_normalizer_users'

    user_id = Column(Integer, primary_key=True)
    first_message_timestamp = Column(DateTime)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    phone_number = Column(String)
