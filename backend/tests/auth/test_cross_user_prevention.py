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


def test_cross_user_access_prevented(client: TestClient, session: Session):
    """Test that users cannot access other users' data"""
    # Create two users
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

    # Create tokens for both users
    user1_token = create_access_token(data={"sub": "user123", "email": "user1@example.com"})
    user2_token = create_access_token(data={"sub": "user456", "email": "user2@example.com"})

    # User 1 creates a task
    headers_user1 = {"Authorization": f"Bearer {user1_token}"}
    task_response = client.post(
        "/api/user123/tasks",
        json={"description": "User 1's task", "user_id": "user123"},
        headers=headers_user1
    )
    assert task_response.status_code == 201
    task_data = task_response.json()
    task_id = task_data["id"]

    # User 2 tries to access User 1's task - should be forbidden
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.get(f"/api/user123/tasks/{task_id}", headers=headers_user2)
    assert response.status_code == 403  # Forbidden

    # User 2 tries to update User 1's task - should be forbidden
    response = client.put(
        f"/api/user123/tasks/{task_id}",
        json={"description": "Hacked task"},
        headers=headers_user2
    )
    assert response.status_code == 403  # Forbidden

    # User 2 tries to delete User 1's task - should be forbidden
    response = client.delete(f"/api/user123/tasks/{task_id}", headers=headers_user2)
    assert response.status_code == 403  # Forbidden


def test_user_can_access_own_data(client: TestClient, session: Session):
    """Test that users can access their own data"""
    # Create a user
    user = User(
        id="ownuser123",
        email="ownuser@example.com",
        password_hash=User.hash_password("password123"),
        name="Own User"
    )
    session.add(user)
    session.commit()

    # Create a token for the user
    token = create_access_token(data={"sub": "ownuser123", "email": "ownuser@example.com"})

    # Create a task for the user
    headers = {"Authorization": f"Bearer {token}"}
    task_response = client.post(
        "/api/ownuser123/tasks",
        json={"description": "Own task", "user_id": "ownuser123"},
        headers=headers
    )
    assert task_response.status_code == 201
    task_data = task_response.json()
    task_id = task_data["id"]

    # User should be able to access their own task
    response = client.get(f"/api/ownuser123/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id

    # User should be able to update their own task
    response = client.put(
        f"/api/ownuser123/tasks/{task_id}",
        json={"description": "Updated own task"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated own task"

    # User should be able to delete their own task
    response = client.delete(f"/api/ownuser123/tasks/{task_id}", headers=headers)
    assert response.status_code == 204


def test_user_id_mismatch_in_url(client: TestClient, session: Session):
    """Test that user_id in URL must match the authenticated user"""
    # Create a user
    user = User(
        id="testuser123",
        email="testuser@example.com",
        password_hash=User.hash_password("password123"),
        name="Test User"
    )
    session.add(user)
    session.commit()

    # Create a token for the user
    token = create_access_token(data={"sub": "testuser123", "email": "testuser@example.com"})

    # User tries to access their own tasks using a different user_id in URL - should be forbidden
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/differentuser123/tasks", headers=headers)
    assert response.status_code == 403  # Forbidden

    # User tries to create task using different user_id in URL - should be forbidden
    response = client.post(
        "/api/differentuser123/tasks",
        json={"description": "Task for different user"},
        headers=headers
    )
    assert response.status_code == 403  # Forbidden