from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.food_entry import Base
import os

# Ensure the database directory exists and has correct permissions
DB_PATH = "food_consumption.db"
if not os.path.exists(DB_PATH):
    # Create an empty file with write permissions
    open(DB_PATH, 'a').close()
    os.chmod(DB_PATH, 0o666)

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create all tables
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()