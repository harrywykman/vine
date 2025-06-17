from functools import lru_cache

from config import Settings
from database import SessionLocal


@lru_cache
def get_settings():
    return Settings()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
