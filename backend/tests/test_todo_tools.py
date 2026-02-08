"""
Unit tests for the todo tools used by the AI agent.

This module tests individual tool functions for proper behavior,
error handling, and data validation.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from sqlmodel import Session, select
from backend.services.todo_tools import TodoTools
from backend.src.models.todo_model import TodoTask
import uuid
from datetime import datetime


@pytest.fixture
def mock_session():
    """Create a mock database session for testing."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def sample_user_id():
    """Provide a sample user ID for testing."""
    return str(uuid.uuid4())


class TestTodoTools:
    """Unit tests for the TodoTools class and its methods."""

    def test_list_todos_success(self, mock_session, sample_user_id):
        """Test that list_todos returns the correct todos for a user."""
        # Create sample todos
        todo1 = MagicMock(spec=TodoTask)
        todo1.id = "1"
        todo1.title = "First task"
        todo1.description = "Description for first task"
        todo1.completed = False
        todo1.user_id = sample_user_id
        todo1.created_at = datetime.utcnow()
        todo1.updated_at = datetime.utcnow()

        todo2 = MagicMock(spec=TodoTask)
        todo2.id = "2"
        todo2.title = "Second task"
        todo2.description = "Description for second task"
        todo2.completed = True
        todo2.user_id = sample_user_id
        todo2.created_at = datetime.utcnow()
        todo2.updated_at = datetime.utcnow()

        mock_session.exec.return_value.all.return_value = [todo1, todo2]

        # Create TodoTools instance and call list_todos
        todo_tools = TodoTools(mock_session)
        result = todo_tools.list_todos(user_id=sample_user_id)

        # Verify the session was called correctly
        mock_session.exec.assert_called_once()
        assert len(result) == 2
        assert result[0].title == "First task"
        assert result[1].completed is True

    def test_add_todo_success(self, mock_session, sample_user_id):
        """Test that add_todo creates a new todo with correct attributes."""
        # Create a mock todo that will be returned after adding
        new_todo = MagicMock(spec=TodoTask)
        new_todo.id = str(uuid.uuid4())
        new_todo.title = "New task"
        new_todo.description = "New task description"
        new_todo.completed = False
        new_todo.user_id = sample_user_id

        # Configure the mock to return our new todo
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        # Patch the TodoTask creation to return our mock
        with patch('backend.services.todo_tools.TodoTask') as mock_todo_class:
            mock_todo_class.return_value = new_todo

            todo_tools = TodoTools(mock_session)
            result = todo_tools.add_todo(
                user_id=sample_user_id,
                title="New task",
                description="New task description"
            )

            # Verify that the todo was created with correct attributes
            mock_todo_class.assert_called_once()
            args, kwargs = mock_todo_class.call_args
            assert kwargs['user_id'] == sample_user_id
            assert kwargs['title'] == "New task"
            assert kwargs['description'] == "New task description"

            # Verify session operations
            mock_session.add.assert_called_once_with(new_todo)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(new_todo)

            assert result.id == new_todo.id

    def test_update_todo_success(self, mock_session, sample_user_id):
        """Test that update_todo modifies an existing todo."""
        # Create a mock existing todo
        existing_todo = MagicMock(spec=TodoTask)
        existing_todo.id = "1"
        existing_todo.title = "Old title"
        existing_todo.description = "Old description"
        existing_todo.completed = False
        existing_todo.user_id = sample_user_id

        # Configure exec to return the existing todo
        mock_statement = MagicMock()
        mock_exec_result = MagicMock()
        mock_exec_result.first.return_value = existing_todo

        mock_session.exec.return_value = mock_exec_result
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        todo_tools = TodoTools(mock_session)
        result = todo_tools.update_todo(
            todo_id="1",
            user_id=sample_user_id,
            title="Updated title",
            description="Updated description",
            completed=True
        )

        # Verify that attributes were updated
        assert existing_todo.title == "Updated title"
        assert existing_todo.description == "Updated description"
        assert existing_todo.completed is True

        # Verify session operations
        mock_session.add.assert_called_once_with(existing_todo)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(existing_todo)

        assert result == existing_todo

    def test_update_todo_not_found(self, mock_session, sample_user_id):
        """Test that update_todo returns None when todo is not found."""
        # Configure exec to return None (todo not found)
        mock_exec_result = MagicMock()
        mock_exec_result.first.return_value = None
        mock_session.exec.return_value = mock_exec_result

        todo_tools = TodoTools(mock_session)
        result = todo_tools.update_todo(
            todo_id="999",
            user_id=sample_user_id,
            title="Updated title"
        )

        assert result is None

    def test_delete_todo_success(self, mock_session, sample_user_id):
        """Test that delete_todo removes an existing todo."""
        # Create a mock existing todo
        existing_todo = MagicMock(spec=TodoTask)
        existing_todo.id = "1"
        existing_todo.user_id = sample_user_id

        # Configure exec to return the existing todo
        mock_exec_result = MagicMock()
        mock_exec_result.first.return_value = existing_todo
        mock_session.exec.return_value = mock_exec_result
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()

        todo_tools = TodoTools(mock_session)
        result = todo_tools.delete_todo(todo_id="1", user_id=sample_user_id)

        # Verify that delete was called with the correct todo
        mock_session.delete.assert_called_once_with(existing_todo)
        mock_session.commit.assert_called_once()
        assert result is True

    def test_delete_todo_not_found(self, mock_session, sample_user_id):
        """Test that delete_todo returns False when todo is not found."""
        # Configure exec to return None (todo not found)
        mock_exec_result = MagicMock()
        mock_exec_result.first.return_value = None
        mock_session.exec.return_value = mock_exec_result

        todo_tools = TodoTools(mock_session)
        result = todo_tools.delete_todo(todo_id="999", user_id=sample_user_id)

        assert result is False

    def test_get_user_context_success(self, mock_session, sample_user_id):
        """Test that get_user_context retrieves user context properly."""
        # Create a mock user context
        from backend.models.user_context import UserContext  # Adjust import as needed
        mock_context = MagicMock(spec=UserContext)
        mock_context.user_id = sample_user_id
        mock_context.preferences = {"theme": "dark", "language": "en"}
        mock_context.usage_stats = {"total_tasks": 10}

        mock_exec_result = MagicMock()
        mock_exec_result.first.return_value = mock_context
        mock_session.exec.return_value = mock_exec_result

        todo_tools = TodoTools(mock_session)
        result = todo_tools.get_user_context(user_id=sample_user_id)

        assert result == mock_context

    def test_get_user_context_not_found(self, mock_session, sample_user_id):
        """Test that get_user_context returns None when context is not found."""
        mock_exec_result = MagicMock()
        mock_exec_result.first.return_value = None
        mock_session.exec.return_value = mock_exec_result

        todo_tools = TodoTools(mock_session)
        result = todo_tools.get_user_context(user_id=sample_user_id)

        assert result is None

    def test_list_todos_empty_result(self, mock_session, sample_user_id):
        """Test that list_todos handles empty results correctly."""
        mock_session.exec.return_value.all.return_value = []

        todo_tools = TodoTools(mock_session)
        result = todo_tools.list_todos(user_id=sample_user_id)

        assert result == []

    def test_add_todo_with_defaults(self, mock_session, sample_user_id):
        """Test that add_todo works with minimal parameters."""
        new_todo = MagicMock(spec=TodoTask)
        new_todo.id = str(uuid.uuid4())
        new_todo.title = "Simple task"
        new_todo.completed = False
        new_todo.user_id = sample_user_id

        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        with patch('backend.services.todo_tools.TodoTask') as mock_todo_class:
            mock_todo_class.return_value = new_todo

            todo_tools = TodoTools(mock_session)
            result = todo_tools.add_todo(user_id=sample_user_id, title="Simple task")

            # Verify default values were used
            args, kwargs = mock_todo_class.call_args
            assert kwargs['user_id'] == sample_user_id
            assert kwargs['title'] == "Simple task"
            # Description might default to empty string or None depending on model
            assert kwargs['completed'] is False  # Default value

    def test_update_todo_partial_fields(self, mock_session, sample_user_id):
        """Test that update_todo only updates provided fields."""
        existing_todo = MagicMock(spec=TodoTask)
        existing_todo.id = "1"
        existing_todo.title = "Original title"
        existing_todo.description = "Original description"
        existing_todo.completed = False
        existing_todo.user_id = sample_user_id

        mock_exec_result = MagicMock()
        mock_exec_result.first.return_value = existing_todo
        mock_session.exec.return_value = mock_exec_result
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        todo_tools = TodoTools(mock_session)
        result = todo_tools.update_todo(
            todo_id="1",
            user_id=sample_user_id,
            title="Updated title"
            # Only updating title, leaving others unchanged
        )

        # Verify only the title was changed
        assert existing_todo.title == "Updated title"
        # Other fields should retain their original values
        assert existing_todo.description == "Original description"
        assert existing_todo.completed is False

    def test_tool_functions_handle_errors_gracefully(self, mock_session, sample_user_id):
        """Test that tool functions handle errors appropriately."""
        # Simulate an exception in the database session
        mock_session.exec.side_effect = Exception("Database error")

        todo_tools = TodoTools(mock_session)

        # This should raise an exception that the caller needs to handle
        with pytest.raises(Exception) as exc_info:
            todo_tools.list_todos(user_id=sample_user_id)

        assert "Database error" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])