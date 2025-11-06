#!/usr/bin/env python3
"""
Create database tables for the AI Food Tracker
"""

from app.database import engine, Base
from app.models import models

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully!")
    print("Database file: food_tracker.db")

if __name__ == "__main__":
    create_tables()
