import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.config.database import get_session
from sqlmodel import Session, SQLModel
from sqlalchemy.pool import StaticPool


@pytest.fixture(name="client")
def client_fixture():
    # Use an in-memory SQLite database for testing
    from sqlmodel import create_engine
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Override the database session
    def get_test_session():
        SQLModel.metadata.create_all(bind=test_engine)
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_task(client: TestClient):
    """Test creating a new todo task"""
    response = client.post(
        "/api/user123/tasks",
        json={"description": "Test task", "completed": False, "user_id": "user123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Test task"
    assert data["user_id"] == "user123"
    assert data["completed"] is False


def test_get_user_tasks(client: TestClient):
    """Test retrieving all tasks for a user"""
    # First create a task
    client.post(
        "/api/user123/tasks",
        json={"description": "Test task", "completed": False, "user_id": "user123"}
    )

    # Then get all tasks for the user
    response = client.get("/api/user123/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Test task"


def test_get_specific_task(client: TestClient):
    """Test retrieving a specific task"""
    # Create a task first
    create_response = client.post(
        "/api/user123/tasks",
        json={"description": "Test task", "completed": False, "user_id": "user123"}
    )
    task_id = create_response.json()["id"]

    # Get the specific task
    response = client.get(f"/api/user123/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Test task"


def test_update_task(client: TestClient):
    """Test updating a task"""
    # Create a task first
    create_response = client.post(
        "/api/user123/tasks",
        json={"description": "Original task", "completed": False, "user_id": "user123"}
    )
    task_id = create_response.json()["id"]

    # Update the task
    response = client.put(
        f"/api/user123/tasks/{task_id}",
        json={"description": "Updated task", "completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated task"
    assert data["completed"] is True


def test_delete_task(client: TestClient):
    """Test deleting a task"""
    # Create a task first
    create_response = client.post(
        "/api/user123/tasks",
        json={"description": "Test task to delete", "completed": False, "user_id": "user123"}
    )
    task_id = create_response.json()["id"]

    # Delete the task
    response = client.delete(f"/api/user123/tasks/{task_id}")
    assert response.status_code == 204


def test_toggle_completion(client: TestClient):
    """Test toggling task completion status"""
    # Create a task first
    create_response = client.post(
        "/api/user123/tasks",
        json={"description": "Test task", "completed": False, "user_id": "user123"}
    )
    task_id = create_response.json()["id"]

    # Toggle completion
    response = client.patch(f"/api/user123/tasks/{task_id}/complete", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True  # Initially false, so toggling makes it true