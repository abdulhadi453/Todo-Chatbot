"""
End-to-End test suite for the complete AI agent workflow.
Tests the complete flow: natural language → tool calls → todo updates → UI reflection.
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


class TestE2EAgentWorkflow:
    """End-to-end tests for the complete AI agent workflow."""

    def test_natural_language_to_todo_creation_flow(self, client, sample_user_id):
        """Test the complete flow: natural language "Add grocery list" → tool call → todo created → UI reflects change."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # Mock OpenAI to simulate the agent's behavior
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # Mock the OpenAI response that would include a tool call to add_todo
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_123",
                        function=MagicMock(
                            name="add_todo",
                            arguments='{"user_id": "' + sample_user_id + '", "title": "Buy groceries", "description": "Need to buy milk, bread, and eggs"}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've added a task to buy groceries to your list."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Send natural language request to the agent endpoint
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "I need to remember to buy groceries"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert "response" in data
                assert "Buy groceries" in data["response"] or "groceries" in data["response"].lower()

                # Verify that the todo was created by checking the user's todos
                todos_response = client.get(
                    f"/api/users/{sample_user_id}/todos",
                    params={"limit": 10, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert todos_response.status_code == 200
                todos = todos_response.json()

                # Find the grocery task
                grocery_task = None
                for todo in todos:
                    if "groceries" in todo["title"].lower() or "buy groceries" in todo["title"].lower():
                        grocery_task = todo
                        break

                assert grocery_task is not None, f"Expected to find grocery task in todos: {todos}"
                assert grocery_task["title"] == "Buy groceries"
                assert "milk, bread, and eggs" in grocery_task["description"]

                # Clean up: delete the created todo
                if grocery_task:
                    client.delete(
                        f"/api/users/{sample_user_id}/todos/{grocery_task['id']}",
                        headers={"Authorization": "Bearer fake-token"}
                    )

    def test_natural_language_to_todo_update_flow(self, client, sample_user_id):
        """Test the flow: natural language "Mark task as complete" → tool call → todo updated → UI reflects change."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # First, create a todo manually
            create_response = client.post(
                f"/api/users/{sample_user_id}/todos",
                json={"title": "Grocery shopping", "description": "Still need to do this", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_response.status_code == 200
            created_todo = create_response.json()
            todo_id = created_todo["id"]

            # Mock OpenAI to simulate the agent's behavior for updating the task
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # Mock the OpenAI response that would include a tool call to update_todo
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_456",
                        function=MagicMock(
                            name="update_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "todo_id": "{todo_id}", "completed": true}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've marked the grocery shopping task as completed."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Send natural language request to the agent endpoint
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": f"Please mark the task '{created_todo['title']}' as complete"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert "response" in data
                assert "marked" in data["response"].lower() or "completed" in data["response"].lower()

                # Verify that the todo was updated by checking the user's todos
                updated_todo_response = client.get(
                    f"/api/users/{sample_user_id}/todos/{todo_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert updated_todo_response.status_code == 200
                updated_todo = updated_todo_response.json()
                assert updated_todo["id"] == todo_id
                assert updated_todo["completed"] is True

                # Clean up: delete the updated todo
                client.delete(
                    f"/api/users/{sample_user_id}/todos/{todo_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )

    def test_natural_language_to_todo_deletion_flow(self, client, sample_user_id):
        """Test the flow: natural language "Delete task" → tool call → todo deleted → UI reflects change."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # First, create a todo manually
            create_response = client.post(
                f"/api/users/{sample_user_id}/todos",
                json={"title": "Old task to delete", "description": "This should be removed", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_response.status_code == 200
            created_todo = create_response.json()
            todo_id = created_todo["id"]

            # Verify the todo exists
            verify_create_response = client.get(
                f"/api/users/{sample_user_id}/todos/{todo_id}",
                headers={"Authorization": "Bearer fake-token"}
            )
            assert verify_create_response.status_code == 200

            # Mock OpenAI to simulate the agent's behavior for deleting the task
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # Mock the OpenAI response that would include a tool call to delete_todo
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_789",
                        function=MagicMock(
                            name="delete_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "todo_id": "{todo_id}"}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = f"I've deleted the task '{created_todo['title']}' for you."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Send natural language request to the agent endpoint
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": f"Please delete the task '{created_todo['title']}'"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert "response" in data
                assert "deleted" in data["response"].lower()

                # Verify that the todo was deleted by trying to access it (should fail)
                deleted_todo_response = client.get(
                    f"/api/users/{sample_user_id}/todos/{todo_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )

                # This should return 404 since the todo was deleted
                assert deleted_todo_response.status_code in [404, 400]

    def test_conversation_history_preserved_through_tool_calls(self, client, sample_user_id):
        """Test that conversation history is preserved when tool calls are executed."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # Mock OpenAI to simulate multiple interactions
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # First interaction - add a todo
                mock_completion_1 = MagicMock()
                mock_completion_1.choices = [MagicMock()]
                mock_completion_1.choices[0].message = MagicMock()
                mock_completion_1.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_abc",
                        function=MagicMock(
                            name="add_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "title": "First task", "description": "Initial task"}}'
                        )
                    )
                ]
                mock_completion_1.choices[0].message.content = "I've added your first task."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(side_effect=[mock_completion_1, mock_completion_1])

                mock_openai.return_value = mock_client_instance

                # First request: add a task
                response1 = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Add a task called 'First task'"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert response1.status_code == 200
                data1 = response1.json()
                conversation_id = data1["conversation_id"]

                # Second request in the same conversation
                response2 = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={
                        "message": "What did I ask you to do in our first message?",
                        "conversation_id": conversation_id
                    },
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert response2.status_code == 200
                data2 = response2.json()

                # The agent should have access to conversation history
                # While we can't verify the exact history in this test without mocking more deeply,
                # we can verify that both requests worked and a conversation ID was maintained
                assert "response" in data2
                assert conversation_id == data2["conversation_id"]

                # Clean up: get and delete the created task
                todos_response = client.get(
                    f"/api/users/{sample_user_id}/todos",
                    params={"limit": 10, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )
                if todos_response.status_code == 200:
                    todos = todos_response.json()
                    for todo in todos:
                        if todo["title"] == "First task":
                            client.delete(
                                f"/api/users/{sample_user_id}/todos/{todo['id']}",
                                headers={"Authorization": "Bearer fake-token"}
                            )
                            break

    def test_agent_handles_multiple_tool_calls_in_single_request(self, client, sample_user_id):
        """Test that the agent can handle multiple tool calls in a single request."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # First, create a couple of todos
            todo1_response = client.post(
                f"/api/users/{sample_user_id}/todos",
                json={"title": "Task A", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert todo1_response.status_code == 200
            todo1 = todo1_response.json()

            todo2_response = client.post(
                f"/api/users/{sample_user_id}/todos",
                json={"title": "Task B", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert todo2_response.status_code == 200
            todo2 = todo2_response.json()

            # Mock OpenAI to return multiple tool calls (list_todos followed by update_todo)
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
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
                    ),
                    MagicMock(
                        id="call_update",
                        function=MagicMock(
                            name="update_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "todo_id": "{todo1['id']}", "completed": true}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've reviewed your tasks and completed the first one."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Send a request that should trigger multiple tool calls
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Check my tasks and complete the first one on the list"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert "response" in data

                # Verify that the first task was marked as completed
                updated_todo_response = client.get(
                    f"/api/users/{sample_user_id}/todos/{todo1['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert updated_todo_response.status_code == 200
                updated_todo = updated_todo_response.json()
                assert updated_todo["completed"] is True

                # Verify that the second task was not affected
                todo2_check_response = client.get(
                    f"/api/users/{sample_user_id}/todos/{todo2['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert todo2_check_response.status_code == 200
                todo2_check = todo2_check_response.json()
                assert todo2_check["completed"] is False  # Should still be false

                # Clean up: delete the created todos
                client.delete(
                    f"/api/users/{sample_user_id}/todos/{todo1['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                client.delete(
                    f"/api/users/{sample_user_id}/todos/{todo2['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )

    def test_ui_reflection_happens_immediately_after_agent_action(self, client, sample_user_id):
        """Test that UI updates reflect agent actions immediately."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # Mock OpenAI to simulate the agent creating a todo
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_create",
                        function=MagicMock(
                            name="add_todo",
                            arguments=f'{{"user_id": "{sample_user_id}", "title": "Immediate reflection test", "description": "This should appear immediately in the UI"}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've created the task for you."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Store the initial todo count
                initial_todos_response = client.get(
                    f"/api/users/{sample_user_id}/todos",
                    params={"limit": 100, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )
                initial_count = len(initial_todos_response.json()) if initial_todos_response.status_code == 200 else 0

                # Send the request to the agent
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Create a new task called 'Immediate reflection test'"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200

                # Immediately check that the todo count increased
                updated_todos_response = client.get(
                    f"/api/users/{sample_user_id}/todos",
                    params={"limit": 100, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )
                updated_count = len(updated_todos_response.json()) if updated_todos_response.status_code == 200 else 0

                # The count should have increased by 1
                assert updated_count == initial_count + 1

                # Find and verify the specific task exists
                all_todos = updated_todos_response.json()
                created_task = None
                for todo in all_todos:
                    if todo["title"] == "Immediate reflection test":
                        created_task = todo
                        break

                assert created_task is not None
                assert created_task["description"] == "This should appear immediately in the UI"

                # Clean up: delete the created task
                if created_task:
                    client.delete(
                        f"/api/users/{sample_user_id}/todos/{created_task['id']}",
                        headers={"Authorization": "Bearer fake-token"}
                    )


if __name__ == "__main__":
    pytest.main([__file__])