#!/usr/bin/env python3
"""
Todo Backend API Startup Script

This script starts the FastAPI server with proper configuration
for the Todo Backend API & Database application.
"""

import os
import subprocess
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from config.database import create_db_and_tables

def load_env_vars():
    """Load environment variables from .env file"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value
        print("Environment variables loaded from .env file")


def main():
    """Main function to start the server"""
    print("Starting Todo Backend API...")

    # Load environment variables
    load_env_vars()

    # Create database tables
    print("Initializing database...")
    create_db_and_tables()
    print("Database initialized successfully!")

    # Get host and port from environment or use defaults
    host = os.getenv("API_HOST", "127.0.0.1")  # Changed from 0.0.0.0 to 127.0.0.1 for Windows compatibility
    port = int(os.getenv("API_PORT", "8000"))

    print(f"Starting server on {host}:{port}")

    # Import and run uvicorn directly
    try:
        import uvicorn
        uvicorn.run(
            "src.main:app",
            host=host,
            port=port,
            reload=bool(os.getenv("DEBUG", "False").lower() == "true"),
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
        )
    except ImportError:
        print("Error: uvicorn not found. Please install it with: pip install uvicorn")
        sys.exit(1)


if __name__ == "__main__":
    main()