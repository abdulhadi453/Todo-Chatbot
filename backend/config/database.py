from sqlmodel import create_engine, Session
from sqlalchemy import Engine
import os
from typing import Generator
from sqlmodel import SQLModel

# Get DATABASE_URL from environment or use SQLite as fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_backend.db")

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
    # Add the backend directory to the Python path
    current_dir = os.path.dirname(os.path.dirname(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Load .env file to ensure DATABASE_URL is set
    env_file = os.path.join(current_dir, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value

    # Import models and create tables with extend_existing to handle duplicates
    # Import User model FIRST (required for foreign key references)
    # Use the SAME User model that auth is using
    from src.models.todo_model import User
    from sqlmodel import SQLModel

    # Import agent models to ensure they're registered with SQLModel
    try:
        from models.agent_session import AgentSession
        from models.agent_message import AgentMessage
        from models.agent_tool import AgentTool
        from models.tool_execution_log import ToolExecutionLog
        from models.user_context import UserContext
    except ImportError as e:
        # Agent models may not exist yet in the old structure
        print(f"Warning: Could not import some agent models: {e}")
        pass

    # Import todo models from src/models
    try:
        from src.models.todo_model import TodoTask
    except ImportError as e:
        print(f"Warning: Could not import TodoTask: {e}")
        pass

    # FORCE DROP AND RECREATE to fix schema (one-time fix)
    # After this runs once, you can comment out the drop_all line
    # print("[SCHEMA FIX] Dropping and recreating all tables to fix schema...")
    # SQLModel.metadata.drop_all(engine)  # Drop existing tables to fix schema
    # SQLModel.metadata.create_all(engine)  # Create tables with correct schema
    # print("[SCHEMA FIX] Tables recreated successfully!")