import pytest
from sqlmodel import Session, SQLModel
from sqlalchemy.pool import StaticPool
from backend.src.models.todo_model import TodoTask, TodoTaskCreate
from backend.src.services.todo_service import (
    create_task, get_tasks_by_user, get_task_by_id,
    update_task, delete_task, toggle_task_completion
)
from datetime import datetime


@pytest.fixture(name="session")
def session_fixture():
    from sqlmodel import create_engine
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


def test_create_task(session: Session):
    """Test creating a new todo task"""
    task_create = TodoTaskCreate(
        description="Test task",
        completed=False,
        user_id="user123"
    )

    created_task = create_task(session, task_create)

    assert created_task.description == "Test task"
    assert created_task.completed is False
    assert created_task.user_id == "user123"
    assert created_task.id is not None


def test_get_tasks_by_user(session: Session):
    """Test getting all tasks for a user"""
    # Create a task first
    task_create = TodoTaskCreate(
        description="Test task",
        completed=False,
        user_id="user123"
    )
    create_task(session, task_create)

    # Get tasks for the user
    tasks = get_tasks_by_user(session, "user123")

    assert len(tasks) == 1
    assert tasks[0].description == "Test task"


def test_get_task_by_id(session: Session):
    """Test getting a specific task by ID"""
    # Create a task first
    task_create = TodoTaskCreate(
        description="Test task",
        completed=False,
        user_id="user123"
    )
    created_task = create_task(session, task_create)

    # Get the task by ID
    retrieved_task = get_task_by_id(session, created_task.id, "user123")

    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.description == "Test task"


def test_update_task(session: Session):
    """Test updating a task"""
    # Create a task first
    task_create = TodoTaskCreate(
        description="Original task",
        completed=False,
        user_id="user123"
    )
    created_task = create_task(session, task_create)

    # Update the task
    from backend.src.models.todo_model import TodoTaskUpdate
    update_data = TodoTaskUpdate(
        description="Updated task",
        completed=True
    )

    updated_task = update_task(session, created_task.id, "user123", update_data)

    assert updated_task is not None
    assert updated_task.description == "Updated task"
    assert updated_task.completed is True


def test_delete_task(session: Session):
    """Test deleting a task"""
    # Create a task first
    task_create = TodoTaskCreate(
        description="Test task to delete",
        completed=False,
        user_id="user123"
    )
    created_task = create_task(session, task_create)

    # Delete the task
    result = delete_task(session, created_task.id, "user123")

    assert result is True

    # Verify the task is gone
    retrieved_task = get_task_by_id(session, created_task.id, "user123")
    assert retrieved_task is None


def test_toggle_task_completion(session: Session):
    """Test toggling task completion"""
    # Create a task first
    task_create = TodoTaskCreate(
        description="Test task",
        completed=False,  # Start as not completed
        user_id="user123"
    )
    created_task = create_task(session, task_create)

    # Toggle completion
    toggled_task = toggle_task_completion(session, created_task.id, "user123")

    assert toggled_task is not None
    assert toggled_task.completed is True  # Should now be completed

    # Toggle again to make sure it goes back
    toggled_again_task = toggle_task_completion(session, created_task.id, "user123")

    assert toggled_again_task is not None
    assert toggled_again_task.completed is False  # Should now be not completed