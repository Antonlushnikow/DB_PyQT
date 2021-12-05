from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    info = Column(String)

    def __init__(self, login, info=''):
        self.login = login
        self.info = info

    def __repr__(self):
        return f'client {self.name} ({self.ipaddr})'


class UserHistory(Base):
    __tablename__ = 'user_history'
    id = Column(Integer, primary_key=True)
    user_id = (Integer, ForeignKey('user.id', ondelete="CASCADE"))
    logon_time = Column(Date)

    def __init__(self, user_id, logon_time=datetime.now()):
        self.user_id = user_id
        self.logon_time = logon_time


class UserContact(Base):
    __tablename__ = 'user_contact'
    id = Column(Integer, primary_key=True)
    user_id = (Integer, ForeignKey('user.id', ondelete="CASCADE"))
    contact_id = (Integer, ForeignKey('user.id', ondelete="CASCADE"))

    def __init__(self, user_id, contact_id):
        self.user_id = user_id
        self.contact_id = contact_id





