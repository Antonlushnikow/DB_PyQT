from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    Класс для таблицы пользователей
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    info = Column(String, nullable=True)
    password_hash = Column(String)
    history = relationship('UserHistory', cascade='all, delete-orphan')

    contacts = relationship('UserContact', foreign_keys='UserContact.user_id')

    def __init__(self, login, password_hash, info=''):
        self.login = login
        self.info = info
        self.password_hash = password_hash

    def __repr__(self):
        return f'client {self.name} ({self.ipaddr})'

    def to_json(self):
        return {'id': self.id}


class UserHistory(Base):
    """
    Класс для таблицы истории входа пользователей
    """
    __tablename__ = 'user_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"))
    ip_addr = Column(String)
    logon_time = Column(DateTime, default=datetime.now())

    def __init__(self, user_id, ip_addr='', logon_time=datetime.now()):
        self.user_id = user_id
        self.ip_addr = ip_addr
        self.logon_time = logon_time


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
