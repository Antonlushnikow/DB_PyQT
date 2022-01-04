"""Создание генератора сессий"""


import os
from pathlib import Path

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import User, UserContact, UserHistory


BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

engine = create_engine('sqlite:///server.sqlite',
                       echo=True,
                       connect_args={'check_same_thread': False}
                       )

SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Создание таблиц"""
    if not os.path.exists('server.sqlite'):
        User.__table__.create(engine)
        UserContact.__table__.create(engine)
        UserHistory.__table__.create(engine)


if __name__ == '__main__':
    init_db()
