from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Add the backend directory to the Python path to allow absolute imports
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import using absolute paths
from backend.src.api.todo_router import router as todo_router
from backend.src.api.auth_router import router as auth_router
from backend.config.database import create_db_and_tables
from backend.routers.agent import router as agent_router  # AI Agent router

# Create FastAPI app with additional metadata for authentication
app = FastAPI(
    title="Todo Backend API with Authentication",
    description="A FastAPI backend for managing todo tasks with user scoping and JWT authentication",
    version="1.0.0",
    contact={
        "name": "Todo API Support",
        "url": "http://example.com/support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def on_startup():
    create_db_and_tables()

# Include routers
app.include_router(auth_router)  # Authentication endpoints
app.include_router(todo_router)  # Todo endpoints
app.include_router(agent_router)  # AI Agent endpoints

@app.get("/")
def read_root():
    return {"message": "Todo Backend API with Authentication"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "authenticated": True}