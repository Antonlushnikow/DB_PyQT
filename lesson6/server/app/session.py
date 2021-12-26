from pathlib import Path

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


base_dir = str(Path(__file__).parent.parent.resolve())

engine = create_engine(f'sqlite:///{base_dir}\\db.sqlite', echo=True, connect_args={'check_same_thread': False})
# Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
