from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
import os

# Database URL should be in environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+mysqlconnector://root:root@mysql:3306/forensic_ai"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Only useful for initial setup, usually migration is better
    Base.metadata.create_all(bind=engine)
