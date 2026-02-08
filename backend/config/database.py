from sqlmodel import create_engine, Session
from sqlalchemy import Engine
import os
from typing import Generator
from sqlmodel import SQLModel

# Force SQLite for local development to avoid connection issues
DATABASE_URL = "sqlite:///./todo_backend.db"

# Create the engine with connection pooling settings
pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Configure engine appropriately for SQLite vs PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration to avoid connection issues
    engine: Engine = create_engine(
        DATABASE_URL,
        echo=(os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG"),
        connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
    )
else:
    # PostgreSQL configuration
    engine: Engine = create_engine(
        DATABASE_URL,
        echo=(os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG"),
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle
    )


def get_session() -> Generator[Session, None, None]:
    """Get a database session"""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Create database tables"""
    import sys
    import os
    # Add the src directory to the Python path
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    src_dir = os.path.join(parent_dir, 'src')

    # Check if src_dir is already in the path to avoid duplicates
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    # Import models and create tables with extend_existing to handle duplicates
    from models.todo_model import TodoTask, User
    from sqlmodel import SQLModel

    # Import agent models to ensure they're registered with SQLModel
    try:
        from models.agent_session import AgentSession
        from models.agent_message import AgentMessage
        from models.agent_tool import AgentTool
        from models.tool_execution_log import ToolExecutionLog
        from models.user_context import UserContext
    except ImportError:
        # Agent models may not exist yet in the old structure
        pass

    # Create all tables, potentially dropping and recreating if needed
    # For development purposes, we'll drop and recreate to ensure schema matches models
    SQLModel.metadata.drop_all(engine)  # Drop existing tables
    SQLModel.metadata.create_all(engine)  # Create tables with new schema