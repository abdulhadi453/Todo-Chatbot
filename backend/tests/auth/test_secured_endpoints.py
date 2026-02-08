import pytest
import sys
import os
# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
from main import app
from config.database import get_session
from models.todo_model import User, TodoTask
from auth.jwt_utils import create_access_token


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_secured_todo_endpoints_require_auth(client: TestClient):
    """Test that secured todo endpoints require authentication"""
    user_id = "testuser123"

    # Try to access secured endpoints without auth - should fail
    response = client.get(f"/api/{user_id}/tasks")
    assert response.status_code == 401  # Unauthorized

    response = client.post(f"/api/{user_id}/tasks", json={"description": "Test task"})
    assert response.status_code == 401  # Unauthorized

    response = client.get(f"/api/{user_id}/tasks/1")
    assert response.status_code == 401  # Unauthorized

    response = client.put(f"/api/{user_id}/tasks/1", json={"description": "Updated"})
    assert response.status_code == 401  # Unauthorized

    response = client.delete(f"/api/{user_id}/tasks/1")
    assert response.status_code == 401  # Unauthorized

    response = client.patch(f"/api/{user_id}/tasks/1/complete")
    assert response.status_code == 401  # Unauthorized


def test_secured_endpoints_with_valid_auth(client: TestClient, session: Session):
    """Test secured endpoints with valid authentication"""
    # Create a user in the database
    user = User(
        id="testuser123",
        email="test@example.com",
        password_hash=User.hash_password("password123"),
        name="Test User"
    )
    session.add(user)
    session.commit()

    # Create a valid token for the user
    token = create_access_token(data={"sub": "testuser123", "email": "test@example.com"})

    # Test secured endpoints with valid auth
    headers = {"Authorization": f"Bearer {token}"}

    # Create a task
    response = client.post(
        "/api/testuser123/tasks",
        json={"description": "Test task"},
        headers=headers
    )
    assert response.status_code == 201

    # Get user's tasks
    response = client.get(f"/api/testuser123/tasks", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_user_id_mismatch_forbidden(client: TestClient, session: Session):
    """Test that user cannot access other users' data"""
    # Create two users in the database
    user1 = User(
        id="user123",
        email="user1@example.com",
        password_hash=User.hash_password("password123"),
        name="User 1"
    )
    user2 = User(
        id="user456",
        email="user2@example.com",
        password_hash=User.hash_password("password123"),
        name="User 2"
    )
    session.add(user1)
    session.add(user2)
    session.commit()

    # Create a token for user1
    token = create_access_token(data={"sub": "user123", "email": "user1@example.com"})

    # Try to access user2's tasks using user1's token - should be forbidden
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/api/user456/tasks", headers=headers)
    assert response.status_code == 403  # Forbidden

    response = client.post(f"/api/user456/tasks", json={"description": "Test task"}, headers=headers)
    assert response.status_code == 403  # Forbidden

    response = client.get(f"/api/user456/tasks/1", headers=headers)
    assert response.status_code == 403  # Forbidden