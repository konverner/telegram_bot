from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    user_id = Column(Integer)
    message_text = Column(String)


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    first_message_timestamp = Column(DateTime)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    phone_number = Column(String)


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    document_text = Column(String)
    document_name = Column(String)
    user_id = Column(Integer)
    upload_timestamp = Column(DateTime)
