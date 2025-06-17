from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine

from config import SETTINGS

# Create sqlite instance

# database_url = "postgresql://archaeon:admin@localhost:5432/vine"

database_url = f"{SETTINGS.database_type}://{SETTINGS.database_user}:{SETTINGS.database_password}@{SETTINGS.database_host}:{SETTINGS.database_port}/{SETTINGS.database_name}"

engine = create_engine(database_url, echo=True)

SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
