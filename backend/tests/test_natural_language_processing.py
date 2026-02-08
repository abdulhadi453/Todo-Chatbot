"""
Test natural language command processing for the AI agent.

This test verifies that natural language commands like "Add a task to buy groceries"
properly result in todo operations being performed successfully.
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlmodel import Session, select
from backend.src.models.todo_model import TodoTask
from backend.services.openai_agent_service import OpenAIAgentService
from backend.services.todo_tools import TodoTools
from backend.models.agent_session import AgentSession
from backend.models.agent_message import AgentMessage
from backend.models.user_context import UserContext
import uuid


@pytest.fixture
def mock_session():
    """Create a mock database session for testing."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def sample_user_id():
    """Provide a sample user ID for testing."""
    return str(uuid.uuid4())


class TestNaturalLanguageProcessing:
    """Test cases for natural language command processing."""

    @patch('backend.services.openai_agent_service.OpenAI')
    def test_add_todo_command_processing(self, mock_openai, mock_session, sample_user_id):
        """
        Test that 'Add a task to buy groceries' creates a new todo.

        Verifies the end-to-end flow from natural language command to database operation.
        """
        # Mock OpenAI response that includes a tool call to create a todo
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.tool_calls = [
            MagicMock(
                function=MagicMock(
                    name="add_todo",
                    arguments='{"title": "Buy groceries", "description": "Need to buy milk, bread, eggs"}'
                )
            )
        ]
        mock_completion.choices[0].message.content = "I've added the task to buy groceries to your list."

        mock_client_instance = MagicMock()
        mock_client_instance.beta = MagicMock()
        mock_client_instance.beta.threads = MagicMock()
        mock_client_instance.beta.threads.runs = MagicMock()
        mock_client_instance.beta.threads.runs.retrieve = MagicMock(return_value=MagicMock(status="completed"))
        mock_client_instance.chat = MagicMock()
        mock_client_instance.chat.completions = MagicMock()
        mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

        mock_openai.return_value = mock_client_instance

        # Create agent service instance
        agent_service = OpenAIAgentService(mock_session)

        # Mock the TodoTools to track the add_todo call
        with patch.object(TodoTools, 'add_todo', return_value=MagicMock(id=str(uuid.uuid4()), title="Buy groceries")):
            # Process the natural language command
            result = agent_service.process_message(
                user_id=sample_user_id,
                message="Add a task to buy groceries",
                session_id=None
            )

            # Verify that the response indicates success
            assert "buy groceries" in result.get("response", "").lower()

            # Verify that the add_todo method was called
            TodoTools.add_todo.assert_called_once()

    @patch('backend.services.openai_agent_service.OpenAI')
    def test_list_todos_command_processing(self, mock_openai, mock_session, sample_user_id):
        """
        Test that 'Show me my tasks' returns a list of todos.

        Verifies that natural language commands for listing todos work correctly.
        """
        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.tool_calls = [
            MagicMock(
                function=MagicMock(
                    name="list_todos",
                    arguments='{}'
                )
            )
        ]
        mock_completion.choices[0].message.content = "Here are your current tasks: Buy groceries, Finish report."

        mock_client_instance = MagicMock()
        mock_client_instance.chat = MagicMock()
        mock_client_instance.chat.completions = MagicMock()
        mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

        mock_openai.return_value = mock_client_instance

        # Mock TodoTools to return sample todos
        mock_todo = MagicMock()
        mock_todo.id = str(uuid.uuid4())
        mock_todo.title = "Sample task"
        mock_todo.completed = False

        with patch.object(TodoTools, 'list_todos', return_value=[mock_todo]):
            agent_service = OpenAIAgentService(mock_session)

            result = agent_service.process_message(
                user_id=sample_user_id,
                message="Show me my tasks",
                session_id=None
            )

            # Verify that the response includes the todo information
            assert "sample task" in result.get("response", "").lower()
            TodoTools.list_todos.assert_called_once()

    @patch('backend.services.openai_agent_service.OpenAI')
    def test_update_todo_command_processing(self, mock_openai, mock_session, sample_user_id):
        """
        Test that 'Mark the grocery task as completed' updates a todo.

        Verifies that natural language commands for updating todos work correctly.
        """
        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.tool_calls = [
            MagicMock(
                function=MagicMock(
                    name="update_todo",
                    arguments='{"todo_id": "1", "completed": true}'
                )
            )
        ]
        mock_completion.choices[0].message.content = "I've marked the grocery task as completed."

        mock_client_instance = MagicMock()
        mock_client_instance.chat = MagicMock()
        mock_client_instance.chat.completions = MagicMock()
        mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

        mock_openai.return_value = mock_client_instance

        # Mock TodoTools to return updated todo
        updated_todo = MagicMock()
        updated_todo.id = "1"
        updated_todo.title = "Buy groceries"
        updated_todo.completed = True

        with patch.object(TodoTools, 'update_todo', return_value=updated_todo):
            agent_service = OpenAIAgentService(mock_session)

            result = agent_service.process_message(
                user_id=sample_user_id,
                message="Mark the grocery task as completed",
                session_id=None
            )

            # Verify that the response confirms the update
            assert "completed" in result.get("response", "").lower()
            TodoTools.update_todo.assert_called_once()

    @patch('backend.services.openai_agent_service.OpenAI')
    def test_delete_todo_command_processing(self, mock_openai, mock_session, sample_user_id):
        """
        Test that 'Delete the old task' deletes a todo.

        Verifies that natural language commands for deleting todos work correctly.
        """
        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.tool_calls = [
            MagicMock(
                function=MagicMock(
                    name="delete_todo",
                    arguments='{"todo_id": "1"}'
                )
            )
        ]
        mock_completion.choices[0].message.content = "I've deleted the old task for you."

        mock_client_instance = MagicMock()
        mock_client_instance.chat = MagicMock()
        mock_client_instance.chat.completions = MagicMock()
        mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

        mock_openai.return_value = mock_client_instance

        # Mock TodoTools to handle deletion
        with patch.object(TodoTools, 'delete_todo', return_value=True):
            agent_service = OpenAIAgentService(mock_session)

            result = agent_service.process_message(
                user_id=sample_user_id,
                message="Delete the old task",
                session_id=None
            )

            # Verify that the response confirms the deletion
            assert "deleted" in result.get("response", "").lower()
            TodoTools.delete_todo.assert_called_once()

    def test_command_processing_edge_cases(self, mock_session, sample_user_id):
        """
        Test edge cases in natural language command processing.

        Verifies that the system handles invalid commands gracefully.
        """
        # Create agent service instance with stub mode
        agent_service = OpenAIAgentService(mock_session, use_stub=True)

        # Test with an empty command
        result = agent_service.process_message(
            user_id=sample_user_id,
            message="",
            session_id=None
        )

        # Should return a helpful response for empty input
        assert isinstance(result.get("response"), str)

        # Test with a command that doesn't map to any todo operation
        result = agent_service.process_message(
            user_id=sample_user_id,
            message="What's the weather today?",
            session_id=None
        )

        # Should still return a response even if not a todo command
        assert isinstance(result.get("response"), str)


if __name__ == "__main__":
    pytest.main([__file__])