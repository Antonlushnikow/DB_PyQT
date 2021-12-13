from sqlalchemy.orm import Session
from app.session import SessionLocal


def get_db() -> Session:
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()
