"""Создание генератора сессий"""


from pathlib import Path

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


BASE_DIR = str(Path(__file__).parent.parent.resolve())

engine = create_engine(f'sqlite:///{BASE_DIR}\\db.sqlite',
                       echo=True,
                       connect_args={'check_same_thread': False}
                       )

SessionLocal = sessionmaker(bind=engine)
