#!/usr/bin/env python3
"""
Emergency schema fix for Neon database.
This will forcefully recreate the users table with the correct schema.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 70)
    print("EMERGENCY SCHEMA FIX FOR NEON DATABASE")
    print("=" * 70)

    print("\n[ISSUE] The 'users' table has the wrong schema")
    print("Database has: username, first_name, last_name")
    print("Code expects: name")

    print("\n[SOLUTION] We need to recreate the users table")
    print("\n[WARNING] This will DELETE all existing users and their data!")
    print("[WARNING] You will need to sign up again.")

    response = input("\nType 'YES' (uppercase) to continue: ")

    if response != 'YES':
        print("\n[CANCELLED] Schema fix cancelled")
        return

    print("\n[STEP 1] Importing models...")

    try:
        from sqlmodel import SQLModel, text
        from config.database import engine
        from src.models.todo_model import User, TodoTask

        print("[SUCCESS] Models imported")

    except Exception as e:
        print(f"[ERROR] Failed to import: {str(e)}")
        return

    print("\n[STEP 2] Dropping dependent tables...")

    # Drop tables in correct order (dependencies first)
    drop_statements = [
        "DROP TABLE IF EXISTS agent_messages CASCADE",
        "DROP TABLE IF EXISTS agent_sessions CASCADE",
        "DROP TABLE IF EXISTS tool_execution_logs CASCADE",
        "DROP TABLE IF EXISTS agent_tools CASCADE",
        "DROP TABLE IF EXISTS user_contexts CASCADE",
        "DROP TABLE IF EXISTS messages CASCADE",
        "DROP TABLE IF EXISTS conversations CASCADE",
        "DROP TABLE IF EXISTS todotasks CASCADE",  # Drop tasks table
        "DROP TABLE IF EXISTS todotask CASCADE",   # Alternative name
        "DROP TABLE IF EXISTS users CASCADE",      # Finally drop users
    ]

    try:
        with engine.connect() as conn:
            for stmt in drop_statements:
                try:
                    conn.execute(text(stmt))
                    conn.commit()
                    table_name = stmt.split()[4]
                    print(f"  Dropped: {table_name}")
                except Exception as e:
                    # Table might not exist, that's okay
                    pass

        print("[SUCCESS] Old tables dropped")

    except Exception as e:
        print(f"[ERROR] Failed to drop tables: {str(e)}")
        return

    print("\n[STEP 3] Creating tables with correct schema...")

    try:
        # Import all models to register them
        try:
            from models.agent_session import AgentSession
            from models.agent_message import AgentMessage
            from models.agent_tool import AgentTool
            from models.tool_execution_log import ToolExecutionLog
            from models.user_context import UserContext
            from models.conversation import Conversation
            from models.message import Message
            print("  [INFO] Agent models imported")
        except ImportError as e:
            print(f"  [WARNING] Some agent models not found: {e}")

        # Create all tables
        SQLModel.metadata.create_all(engine)
        print("[SUCCESS] Tables created with correct schema")

    except Exception as e:
        print(f"[ERROR] Failed to create tables: {str(e)}")
        return

    print("\n[STEP 4] Verifying schema...")

    try:
        from sqlmodel import Session, select

        with Session(engine) as session:
            # Try to query users table
            users = session.exec(select(User)).all()
            print(f"[SUCCESS] Users table accessible (found {len(users)} users)")

    except Exception as e:
        print(f"[ERROR] Failed to verify: {str(e)}")
        return

    print("\n" + "=" * 70)
    print("SCHEMA FIX COMPLETE!")
    print("=" * 70)
    print("\n[NEXT STEPS]")
    print("1. Restart your backend: python run_server.py")
    print("2. Clear browser cache: localStorage.clear()")
    print("3. Sign up with new account at http://localhost:3000/signup")
    print("4. Test auth, tasks, and chat - everything should work!")

if __name__ == "__main__":
    main()
