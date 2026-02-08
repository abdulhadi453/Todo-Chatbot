"""
Database migration script for creating chat-related tables:
- conversations table
- messages table

This migration creates the necessary database tables for the AI chatbot feature.
"""

import os
import sys
from datetime import datetime
import uuid

# Add the backend directory to the Python path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlmodel import SQLModel, create_engine, Session
from backend.models.conversation import Conversation
from backend.models.message import Message

def run_migration():
    """
    Execute the database migration to create chat tables.
    """
    print(f"[{datetime.now()}] Starting chat tables migration...")

    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./todo_backend.db")

    # Create engine
    engine = create_engine(database_url, echo=True)

    # Create tables
    print("Creating conversations and messages tables...")
    SQLModel.metadata.create_all(engine)

    print(f"[{datetime.now()}] Chat tables migration completed successfully!")
    print("- Created 'conversations' table")
    print("- Created 'messages' table")
    print("- Created foreign key relationships")
    print("- Created indexes for user_id and conversation_id")

def rollback_migration():
    """
    Rollback the database migration if needed.
    Note: This will delete the chat tables and all associated data!
    """
    print(f"[{datetime.now()}] Starting rollback of chat tables migration...")

    database_url = os.getenv("DATABASE_URL", "sqlite:///./todo_backend.db")
    engine = create_engine(database_url, echo=True)

    # Drop tables
    print("Dropping conversations and messages tables...")
    Message.__table__.drop(engine, checkfirst=True)
    Conversation.__table__.drop(engine, checkfirst=True)

    print(f"[{datetime.now()}] Chat tables rollback completed!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage chat tables migration")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")

    args = parser.parse_args()

    if args.rollback:
        rollback_migration()
    else:
        run_migration()