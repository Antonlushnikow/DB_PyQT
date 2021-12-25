from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """
    Класс для таблицы пользователей
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    info = Column(String, nullable=True)

    def __init__(self, login, info=''):
        self.login = login
        self.info = info

    def __repr__(self):
        return f'client {self.name} ({self.ipaddr})'


class UserContact(Base):
    """
    Класс для таблицы контактов пользователей
    """
    __tablename__ = 'user_contact'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    contact = Column(String)
    __table_args__ = (UniqueConstraint('user', 'contact', name='uix_1'),
                      )


class MessageHistory(Base):
    """
    Класс для таблицы истории сообщений
    """
    __tablename__ = 'message_history'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    contact = Column(String)
    message = Column(String)
    time = Column(DateTime, default=datetime.now())

    def __init__(self, user, contact, message):
        self.user = user
        self.contact = contact
        self.message = message
