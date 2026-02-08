from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Try relative imports first (when running as a module)
try:
    from .api.todo_router import router as todo_router
    from .api.auth_router import router as auth_router
    from .config.database import create_db_and_tables
except ImportError:
    # Fall back to absolute imports (when running directly)
    import sys
    import os.path
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from api.todo_router import router as todo_router
    from api.auth_router import router as auth_router
    from config.database import create_db_and_tables

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

@app.get("/")
def read_root():
    return {"message": "Todo Backend API with Authentication"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "authenticated": True}