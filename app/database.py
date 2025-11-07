from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker, Session, declarative_base# type: ignore
from dotenv import load_dotenv  # type: ignore
import os

# Load .env file first
load_dotenv()

# Use SQLite for local development, fallback to AWS RDS if needed
# Check if .env file has a DATABASE_URL
env_database_url = os.getenv("DATABASE_URL")

if env_database_url:
    # Normalize psycopg2 URL to psycopg3 format (psycopg3 is compatible with postgresql://)
    DATABASE_URL = env_database_url.replace("postgresql+psycopg2://", "postgresql+psycopg://")
else:
    # Default to SQLite for local development
    DATABASE_URL = "sqlite:///./food_tracker.db"

# print(DATABASE_URL)

engine = create_engine(DATABASE_URL) # type: ignore

# Database connection established (credentials hidden for security)
Sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()