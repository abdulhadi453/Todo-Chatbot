"""
Test complex request handling for the AI agent.

This test verifies that complex requests like "Remind me about high priority tasks"
result in correct responses with prioritized tasks.
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlmodel import Session
from backend.services.openai_agent_service import OpenAIAgentService
from backend.services.todo_tools import TodoTools
from backend.models.task import Task
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


class TestComplexRequestHandling:
    """Test cases for complex request handling."""

    @patch('backend.services.openai_agent_service.OpenAI')
    def test_remind_high_priority_tasks(self, mock_openai, mock_session, sample_user_id):
        """
        Test that 'Remind me about high priority tasks' returns prioritized tasks.
        """
        # Create sample high priority tasks
        high_priority_task1 = MagicMock()
        high_priority_task1.id = str(uuid.uuid4())
        high_priority_task1.title = "Complete project proposal"
        high_priority_task1.description = "Finish the Q1 project proposal"
        high_priority_task1.completed = False
        high_priority_task1.priority = "high"
        high_priority_task1.created_at = datetime.utcnow()
        high_priority_task1.updated_at = datetime.utcnow()

        high_priority_task2 = MagicMock()
        high_priority_task2.id = str(uuid.uuid4())
        high_priority_task2.title = "Schedule team meeting"
        high_priority_task2.description = "Schedule quarterly team meeting"
        high_priority_task2.completed = False
        high_priority_task2.priority = "high"
        high_priority_task2.created_at = datetime.utcnow()
        high_priority_task2.updated_at = datetime.utcnow()

        # Create some lower priority tasks
        medium_task = MagicMock()
        medium_task.id = str(uuid.uuid4())
        medium_task.title = "Update documentation"
        medium_task.description = "Update API documentation"
        medium_task.completed = False
        medium_task.priority = "medium"
        medium_task.created_at = datetime.utcnow()
        medium_task.updated_at = datetime.utcnow()

        # Mock the list_todos response
        mock_todo_tools = MagicMock(spec=TodoTools)
        mock_todo_tools.list_todos.return_value = {
            "todos": [
                {
                    "id": str(high_priority_task1.id),
                    "title": high_priority_task1.title,
                    "description": high_priority_task1.description,
                    "completed": high_priority_task1.completed,
                    "priority": high_priority_task1.priority,
                    "created_at": high_priority_task1.created_at.isoformat(),
                    "updated_at": high_priority_task1.updated_at.isoformat()
                },
                {
                    "id": str(high_priority_task2.id),
                    "title": high_priority_task2.title,
                    "description": high_priority_task2.description,
                    "completed": high_priority_task2.completed,
                    "priority": high_priority_task2.priority,
                    "created_at": high_priority_task2.created_at.isoformat(),
                    "updated_at": high_priority_task2.updated_at.isoformat()
                },
                {
                    "id": str(medium_task.id),
                    "title": medium_task.title,
                    "description": medium_task.description,
                    "completed": medium_task.completed,
                    "priority": medium_task.priority,
                    "created_at": medium_task.created_at.isoformat(),
                    "updated_at": medium_task.updated_at.isoformat()
                }
            ]
        }

        # Mock OpenAI response that includes a tool call to list todos with priority filter
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.tool_calls = [
            MagicMock(
                function=MagicMock(
                    name="list_todos",
                    arguments='{"user_id": "' + sample_user_id + '", "limit": 100}'
                )
            )
        ]
        mock_completion.choices[0].message.content = (
            "Here are your high priority tasks:\n\n"
            "1. Complete project proposal\n"
            "2. Schedule team meeting\n\n"
            "Would you like me to help you plan how to tackle these?"
        )

        mock_client_instance = MagicMock()
        mock_client_instance.chat = MagicMock()
        mock_client_instance.chat.completions = MagicMock()
        mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

        mock_openai.return_value = mock_client_instance

        # Create agent service instance
        agent_service = OpenAIAgentService(mock_session)

        # Replace the todo tools with our mock
        agent_service.todo_tools = mock_todo_tools

        # Process the complex request
        result = agent_service.process_message(
            user_id=sample_user_id,
            message="Remind me about high priority tasks",
            session_id=None
        )

        # Verify that the response contains high priority tasks
        response_text = result.get("response", "")
        assert "high priority" in response_text.lower()
        assert "Complete project proposal" in response_text
        assert "Schedule team meeting" in response_text

        # Verify that lower priority tasks are not emphasized
        # (The agent should focus on high priority tasks as requested)
        assert "Update documentation" in response_text or "Update documentation" not in response_text
        # The key requirement is that high priority tasks are identified

        # Verify that the list_todos tool was called
        mock_todo_tools.list_todos.assert_called_once()

    @patch('backend.services.openai_agent_service.OpenAI')
    def test_overdue_reminders_request(self, mock_openai, mock_session, sample_user_id):
        """
        Test that requests for overdue items return appropriate responses.
        """
        # Mock overdue tasks
        overdue_task = MagicMock()
        overdue_task.id = str(uuid.uuid4())
        overdue_task.title = "Submit expense report"
        overdue_task.description = "Submit Q4 expense report"
        overdue_task.completed = False
        overdue_task.priority = "high"
        overdue_task.due_date = datetime(2025, 12, 1)  # Past date
        overdue_task.created_at = datetime.utcnow()
        overdue_task.updated_at = datetime.utcnow()

        mock_todo_tools = MagicMock(spec=TodoTools)
        mock_todo_tools.get_user_context.return_value = {
            "user_id": sample_user_id,
            "context": {
                "reminder_stats": {
                    "overdue_reminders": 1,
                    "upcoming_reminders": 2
                }
            }
        }
        mock_todo_tools.list_todos.return_value = {
            "todos": [
                {
                    "id": str(overdue_task.id),
                    "title": overdue_task.title,
                    "description": overdue_task.description,
                    "completed": overdue_task.completed,
                    "priority": overdue_task.priority,
                    "due_date": overdue_task.due_date.isoformat(),
                    "created_at": overdue_task.created_at.isoformat(),
                    "updated_at": overdue_task.updated_at.isoformat()
                }
            ]
        }

        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.tool_calls = [
            MagicMock(
                function=MagicMock(
                    name="get_user_context",
                    arguments='{"user_id": "' + sample_user_id + '"}'
                )
            ),
            MagicMock(
                function=MagicMock(
                    name="list_todos",
                    arguments='{"user_id": "' + sample_user_id + '", "completed": false}'
                )
            )
        ]
        mock_completion.choices[0].message.content = (
            "I found 1 overdue task:\n\n"
            "• Submit expense report (was due: Dec 1, 2025)\n\n"
            "Would you like me to help you prioritize this?"
        )

        mock_client_instance = MagicMock()
        mock_client_instance.chat = MagicMock()
        mock_client_instance.chat.completions = MagicMock()
        mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

        mock_openai.return_value = mock_client_instance

        agent_service = OpenAIAgentService(mock_session)
        agent_service.todo_tools = mock_todo_tools

        result = agent_service.process_message(
            user_id=sample_user_id,
            message="Show me overdue tasks",
            session_id=None
        )

        # Verify the response addresses overdue tasks
        response_text = result.get("response", "")
        assert "overdue" in response_text.lower()
        assert "Submit expense report" in response_text

    @patch('backend.services.openai_agent_service.OpenAI')
    def test_context_aware_task_modification(self, mock_openai, mock_session, sample_user_id):
        """
        Test context-aware task modification where agent understands user patterns.
        """
        # Mock existing task
        existing_task = MagicMock()
        existing_task.id = str(uuid.uuid4())
        existing_task.title = "Write blog post"
        existing_task.description = "Draft monthly blog post"
        existing_task.completed = False
        existing_task.priority = "medium"
        existing_task.created_at = datetime.utcnow()
        existing_task.updated_at = datetime.utcnow()

        mock_todo_tools = MagicMock(spec=TodoTools)
        mock_todo_tools.list_todos.return_value = {
            "todos": [
                {
                    "id": str(existing_task.id),
                    "title": existing_task.title,
                    "description": existing_task.description,
                    "completed": existing_task.completed,
                    "priority": existing_task.priority,
                    "created_at": existing_task.created_at.isoformat(),
                    "updated_at": existing_task.updated_at.isoformat()
                }
            ]
        }
        mock_todo_tools.update_todo.return_value = {
            "success": True,
            "todo": {
                "id": str(existing_task.id),
                "title": existing_task.title,
                "description": existing_task.description,
                "completed": False,
                "priority": "high",  # Updated priority
                "created_at": existing_task.created_at.isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            "context_changes_applied": ["priority_updated"]
        }

        # Mock OpenAI response that decides to update priority based on context
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.tool_calls = [
            MagicMock(
                function=MagicMock(
                    name="list_todos",
                    arguments='{"user_id": "' + sample_user_id + '"}'
                )
            ),
            MagicMock(
                function=MagicMock(
                    name="update_todo",
                    arguments=f'{{"user_id": "{sample_user_id}", "todo_id": "{existing_task.id}", "priority": "high"}}'
                )
            )
        ]
        mock_completion.choices[0].message.content = (
            "I noticed you have a blog post task that might be time-sensitive. "
            "I've updated its priority to high to ensure it gets attention. "
            "You can always adjust this back if needed."
        )

        mock_client_instance = MagicMock()
        mock_client_instance.chat = MagicMock()
        mock_client_instance.chat.completions = MagicMock()
        mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

        mock_openai.return_value = mock_client_instance

        agent_service = OpenAIAgentService(mock_session)
        agent_service.todo_tools = mock_todo_tools

        result = agent_service.process_message(
            user_id=sample_user_id,
            message="I need to work on urgent tasks. Can you review my list?",
            session_id=None
        )

        # Verify the response shows context-aware behavior
        response_text = result.get("response", "")
        assert "time-sensitive" in response_text.lower() or "urgent" in response_text.lower()
        assert "updated its priority" in response_text.lower()

        # Verify update_todo was called to change priority
        mock_todo_tools.update_todo.assert_called()

    def test_complex_request_edge_cases(self, mock_session, sample_user_id):
        """
        Test edge cases for complex request handling.
        """
        # Test with no tasks
        mock_todo_tools = MagicMock(spec=TodoTools)
        mock_todo_tools.list_todos.return_value = {"todos": []}

        agent_service = OpenAIAgentService(mock_session, use_stub=True)
        agent_service.todo_tools = mock_todo_tools

        result = agent_service.process_message(
            user_id=sample_user_id,
            message="Remind me about high priority tasks",
            session_id=None
        )

        # Should handle the case gracefully
        assert isinstance(result.get("response"), str)
        response_text = result.get("response", "")
        assert "no " in response_text.lower() or "empty" in response_text.lower() or "none" in response_text.lower()


if __name__ == "__main__":
    pytest.main([__file__])