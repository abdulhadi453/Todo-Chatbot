import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
from backend.src.main import app
from backend.config.database import get_session
from backend.src.models.todo_model import User
from backend.src.auth.jwt-utils import create_access_token, create_refresh_token
from datetime import timedelta
import time


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


def test_full_token_lifecycle_integration(client: TestClient, session: Session):
    """Test the complete token lifecycle: creation, usage, expiration, refresh"""
    # 1. Register a user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "lifecycle@test.com",
            "password": "securepassword123",
            "name": "Lifecycle Test User"
        }
    )
    assert register_response.status_code == 201
    register_data = register_response.json()

    user_id = register_data["user_id"]
    initial_access_token = register_data["access_token"]
    initial_refresh_token = register_data["refresh_token"]

    assert initial_access_token is not None
    assert initial_refresh_token is not None

    # 2. Use the initial access token to access protected endpoints
    headers = {"Authorization": f"Bearer {initial_access_token}"}

    # Get user info
    user_info_response = client.get("/auth/me", headers=headers)
    assert user_info_response.status_code == 200

    # Create a task
    task_response = client.post(
        f"/api/{user_id}/tasks",
        json={"description": "Lifecycle test task"},
        headers=headers
    )
    assert task_response.status_code == 201
    task_data = task_response.json()
    task_id = task_data["id"]

    # 3. Test with a short-lived token that expires
    short_lived_token = create_access_token(
        data={"sub": user_id, "email": "lifecycle@test.com"},
        expires_delta=timedelta(seconds=1)  # Very short expiration
    )

    # Use the short-lived token immediately - should work
    short_headers = {"Authorization": f"Bearer {short_lived_token}"}
    immediate_response = client.get("/auth/me", headers=short_headers)
    assert immediate_response.status_code == 200

    # Wait for the token to expire
    time.sleep(2)

    # Try to use the expired token - should fail
    expired_response = client.get("/auth/me", headers=short_headers)
    assert expired_response.status_code == 401  # Unauthorized

    # 4. Use the refresh token to get a new access token
    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": initial_refresh_token
        }
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    new_access_token = refresh_data["access_token"]
    assert new_access_token is not None
    assert new_access_token != initial_access_token  # Should be a new token

    # 5. Use the new access token to access protected endpoints
    new_headers = {"Authorization": f"Bearer {new_access_token}"}

    # Get user info with new token
    new_user_info_response = client.get("/auth/me", headers=new_headers)
    assert new_user_info_response.status_code == 200

    # Access the task created with the original token
    task_access_response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=new_headers)
    assert task_access_response.status_code == 200
    assert task_access_response.json()["id"] == task_id

    # 6. Create a new task with the refreshed token
    new_task_response = client.post(
        f"/api/{user_id}/tasks",
        json={"description": "Task with refreshed token"},
        headers=new_headers
    )
    assert new_task_response.status_code == 201
    new_task_data = new_task_response.json()
    assert new_task_data["description"] == "Task with refreshed token"

    # 7. Verify both tasks exist for the user
    all_tasks_response = client.get(f"/api/{user_id}/tasks", headers=new_headers)
    assert all_tasks_response.status_code == 200
    all_tasks = all_tasks_response.json()
    assert len(all_tasks) == 2


def test_concurrent_token_usage(client: TestClient, session: Session):
    """Test that multiple valid tokens can be used concurrently"""
    # Register a user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "concurrent@test.com",
            "password": "securepassword123",
            "name": "Concurrent Test User"
        }
    )
    assert register_response.status_code == 201
    register_data = register_response.json()

    user_id = register_data["user_id"]
    access_token_1 = register_data["access_token"]
    refresh_token = register_data["refresh_token"]

    # Generate a second access token via refresh (without logging out the first)
    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    access_token_2 = refresh_data["access_token"]

    # Both tokens should work for accessing user info
    headers1 = {"Authorization": f"Bearer {access_token_1}"}
    headers2 = {"Authorization": f"Bearer {access_token_2}"}

    response1 = client.get("/auth/me", headers=headers1)
    assert response1.status_code == 200

    response2 = client.get("/auth/me", headers=headers2)
    assert response2.status_code == 200

    # Both tokens should work for creating tasks
    task1_response = client.post(
        f"/api/{user_id}/tasks",
        json={"description": "Task with first token"},
        headers=headers1
    )
    assert task1_response.status_code == 201

    task2_response = client.post(
        f"/api/{user_id}/tasks",
        json={"description": "Task with second token"},
        headers=headers2
    )
    assert task2_response.status_code == 201

    # Both tokens should be able to access all tasks
    tasks1_response = client.get(f"/api/{user_id}/tasks", headers=headers1)
    assert tasks1_response.status_code == 200
    tasks2_response = client.get(f"/api/{user_id}/tasks", headers=headers2)
    assert tasks2_response.status_code == 200

    assert len(tasks1_response.json()) == 2
    assert len(tasks2_response.json()) == 2


def test_token_rotation_scenario(client: TestClient, session: Session):
    """Test token rotation where new refresh tokens are issued"""
    # Register a user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "rotation@test.com",
            "password": "securepassword123",
            "name": "Rotation Test User"
        }
    )
    assert register_response.status_code == 201
    register_data = register_response.json()

    access_token = register_data["access_token"]
    refresh_token = register_data["refresh_token"]

    # Use refresh endpoint (in a real implementation, this might return a new refresh token)
    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )
    assert refresh_response.status_code == 200
    new_access_token = refresh_response.json()["access_token"]
    assert new_access_token != access_token

    # The new access token should work
    headers = {"Authorization": f"Bearer {new_access_token}"}
    verify_response = client.get("/auth/me", headers=headers)
    assert verify_response.status_code == 200