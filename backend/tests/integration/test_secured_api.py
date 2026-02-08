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


def test_full_authentication_flow(client: TestClient, session: Session):
    """Test the complete authentication and authorization flow"""
    # 1. Register a new user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "integration@test.com",
            "password": "securepassword123",
            "name": "Integration Test User"
        }
    )
    assert register_response.status_code == 201
    register_data = register_response.json()

    user_id = register_data["user_id"]
    access_token = register_data["access_token"]
    assert access_token is not None

    # 2. Login with the same user
    login_response = client.post(
        "/auth/login",
        json={
            "email": "integration@test.com",
            "password": "securepassword123"
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["access_token"] is not None

    # 3. Get current user info
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = client.get("/auth/me", headers=headers)
    assert user_info_response.status_code == 200
    user_info = user_info_response.json()
    assert user_info["email"] == "integration@test.com"
    assert user_info["name"] == "Integration Test User"

    # 4. Create a todo task for the user
    task_response = client.post(
        f"/api/{user_id}/tasks",
        json={"description": "Integration test task"},
        headers=headers
    )
    assert task_response.status_code == 201
    task_data = task_response.json()
    assert task_data["description"] == "Integration test task"
    assert task_data["user_id"] == user_id

    # 5. Get the user's tasks
    tasks_response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert tasks_response.status_code == 200
    tasks = tasks_response.json()
    assert len(tasks) == 1
    assert tasks[0]["description"] == "Integration test task"

    # 6. Get specific task
    task_id = task_data["id"]
    specific_task_response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert specific_task_response.status_code == 200
    specific_task = specific_task_response.json()
    assert specific_task["id"] == task_id
    assert specific_task["description"] == "Integration test task"

    # 7. Update the task
    update_response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"description": "Updated integration test task", "completed": True},
        headers=headers
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["description"] == "Updated integration test task"
    assert updated_task["completed"] is True

    # 8. Toggle task completion
    toggle_response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete", headers=headers)
    assert toggle_response.status_code == 200
    toggled_task = toggle_response.json()
    assert toggled_task["completed"] is False  # Should be toggled back to False

    # 9. Delete the task
    delete_response = client.delete(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204

    # 10. Verify task is deleted
    tasks_after_delete = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert tasks_after_delete.status_code == 200
    remaining_tasks = tasks_after_delete.json()
    assert len(remaining_tasks) == 0


def test_cross_user_access_prevention(client: TestClient, session: Session):
    """Test that users cannot access each other's data"""
    # Create first user
    user1_register = client.post(
        "/auth/register",
        json={
            "email": "user1@test.com",
            "password": "password123",
            "name": "User 1"
        }
    )
    assert user1_register.status_code == 201
    user1_data = user1_register.json()
    user1_id = user1_data["user_id"]
    user1_token = user1_data["access_token"]

    # Create second user
    user2_register = client.post(
        "/auth/register",
        json={
            "email": "user2@test.com",
            "password": "password123",
            "name": "User 2"
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
        json={"description": "User 1's task"},
        headers=headers_user1
    )
    assert task_response.status_code == 201
    task_data = task_response.json()
    task_id = task_data["id"]

    # User 2 tries to access User 1's task - should be forbidden
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.get(f"/api/{user1_id}/tasks/{task_id}", headers=headers_user2)
    assert response.status_code == 403  # Forbidden

    # User 2 tries to create a task for User 1 - should be forbidden
    response = client.post(
        f"/api/{user1_id}/tasks",
        json={"description": "Trying to create for user 1"},
        headers=headers_user2
    )
    assert response.status_code == 403  # Forbidden

    # User 2 tries to update User 1's task - should be forbidden
    response = client.put(
        f"/api/{user1_id}/tasks/{task_id}",
        json={"description": "Hacked task"},
        headers=headers_user2
    )
    assert response.status_code == 403  # Forbidden

    # User 2 tries to delete User 1's task - should be forbidden
    response = client.delete(f"/api/{user1_id}/tasks/{task_id}", headers=headers_user2)
    assert response.status_code == 403  # Forbidden