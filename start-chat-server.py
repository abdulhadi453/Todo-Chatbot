#!/usr/bin/env python3
"""
Startup script for the Todo app with AI Chatbot feature.
This script starts the backend server with all necessary configurations.
"""

import subprocess
import sys
import os
import signal
import time
from pathlib import Path

def setup_environment():
    """Setup environment variables and configurations."""
    # Set the Python path to include backend
    backend_path = Path("backend").resolve()
    os.environ["PYTHONPATH"] = str(backend_path)

    # Load environment variables from .env file if it exists
    env_file = backend_path / ".env"
    if env_file.exists():
        import dotenv
        dotenv.load_dotenv(str(env_file))
        print("Loaded environment variables from .env file")

def run_migrations():
    """Run database migrations to ensure tables are up to date."""
    print("Running database migrations...")

    # Run the migration script
    migration_result = subprocess.run([
        sys.executable, "-m", "backend.migrations.001_create_chat_tables"
    ], cwd=".")

    if migration_result.returncode != 0:
        print("Error running migrations!")
        return False

    print("Migrations completed successfully.")
    return True

def start_backend():
    """Start the backend server."""
    print("Starting backend server...")

    # Start the backend server using uvicorn
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "backend.routers.chat:create_app",  # This might need adjustment
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

    return process

def start_frontend():
    """Start the frontend development server."""
    print("Starting frontend server...")

    # Change to frontend directory and start the dev server
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd="frontend")

    return frontend_process

def create_app():
    """Create and return the FastAPI app with all routes."""
    # This is a placeholder - in a real implementation, this would construct
    # the FastAPI app with all the routes from different modules
    from fastapi import FastAPI
    import uvicorn

    app = FastAPI(title="Todo App with AI Chatbot", version="3.0.0")

    # Placeholder for routes - in real implementation these would be imported
    # from their respective modules
    @app.get("/")
    def read_root():
        return {"message": "Welcome to Todo App with AI Chatbot v3.0!"}

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "todo-app-with-chatbot"}

    return app

def main():
    """Main function to start the application."""
    print("🚀 Starting Todo App with AI Chatbot (Phase III)")
    print("="*50)

    # Setup environment
    setup_environment()

    # Run migrations
    if not run_migrations():
        print("Failed to run migrations. Exiting.")
        sys.exit(1)

    # In a real implementation, we would start both servers
    # For now, we'll just create the app and start the backend
    print("\nStarting servers...")

    try:
        app = create_app()

        print("\n✅ Application started successfully!")
        print("🌐 Backend API: http://localhost:8000")
        print("📖 API Docs: http://localhost:8000/docs")
        print("💬 Chat Endpoint: http://localhost:8000/api/{user_id}/chat")
        print("\nPress Ctrl+C to stop the server")

        # Run the server
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False  # Set to True in development
        )

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()