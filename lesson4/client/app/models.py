from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """
    Класс для таблицы пользователей
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    info = Column(String)

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
    user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"))
    contact_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"))
    __table_args__ = (UniqueConstraint('user_id', 'contact_id', name='uix_1'),
                      )

    def __init__(self, user_id, contact_id):
        self.user_id = user_id
        self.contact_id = contact_id


class MessageHistory(Base):
    """
    Класс для таблицы истории сообщений
    """
    __tablename__ = 'message_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"))
    contact_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"))
    message = Column(String)

    def __init__(self, user_id, contact_id, message):
        self.user_id = user_id
        self.contact_id = contact_id
        self.message = message
