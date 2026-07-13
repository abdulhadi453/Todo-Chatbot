#!/usr/bin/env python3
"""
Database schema fix tool.
This will recreate all tables with the correct schema to fix foreign key issues.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import SQLModel, Session, select
from config.database import engine

def check_current_schema():
    """Check what tables and users exist."""
    print("\n[INFO] Checking current database schema...")

    try:
        # Try to query users
        from src.models.todo_model import User
        with Session(engine) as session:
            users = session.exec(select(User)).all()
            print(f"[INFO] Found {len(users)} users in database:")
            for user in users:
                print(f"  - {user.email} (ID: {user.id})")
            return len(users)
    except Exception as e:
        print(f"[ERROR] Could not query users: {str(e)}")
        return 0

def recreate_schema():
    """Recreate all database tables with correct schema."""
    print("\n[WARNING] This will DROP all existing tables and data!")
    print("[WARNING] Make sure you've backed up any important data.")

    response = input("\nContinue? (yes/no): ")

    if response.lower() != 'yes':
        print("[CANCELLED] Schema recreation cancelled")
        return False

    print("\n[INFO] Recreating database schema...")

    try:
        # Import ALL models to ensure they're registered
        from src.models.todo_model import User, TodoTask
        from models.agent_session import AgentSession
        from models.agent_message import AgentMessage
        from models.agent_tool import AgentTool
        from models.tool_execution_log import ToolExecutionLog
        from models.user_context import UserContext

        # Drop all tables
        print("[STEP 1] Dropping all existing tables...")
        SQLModel.metadata.drop_all(engine)
        print("[SUCCESS] All tables dropped")

        # Create all tables with correct schema
        print("[STEP 2] Creating tables with correct schema...")
        SQLModel.metadata.create_all(engine)
        print("[SUCCESS] All tables created")

        print("\n[DONE] Database schema recreated successfully!")
        print("\n[NEXT STEPS]")
        print("1. Sign up with a new account at http://localhost:3000/signup")
        print("2. Your old data has been cleared, but the schema is now consistent")
        print("3. All features (auth, tasks, chat) should now work correctly")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to recreate schema: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("DATABASE SCHEMA FIX TOOL")
    print("=" * 70)
    print("\nThis tool fixes the foreign key constraint violation by ensuring")
    print("all tables use the same User model.\n")

    # Check current state
    user_count = check_current_schema()

    if user_count > 0:
        print(f"\n[INFO] You have {user_count} user(s) in the database.")
        print("[INFO] This data will be lost when we recreate the schema.")

    # Recreate schema
    success = recreate_schema()

    if success:
        print("\n" + "=" * 70)
        print("SCHEMA FIX COMPLETE")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("SCHEMA FIX FAILED OR CANCELLED")
        print("=" * 70)

if __name__ == "__main__":
    main()
