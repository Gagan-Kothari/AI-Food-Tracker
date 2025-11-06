from sqlalchemy import create_engine # type: ignore
# from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker, Session, declarative_base# type: ignore
from dotenv import load_dotenv  # type: ignore
import os

# Load .env file first
load_dotenv()

# Use SQLite for local development, fallback to AWS RDS if needed
# Check if .env file has a DATABASE_URL
env_database_url = os.getenv("DATABASE_URL")

if env_database_url:
    DATABASE_URL = env_database_url
else:
    # Default to SQLite for local development
    DATABASE_URL = "sqlite:///./food_tracker.db"

# print(DATABASE_URL)

engine = create_engine(DATABASE_URL) # type: ignore
Sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()