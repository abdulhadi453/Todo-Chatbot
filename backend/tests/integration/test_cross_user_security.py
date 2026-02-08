import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
from backend.src.main import app
from backend.config.database import get_session
from backend.src.models.todo_model import User, TodoTask
from backend.src.auth.jwt-utils import create_access_token


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


def test_comprehensive_cross_user_security(client: TestClient, session: Session):
    """Comprehensive test for cross-user access prevention"""
    # Register User 1
    user1_register = client.post(
        "/auth/register",
        json={
            "email": "crossuser1@test.com",
            "password": "securepassword123",
            "name": "Cross User 1"
        }
    )
    assert user1_register.status_code == 201
    user1_data = user1_register.json()
    user1_id = user1_data["user_id"]
    user1_token = user1_data["access_token"]
    assert user1_token is not None

    # Register User 2
    user2_register = client.post(
        "/auth/register",
        json={
            "email": "crossuser2@test.com",
            "password": "securepassword123",
            "name": "Cross User 2"
        }
    )
    assert user2_register.status_code == 201
    user2_data = user2_register.json()
    user2_id = user2_data["user_id"]
    user2_token = user2_data["access_token"]
    assert user2_token is not None

    # User 1 creates a task
    headers_user1 = {"Authorization": f"Bearer {user1_token}"}
    task_response = client.post(
        f"/api/{user1_id}/tasks",
        json={"description": "User 1's private task"},
        headers=headers_user1
    )
    assert task_response.status_code == 201
    task_data = task_response.json()
    task_id = task_data["id"]
    assert task_id is not None

    # User 2 tries to access User 1's task - should be forbidden
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.get(f"/api/{user1_id}/tasks/{task_id}", headers=headers_user2)
    assert response.status_code == 403  # Forbidden
    assert "Forbidden" in response.json().get("detail", "")

    # User 2 tries to update User 1's task - should be forbidden
    response = client.put(
        f"/api/{user1_id}/tasks/{task_id}",
        json={"description": "User 2 trying to update User 1's task", "completed": True},
        headers=headers_user2
    )
    assert response.status_code == 403  # Forbidden

    # User 2 tries to delete User 1's task - should be forbidden
    response = client.delete(f"/api/{user1_id}/tasks/{task_id}", headers=headers_user2)
    assert response.status_code == 403  # Forbidden

    # User 2 tries to toggle completion of User 1's task - should be forbidden
    response = client.patch(f"/api/{user1_id}/tasks/{task_id}/complete", headers=headers_user2)
    assert response.status_code == 403  # Forbidden

    # User 2 tries to access User 1's task list - should be forbidden
    response = client.get(f"/api/{user1_id}/tasks", headers=headers_user2)
    assert response.status_code == 403  # Forbidden

    # Verify User 1 can still access their own task
    response = client.get(f"/api/{user1_id}/tasks/{task_id}", headers=headers_user1)
    assert response.status_code == 200
    assert response.json()["id"] == task_id

    # User 1 should be able to update their own task
    response = client.put(
        f"/api/{user1_id}/tasks/{task_id}",
        json={"description": "User 1 updated their task", "completed": True},
        headers=headers_user1
    )
    assert response.status_code == 200
    assert response.json()["description"] == "User 1 updated their task"

    # User 1 should be able to delete their own task
    response = client.delete(f"/api/{user1_id}/tasks/{task_id}", headers=headers_user1)
    assert response.status_code == 204

    # Verify task is deleted
    response = client.get(f"/api/{user1_id}/tasks", headers=headers_user1)
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_user_cannot_impersonate_other_users(client: TestClient, session: Session):
    """Test that users cannot impersonate other users by changing URL parameters"""
    # Register User 1
    user1_register = client.post(
        "/auth/register",
        json={
            "email": "impersonate1@test.com",
            "password": "securepassword123",
            "name": "Impersonate User 1"
        }
    )
    assert user1_register.status_code == 201
    user1_data = user1_register.json()
    user1_id = user1_data["user_id"]
    user1_token = user1_data["access_token"]

    # Register User 2
    user2_register = client.post(
        "/auth/register",
        json={
            "email": "impersonate2@test.com",
            "password": "securepassword123",
            "name": "Impersonate User 2"
        }
    )
    assert user2_register.status_code == 201
    user2_data = user2_register.json()
    user2_id = user2_data["user_id"]
    user2_token = user2_data["access_token"]

    # User 1 creates a task
    headers_user1 = {"Authorization": f"Bearer {user1_token}"}
    task_response = client.post(
        f"/api/{user1_id}/tasks",
        json={"description": "User 1's secure task"},
        headers=headers_user1
    )
    assert task_response.status_code == 201
    task_data = task_response.json()
    task_id = task_data["id"]

    # User 2 tries to access User 1's task using User 1's user_id in URL but with their own token
    # This should be forbidden - the token validation should match user_id in token with user_id in URL
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.get(f"/api/{user1_id}/tasks/{task_id}", headers=headers_user2)
    assert response.status_code == 403  # Forbidden

    # User 2 tries to create a task for User 1 (using User 1's ID in URL but with User 2's token)
    response = client.post(
        f"/api/{user1_id}/tasks",
        json={"description": "User 2 trying to create task for User 1"},
        headers=headers_user2
    )
    assert response.status_code == 403  # Forbidden

    # Both users should be able to access their own data
    response = client.get(f"/api/{user1_id}/tasks", headers=headers_user1)
    assert response.status_code == 200

    response = client.get(f"/api/{user2_id}/tasks", headers=headers_user2)
    assert response.status_code == 200


