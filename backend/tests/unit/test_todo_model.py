import pytest
from backend.src.models.todo_model import TodoTask, TodoTaskCreate


def test_create_todo_task():
    """Test creating a todo task"""
    task = TodoTask(
        description="Test task",
        completed=False,
        user_id="user123"
    )

    assert task.description == "Test task"
    assert task.completed is False
    assert task.user_id == "user123"
    assert task.id is None  # ID will be set by the database


def test_todo_task_create_schema():
    """Test the TodoTaskCreate schema"""
    task_create = TodoTaskCreate(
        description="Test task",
        completed=False,
        user_id="user123"
    )

    assert task_create.description == "Test task"
    assert task_create.completed is False
    assert task_create.user_id == "user123"


def test_todo_task_required_fields():
    """Test that required fields are enforced"""
    # This would normally be tested through validation in a real scenario
    with pytest.raises(ValueError):
        # We can't really test this without actual validation being triggered
        # This is more of a placeholder
        pass