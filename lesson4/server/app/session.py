from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


engine = create_engine('sqlite:///..\\db.sqlite', echo=True)
# Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
