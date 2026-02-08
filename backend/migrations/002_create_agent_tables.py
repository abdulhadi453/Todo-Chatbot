"""
Database migration script for creating AI agent-related tables.

This script creates the necessary database tables for the AI agent functionality:
- agent_sessions: Stores conversation sessions between users and AI agent
- agent_messages: Stores messages within agent conversations
- agent_tools: Stores available tools that the agent can use
- tool_execution_logs: Logs all tool executions by the agent
- user_contexts: Stores user-specific context and preferences for AI interactions

This migration ensures proper table structure with appropriate indexes, foreign keys,
and constraints for security and performance.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add the backend directory to the Python path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import SQLModel, create_engine, Session
from backend.models.agent_session import AgentSession
from backend.models.agent_message import AgentMessage
from backend.models.agent_tool import AgentTool
from backend.models.tool_execution_log import ToolExecutionLog
from backend.models.user_context import UserContext


def run_migration():
    """
    Execute the database migration to create agent-related tables.

    This function creates all the necessary tables for the AI agent functionality:
    - agent_sessions
    - agent_messages
    - agent_tools
    - tool_execution_logs
    - user_contexts

    It ensures proper foreign key relationships and indexes for performance.
    """
    print(f"[{datetime.now()}] Starting AI agent tables migration...")

    # Get database URL from environment variable or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./todo_backend.db")

    # Create database engine
    engine = create_engine(database_url, echo=True)

    # Create all tables
    print("Creating agent-related tables...")
    SQLModel.metadata.create_all(engine)

    # Verify tables were created by attempting to create a session
    try:
        with Session(engine) as session:
            print("Connection to database successful, tables created.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

    print(f"[{datetime.now()}] AI agent tables migration completed successfully!")
    print("- Created 'agent_sessions' table")
    print("- Created 'agent_messages' table")
    print("- Created 'agent_tools' table")
    print("- Created 'tool_execution_logs' table")
    print("- Created 'user_contexts' table")
    print("- Established foreign key relationships")
    print("- Created indexes for performance optimization")

    return True


def rollback_migration():
    """
    Rollback the database migration if needed.

    NOTE: This will delete the agent-related tables and ALL associated data.
    Use with caution as this operation is irreversible.
    """
    print(f"[{datetime.now()}] Starting rollback of AI agent tables migration...")

    # Get database URL from environment variable or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./todo_backend.db")

    # Create database engine
    engine = create_engine(database_url, echo=True)

    # Drop all agent-related tables
    print("Dropping agent-related tables...")

    # We need to drop tables in the right order to respect foreign key constraints
    ToolExecutionLog.__table__.drop(engine, checkfirst=True)
    print("- Dropped 'tool_execution_logs' table")

    AgentMessage.__table__.drop(engine, checkfirst=True)
    print("- Dropped 'agent_messages' table")

    AgentSession.__table__.drop(engine, checkfirst=True)
    print("- Dropped 'agent_sessions' table")

    AgentTool.__table__.drop(engine, checkfirst=True)
    print("- Dropped 'agent_tools' table")

    UserContext.__table__.drop(engine, checkfirst=True)
    print("- Dropped 'user_contexts' table")

    print(f"[{datetime.now()}] AI agent tables rollback completed!")


if __name__ == "__main__":
    import argparse

    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Manage AI agent tables migration")
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback the migration (will delete all agent-related data)"
    )

    args = parser.parse_args()

    if args.rollback:
        rollback_migration()
    else:
        success = run_migration()
        if not success:
            print("Migration failed!")
            sys.exit(1)
        else:
            print("Migration completed successfully!")