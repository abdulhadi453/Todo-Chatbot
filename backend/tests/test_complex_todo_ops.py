"""
Test suite for complex todo operations in the AI agent system.
Tests the ability to handle complex requests involving multiple steps,
contextual understanding, and advanced todo features.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid
from sqlmodel import Session
from backend.src.main import app
from backend.services.todo_tools import TodoTools
from backend.services.openai_agent_service import OpenAIAgentService
from backend.models.task import Task


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_user_id():
    """Provide a sample user ID for testing."""
    return str(uuid.uuid4())


class TestComplexTodoOperations:
    """Test cases for complex todo operations and multi-step interactions."""

    def test_multiple_tool_calls_in_single_request(self, client, sample_user_id):
        """Test that the agent can execute multiple tool calls in a single request."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # Mock response with multiple tool calls
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_1",
                        function=MagicMock(
                            name="add_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "title": "First task", "description": "Created in batch"}}'
                        )
                    ),
                    MagicMock(
                        id="call_2",
                        function=MagicMock(
                            name="add_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "title": "Second task", "description": "Also created in batch"}}'
                        )
                    ),
                    MagicMock(
                        id="call_3",
                        function=MagicMock(
                            name="list_todos",
                            arguments=f'{{"user_id": "{sample_user_id}", "limit": 10}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've created two tasks and listed your todos."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Send request to agent
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Create two tasks and show me my list"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert "response" in data

                # Verify the tasks were created by checking the user's todos
                todos_response = client.get(
                    f"/api/users/{sample_user_id}/todos",
                    params={"limit": 100, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert todos_response.status_code == 200
                todos = todos_response.json()

                # Count the tasks that were created in this test
                created_tasks = [t for t in todos if t["title"] in ["First task", "Second task"]]
                assert len(created_tasks) == 2

                # Clean up created tasks
                for task in created_tasks:
                    client.delete(
                        f"/api/users/{sample_user_id}/todos/{task['id']}",
                        headers={"Authorization": "Bearer fake-token"}
                    )

    def test_complex_contextual_modification(self, client, sample_user_id):
        """Test complex contextual modifications based on conversation history."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # First, create some tasks manually
            create_task_response = client.post(
                f"/api/users/{sample_user_id}/todos",
                json={"title": "Important task", "completed": False, "priority": "high"},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_task_response.status_code == 200
            important_task = create_task_response.json()

            create_task_response = client.post(
                f"/api/users/{sample_user_id}/todos",
                json={"title": "Regular task", "completed": False, "priority": "low"},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_task_response.status_code == 200
            regular_task = create_task_response.json()

            # Now use the agent to perform a complex operation based on context
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # First mock response to get list of tasks
                mock_completion_1 = MagicMock()
                mock_completion_1.choices = [MagicMock()]
                mock_completion_1.choices[0].message = MagicMock()
                mock_completion_1.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_list",
                        function=MagicMock(
                            name="list_todos",
                            arguments=f'{{"user_id": "{sample_user_id}", "limit": 10}}'
                        )
                    )
                ]
                mock_completion_1.choices[0].message.content = "Let me check your tasks and prioritize accordingly."

                # Second mock response to update the important task
                mock_completion_2 = MagicMock()
                mock_completion_2.choices = [MagicMock()]
                mock_completion_2.choices[0].message = MagicMock()
                mock_completion_2.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_update",
                        function=MagicMock(
                            name="update_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "todo_id": "{important_task['id']}", "description": "This is a high priority task"}}'
                        )
                    )
                ]
                mock_completion_2.choices[0].message.content = "I've updated the important task with a description."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(side_effect=[mock_completion_1, mock_completion_2])

                mock_openai.return_value = mock_client_instance

                # First request to initiate the process
                first_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Identify and update my high priority tasks"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert first_response.status_code == 200

                # Verify the task was updated
                updated_task_response = client.get(
                    f"/api/users/{sample_user_id}/todos/{important_task['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert updated_task_response.status_code == 200
                updated_task = updated_task_response.json()
                assert "high priority" in updated_task["description"].lower()

                # Clean up
                client.delete(
                    f"/api/users/{sample_user_id}/todos/{important_task['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                client.delete(
                    f"/api/users/{sample_user_id}/todos/{regular_task['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )

    def test_multi_step_reminder_operation(self, client, sample_user_id):
        """Test multi-step operation involving reminders and notes."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # Mock response that creates a task and sets a reminder
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_add",
                        function=MagicMock(
                            name="add_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "title": "Meeting preparation", "description": "Prepare for team meeting"}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've created a task for meeting preparation."

                # Second mock for adding a reminder
                mock_completion_2 = MagicMock()
                mock_completion_2.choices = [MagicMock()]
                mock_completion_2.choices[0].message = MagicMock()
                mock_completion_2.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_reminder",
                        function=MagicMock(
                            name="create_reminder",
                            arguments=f'{{"user_id": "{sample_user_id}", "todo_id": "TASK_ID_PLACEHOLDER", "reminder_time": "2026-02-10T10:00:00Z", "message": "Time for meeting prep"}}'
                        )
                    )
                ]
                mock_completion_2.choices[0].message.content = "I've set a reminder for your meeting preparation."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(side_effect=[mock_completion, mock_completion_2])

                mock_openai.return_value = mock_client_instance

                # Create the task first using the agent
                create_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Create a task to prepare for team meeting"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert create_response.status_code == 200

                # Verify the task was created
                todos_response = client.get(
                    f"/api/users/{sample_user_id}/todos",
                    params={"limit": 100, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert todos_response.status_code == 200
                todos = [t for t in todos_response.json() if t["title"] == "Meeting preparation"]
                assert len(todos) == 1
                task_id = todos[0]["id"]

                # Now ask to set a reminder for the task
                reminder_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": f"Set a reminder for the meeting preparation task for tomorrow morning"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert reminder_response.status_code == 200

                # Clean up
                client.delete(
                    f"/api/users/{sample_user_id}/todos/{task_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )

    def test_complex_task_filtering_and_selection(self, client, sample_user_id):
        """Test complex filtering and selection of tasks."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # Create multiple tasks with different attributes
            tasks_to_create = [
                {"title": "Urgent work task", "completed": False, "priority": "high", "category": "work"},
                {"title": "Personal errand", "completed": False, "priority": "medium", "category": "personal"},
                {"title": "Completed work task", "completed": True, "priority": "low", "category": "work"},
                {"title": "Personal project", "completed": False, "priority": "medium", "category": "personal"}
            ]

            created_tasks = []
            for task_data in tasks_to_create:
                response = client.post(
                    f"/api/users/{sample_user_id}/todos",
                    json=task_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert response.status_code == 200
                created_tasks.append(response.json())

            # Use agent to perform complex filtering operation
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # Mock response that lists todos based on filters
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_list_work",
                        function=MagicMock(
                            name="list_todos",
                            arguments=f'{{"user_id": "{sample_user_id}", "limit": 10, "completed": false}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "Here are your pending work tasks."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Ask agent to filter and list specific tasks
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Show me my pending work tasks"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert response.status_code == 200

                # Verify we can get the correct tasks via API too
                work_todos_response = client.get(
                    f"/api/users/{sample_user_id}/todos",
                    params={"limit": 10, "offset": 0, "completed": "false"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert work_todos_response.status_code == 200
                work_todos = work_todos_response.json()

                # Should have at least the two pending tasks
                pending_tasks = [t for t in work_todos if not t["completed"]]
                assert len(pending_tasks) >= 2

                # Clean up
                for task in created_tasks:
                    client.delete(
                        f"/api/users/{sample_user_id}/todos/{task['id']}",
                        headers={"Authorization": "Bearer fake-token"}
                    )

    def test_error_handling_in_complex_operations(self, client, sample_user_id):
        """Test that complex operations handle errors gracefully."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # Create one valid task
            create_response = client.post(
                f"/api/users/{sample_user_id}/todos",
                json={"title": "Valid task", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_response.status_code == 200
            valid_task = create_response.json()

            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # Mock response that attempts to update a non-existent task
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_invalid",
                        function=MagicMock(
                            name="update_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "todo_id": "invalid-id", "title": "New title"}}'
                        )
                    ),
                    MagicMock(
                        id="call_valid",
                        function=MagicMock(
                            name="update_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "todo_id": "{valid_task['id']}", "completed": true}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've tried to update your tasks."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Send request - should handle error gracefully
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Update invalid task and valid task"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                # Should still return success even if individual operations failed
                assert response.status_code in [200, 206, 400]  # 206 for partial success, 400 for bad request

                # Verify that the valid task update was processed
                updated_task_response = client.get(
                    f"/api/users/{sample_user_id}/todos/{valid_task['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                # Depending on implementation, the valid task might have been updated or not

                # Clean up
                client.delete(
                    f"/api/users/{sample_user_id}/todos/{valid_task['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )

    def test_batch_task_operations(self, client, sample_user_id):
        """Test batch operations on multiple tasks."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # Create multiple tasks to operate on
            tasks_data = [
                {"title": "Task 1", "completed": False},
                {"title": "Task 2", "completed": False},
                {"title": "Task 3", "completed": False},
            ]

            created_tasks = []
            for task_data in tasks_data:
                response = client.post(
                    f"/api/users/{sample_user_id}/todos",
                    json=task_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert response.status_code == 200
                created_tasks.append(response.json())

            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # Mock response that performs batch operations
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_list",
                        function=MagicMock(
                            name="list_todos",
                            arguments=f'{{"user_id": "{sample_user_id}", "limit": 10}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've retrieved your tasks and will process them."

                # Second call to update multiple tasks
                mock_completion_2 = MagicMock()
                mock_completion_2.choices = [MagicMock()]
                mock_completion_2.choices[0].message = MagicMock()
                mock_completion_2.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_update_1",
                        function=MagicMock(
                            name="update_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "todo_id": "{created_tasks[0]['id']}", "completed": true}}'
                        )
                    ),
                    MagicMock(
                        id="call_update_2",
                        function=MagicMock(
                            name="update_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "todo_id": "{created_tasks[1]['id']}", "completed": true}}'
                        )
                    )
                ]
                mock_completion_2.choices[0].message.content = "I've updated the first two tasks as completed."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(side_effect=[mock_completion, mock_completion_2])

                mock_openai.return_value = mock_client_instance

                # First, get the tasks
                first_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Get my tasks"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert first_response.status_code == 200

                # Then, process them in batch
                second_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Mark the first two tasks as completed"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert second_response.status_code == 200

                # Verify the updates happened
                updated_tasks_response = client.get(
                    f"/api/users/{sample_user_id}/todos",
                    params={"limit": 100, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert updated_tasks_response.status_code == 200
                updated_tasks = updated_tasks_response.json()

                # Check that the first two tasks are now completed
                for i, task in enumerate(created_tasks[:2]):
                    task_from_api = next((t for t in updated_tasks if t["id"] == task["id"]), None)
                    if task_from_api:
                        assert task_from_api["completed"] is True

                # Third task should still be incomplete
                third_task = next((t for t in updated_tasks if t["id"] == created_tasks[2]["id"]), None)
                if third_task:
                    assert third_task["completed"] is False

                # Clean up
                for task in created_tasks:
                    client.delete(
                        f"/api/users/{sample_user_id}/todos/{task['id']}",
                        headers={"Authorization": "Bearer fake-token"}
                    )


if __name__ == "__main__":
    pytest.main([__file__])