def test_cross_user_security_with_multiple_operations(client: TestClient, session: Session):
    """Test cross-user security across multiple operations"""
    # Register two users
    user1_register = client.post(
        "/auth/register",
        json={
            "email": "multitest1@test.com",
            "password": "securepassword123",
            "name": "Multi Test User 1"
        }
    )
    assert user1_register.status_code == 201
    user1_data = user1_register.json()
    user1_id = user1_data["user_id"]
    user1_token = user1_data["access_token"]

    user2_register = client.post(
        "/auth/register",
        json={
            "email": "multitest2@test.com",
            "password": "securepassword123",
            "name": "Multi Test User 2"
        }
    )
    assert user2_register.status_code == 201
    user2_data = user2_register.json()
    user2_id = user2_data["user_id"]
    user2_token = user2_data["access_token"]

    # User 1 creates multiple tasks
    headers_user1 = {"Authorization": f"Bearer {user1_token}"}
    for i in range(3):
        task_response = client.post(
            f"/api/{user1_id}/tasks",
            json={"description": f"User 1's task {i+1}"},
            headers=headers_user1
        )
        assert task_response.status_code == 201

    # User 2 creates multiple tasks
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    for i in range(2):
        task_response = client.post(
            f"/api/{user2_id}/tasks",
            json={"description": f"User 2's task {i+1}"},
            headers=headers_user2
        )
        assert task_response.status_code == 201

    # Verify each user can only see their own tasks
    user1_tasks = client.get(f"/api/{user1_id}/tasks", headers=headers_user1)
    assert user1_tasks.status_code == 200
    assert len(user1_tasks.json()) == 3

    user2_tasks = client.get(f"/api/{user2_id}/tasks", headers=headers_user2)
    assert user2_tasks.status_code == 200
    assert len(user2_tasks.json()) == 2

    # User 2 tries to access User 1's tasks - should be forbidden
    cross_access = client.get(f"/api/{user1_id}/tasks", headers=headers_user2)
    assert cross_access.status_code == 403  # Forbidden

    # User 1 tries to access User 2's tasks - should be forbidden
    cross_access = client.get(f"/api/{user2_id}/tasks", headers=headers_user1)
    assert cross_access.status_code == 403  # Forbidden