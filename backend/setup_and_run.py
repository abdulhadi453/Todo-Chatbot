#!/usr/bin/env python3
"""
Todo Backend API Setup and Run Script

This script handles the complete setup process for the Todo Backend API:
1. Installs required dependencies
2. Initializes the database
3. Starts the server
"""

import os
import sys
import subprocess

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
        print("✓ Environment variables loaded from .env file")


def install_requirements():
    """Install all required packages from requirements.txt"""
    requirements_file = "backend/requirements.txt"

    if not os.path.exists(requirements_file):
        print(f"❌ Error: {requirements_file} not found!")
        return False

    print("📦 Installing required packages...")

    try:
        # Install packages
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], check=True, capture_output=False)  # Show output directly

        print("✅ Installation completed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def check_dependencies():
    """Check if key dependencies are available"""
    try:
        import fastapi
        import sqlmodel
        import uvicorn
        print("V All key dependencies are available!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False


def initialize_database():
    """Initialize the database and create tables"""
    print("DB Initializing database...")

    try:
        create_db_and_tables()
        print("V Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False


def start_server():
    """Start the FastAPI server"""
    print("SERVER: Starting Todo Backend API server...")

    try:
        import uvicorn

        # Load environment variables
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", "8000"))

        print(f"WEB: Server will start on {host}:{port}")
        print(f"DOC: Visit http://{host}:{port}/docs for API documentation")
        print(f"STOP: Press Ctrl+C to stop the server")

        # Run the server
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=bool(os.getenv("DEBUG", "False").lower() == "true"),
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            app_dir="./src"
        )

    except KeyboardInterrupt:
        print("\nSTOPPED: Server stopped by user")
    except ImportError:
        print("❌ Uvicorn not available. Please install it with: pip install uvicorn")
    except Exception as e:
        print(f"❌ Error starting server: {e}")


def main():
    """Main function to orchestrate the setup and run process"""
    print("Todo Backend API - Complete Setup and Run")
    print("=" * 50)
    print("Step 1: Loading environment variables")
    load_env_vars()

    print("\nStep 2: Checking dependencies")
    if not check_dependencies():
        print("⚠️  Some dependencies are missing, attempting to install...")
        print("Step 3: Installing requirements")
        if not install_requirements():
            print("❌ Failed to install requirements. Please install manually.")
            return
        print("\nRechecking dependencies after installation...")
        if not check_dependencies():
            print("❌ Still missing dependencies after installation.")
            return

    print("\nStep 4: Initializing database")
    if not initialize_database():
        print("❌ Failed to initialize database.")
        return

    print("\nStep 5: Starting the server")
    start_server()

    print("\nSUCCESS: Setup and run process completed!")


if __name__ == "__main__":
    main()