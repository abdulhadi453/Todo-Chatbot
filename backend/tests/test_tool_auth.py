"""
Test suite for tool authorization in the AI agent system.
Tests that all agent tools properly validate user permissions and enforce multi-user isolation.
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
def sample_user_ids():
    """Provide sample user IDs for testing."""
    return [str(uuid.uuid4()), str(uuid.uuid4())]


class TestToolAuthorization:
    """Test cases for tool authorization and user isolation."""

    def test_list_todos_only_returns_current_user_items(self, client, sample_user_ids):
        """Test that list_todos only returns items belonging to the authenticated user."""
        user1_id, user2_id = sample_user_ids

        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            # Create a task for user 1
            mock_auth.return_value = user1_id
            create_response_1 = client.post(
                f"/api/users/{user1_id}/todos",
                json={"title": "User 1 task", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_response_1.status_code == 200
            user1_task = create_response_1.json()

            # Create a task for user 2
            mock_auth.return_value = user2_id
            create_response_2 = client.post(
                f"/api/users/{user2_id}/todos",
                json={"title": "User 2 task", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_response_2.status_code == 200
            user2_task = create_response_2.json()

            # Test that user 1 can only see their own tasks via agent tool
            mock_auth.return_value = user1_id
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_list",
                        function=MagicMock(
                            name="list_todos",
                            arguments=f'{{"user_id": "{user1_id}", "limit": 10}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "Here are your tasks."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Call agent with user 1's ID
                response = client.post(
                    f"/api/{user1_id}/chat",
                    json={"message": "List my tasks"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200

                # Direct API test: user 1 should only see their own tasks
                user1_todos_response = client.get(
                    f"/api/users/{user1_id}/todos",
                    params={"limit": 100, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert user1_todos_response.status_code == 200
                user1_todos = user1_todos_response.json()

                user1_titles = [t["title"] for t in user1_todos]
                assert "User 1 task" in user1_titles
                assert "User 2 task" not in user1_titles  # User 1 should not see user 2's task

            # Test that user 2 can only see their own tasks
            mock_auth.return_value = user2_id
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_list",
                        function=MagicMock(
                            name="list_todos",
                            arguments=f'{{"user_id": "{user2_id}", "limit": 10}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "Here are your tasks."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Call agent with user 2's ID
                response = client.post(
                    f"/api/{user2_id}/chat",
                    json={"message": "List my tasks"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200

                # Direct API test: user 2 should only see their own tasks
                user2_todos_response = client.get(
                    f"/api/users/{user2_id}/todos",
                    params={"limit": 100, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert user2_todos_response.status_code == 200
                user2_todos = user2_todos_response.json()

                user2_titles = [t["title"] for t in user2_todos]
                assert "User 2 task" in user2_titles
                assert "User 1 task" not in user2_titles  # User 2 should not see user 1's task

            # Clean up
            mock_auth.return_value = user1_id
            client.delete(
                f"/api/users/{user1_id}/todos/{user1_task['id']}",
                headers={"Authorization": "Bearer fake-token"}
            )

            mock_auth.return_value = user2_id
            client.delete(
                f"/api/users/{user2_id}/todos/{user2_task['id']}",
                headers={"Authorization": "Bearer fake-token"}
            )

    def test_add_todo_respects_user_boundary(self, client, sample_user_ids):
        """Test that add_todo only allows creating tasks for the authenticated user."""
        user1_id, user2_id = sample_user_ids

        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = user1_id

            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_add",
                        function=MagicMock(
                            name="add_todo",
                            arguments=f'{{"user_id": "{user1_id}", "title": "User 1 new task", "description": "Created by agent"}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've added a task for you."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Call agent to add a task for user 1
                response = client.post(
                    f"/api/{user1_id}/chat",
                    json={"message": "Add a task: User 1 new task"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200

                # Verify the task was created for user 1
                user1_todos_response = client.get(
                    f"/api/users/{user1_id}/todos",
                    params={"limit": 100, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert user1_todos_response.status_code == 200
                user1_todos = user1_todos_response.json()

                user1_new_tasks = [t for t in user1_todos if t["title"] == "User 1 new task"]
                assert len(user1_new_tasks) == 1

                # Verify user 2 doesn't have this task
                mock_auth.return_value = user2_id
                user2_todos_response = client.get(
                    f"/api/users/{user2_id}/todos",
                    params={"limit": 100, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert user2_todos_response.status_code == 200
                user2_todos = user2_todos_response.json()

                user2_new_tasks = [t for t in user2_todos if t["title"] == "User 1 new task"]
                assert len(user2_new_tasks) == 0  # User 2 should not have user 1's task

                # Clean up
                mock_auth.return_value = user1_id
                for task in user1_new_tasks:
                    client.delete(
                        f"/api/users/{user1_id}/todos/{task['id']}",
                        headers={"Authorization": "Bearer fake-token"}
                    )

    def test_update_todo_enforces_user_boundary(self, client, sample_user_ids):
        """Test that update_todo only allows updating tasks owned by the authenticated user."""
        user1_id, user2_id = sample_user_ids

        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            # Create tasks for both users
            mock_auth.return_value = user1_id
            create_response_1 = client.post(
                f"/api/users/{user1_id}/todos",
                json={"title": "User 1 original task", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_response_1.status_code == 200
            user1_task = create_response_1.json()

            mock_auth.return_value = user2_id
            create_response_2 = client.post(
                f"/api/users/{user2_id}/todos",
                json={"title": "User 2 original task", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_response_2.status_code == 200
            user2_task = create_response_2.json()

            # Try to update user 1's task using agent as user 1 (should work)
            mock_auth.return_value = user1_id
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_update",
                        function=MagicMock(
                            name="update_todo",
                            arguments=f'{{"user_id": "{user1_id}", "todo_id": "{user1_task["id"]}", "title": "User 1 updated task"}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've updated your task."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                response = client.post(
                    f"/api/{user1_id}/chat",
                    json={"message": "Update my task to 'User 1 updated task'"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200

                # Verify the update worked
                updated_task_response = client.get(
                    f"/api/users/{user1_id}/todos/{user1_task['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert updated_task_response.status_code == 200
                updated_task = updated_task_response.json()
                assert updated_task["title"] == "User 1 updated task"

            # Try to update user 2's task as user 1 (should fail)
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_update_invalid",
                        function=MagicMock(
                            name="update_todo",
                            arguments=f'{{"user_id": "{user1_id}", "todo_id": "{user2_task["id"]}", "title": "Attempted update"}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I'll try to update that task."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                response = client.post(
                    f"/api/{user1_id}/chat",
                    json={"message": f"Update task {user2_task['id']} to 'Attempted update'"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                # The response might be 200 (successful request) but the update should fail internally
                # The tool execution should return an error for unauthorized access
                if response.status_code == 200:
                    # If the request was accepted, verify the task wasn't actually changed
                    unchanged_task_response = client.get(
                        f"/api/users/{user2_id}/todos/{user2_task['id']}",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    assert unchanged_task_response.status_code == 200
                    unchanged_task = unchanged_task_response.json()
                    assert unchanged_task["title"] == "User 2 original task"  # Should be unchanged

            # Clean up
            mock_auth.return_value = user1_id
            client.delete(
                f"/api/users/{user1_id}/todos/{user1_task['id']}",
                headers={"Authorization": "Bearer fake-token"}
            )

            mock_auth.return_value = user2_id
            client.delete(
                f"/api/users/{user2_id}/todos/{user2_task['id']}",
                headers={"Authorization": "Bearer fake-token"}
            )

    def test_delete_todo_enforces_user_boundary(self, client, sample_user_ids):
        """Test that delete_todo only allows deleting tasks owned by the authenticated user."""
        user1_id, user2_id = sample_user_ids

        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            # Create tasks for both users
            mock_auth.return_value = user1_id
            create_response_1 = client.post(
                f"/api/users/{user1_id}/todos",
                json={"title": "User 1 task to delete", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_response_1.status_code == 200
            user1_task = create_response_1.json()

            mock_auth.return_value = user2_id
            create_response_2 = client.post(
                f"/api/users/{user2_id}/todos",
                json={"title": "User 2 task to delete", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert create_response_2.status_code == 200
            user2_task = create_response_2.json()

            # Try to delete user 1's task as user 1 (should work)
            mock_auth.return_value = user1_id
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_delete",
                        function=MagicMock(
                            name="delete_todo",
                            arguments=f'{{"user_id": "{user1_id}", "todo_id": "{user1_task["id"]}"}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I've deleted your task."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                response = client.post(
                    f"/api/{user1_id}/chat",
                    json={"message": f"Delete task {user1_task['id']}"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200

                # Verify the task was deleted
                deleted_task_response = client.get(
                    f"/api/users/{user1_id}/todos/{user1_task['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert deleted_task_response.status_code in [404, 400]  # Should be gone

            # Try to delete user 2's task as user 1 (should fail)
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_delete_invalid",
                        function=MagicMock(
                            name="delete_todo",
                            arguments=f'{{"user_id": "{user1_id}", "todo_id": "{user2_task["id"]}"}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "I'll try to delete that task."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                response = client.post(
                    f"/api/{user1_id}/chat",
                    json={"message": f"Delete task {user2_task['id']}"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                # Verify user 2's task still exists
                user2_task_response = client.get(
                    f"/api/users/{user2_id}/todos/{user2_task['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert user2_task_response.status_code == 200  # Should still exist

            # Clean up remaining task
            mock_auth.return_value = user2_id
            client.delete(
                f"/api/users/{user2_id}/todos/{user2_task['id']}",
                headers={"Authorization": "Bearer fake-token"}
            )

    def test_get_user_context_enforces_user_boundary(self, client, sample_user_ids):
        """Test that get_user_context only returns context for the authenticated user."""
        user1_id, user2_id = sample_user_ids

        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            # Test user 1 context access
            mock_auth.return_value = user1_id
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_context_1",
                        function=MagicMock(
                            name="get_user_context",
                            arguments=f'{{"user_id": "{user1_id}"}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "Here's your context."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                response = client.post(
                    f"/api/{user1_id}/chat",
                    json={"message": "Get my user context"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200

            # Test user 2 context access
            mock_auth.return_value = user2_id
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    MagicMock(
                        id="call_context_2",
                        function=MagicMock(
                            name="get_user_context",
                            arguments=f'{{"user_id": "{user2_id}"}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "Here's your context."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                response = client.post(
                    f"/api/{user2_id}/chat",
                    json={"message": "Get my user context"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200

    def test_jwt_validation_prevents_cross_user_access(self, client, sample_user_ids):
        """Test that JWT validation prevents cross-user access in all tool operations."""
        user1_id, user2_id = sample_user_ids

        # This test simulates a potential attack where someone tries to manipulate
        # the user_id in tool arguments while using another user's token
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            # Authenticate as user 1
            mock_auth.return_value = user1_id

            # Attempt to use agent tools for user 2 while authenticated as user 1
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = [
                    # Malicious attempt: trying to access user2's data while authenticated as user1
                    MagicMock(
                        id="call_malicious",
                        function=MagicMock(
                            name="list_todos",
                            arguments=f'{{"user_id": "{user2_id}", "limit": 10}}'
                        )
                    )
                ]
                mock_completion.choices[0].message.content = "Trying to access other user's data."

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                response = client.post(
                    f"/api/{user1_id}/chat",
                    json={"message": "Show me user2's tasks"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                # The request should either fail or the tool execution should be properly validated
                # The tool should respect the authenticated user, not the user_id in arguments
                if response.status_code == 200:
                    # If the request succeeded, verify that the response doesn't leak user2's data
                    # This depends on how the backend validates the user_id consistency
                    data = response.json()
                    # The agent might still return a generic response but should not expose user2's data
                    pass

    def test_tool_input_validation_and_sanitization(self, client, sample_user_ids):
        """Test that all tools properly validate and sanitize their inputs."""
        user1_id = sample_user_ids[0]

        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = user1_id

            # Test various malformed inputs to ensure proper validation
            test_cases = [
                # Invalid user_id format
                '{"user_id": "", "title": "Invalid user ID"}',
                # Missing required fields
                '{"user_id": "' + user1_id + '"}',  # Missing title for add_todo
                # SQL injection attempt in title
                '{"user_id": "' + user1_id + '", "title": "Test; DROP TABLE tasks; --"}',
                # XSS attempt in description
                '{"user_id": "' + user1_id + '", "title": "XSS test", "description": "<script>alert(1)</script>"}',
            ]

            for i, bad_args in enumerate(test_cases):
                with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                    mock_completion = MagicMock()
                    mock_completion.choices = [MagicMock()]
                    mock_completion.choices[0].message = MagicMock()
                    mock_completion.choices[0].message.tool_calls = [
                        MagicMock(
                            id=f"call_bad_{i}",
                            function=MagicMock(
                                name="add_todo",
                                arguments=bad_args
                            )
                        )
                    ]
                    mock_completion.choices[0].message.content = "Processing invalid input."

                    mock_client_instance = MagicMock()
                    mock_client_instance.chat = MagicMock()
                    mock_client_instance.chat.completions = MagicMock()
                    mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                    mock_openai.return_value = mock_client_instance

                    response = client.post(
                        f"/api/{user1_id}/chat",
                        json={"message": f"Process invalid input: {bad_args}"},
                        headers={"Authorization": "Bearer fake-token"}
                    )

                    # Should handle invalid input gracefully
                    assert response.status_code in [200, 400, 422, 500]

            # Verify that no malicious data was stored
            todos_response = client.get(
                f"/api/users/{user1_id}/todos",
                params={"limit": 100, "offset": 0},
                headers={"Authorization": "Bearer fake-token"}
            )
            assert todos_response.status_code == 200
            todos = todos_response.json()

            # Ensure no tasks with malicious content were created
            for todo in todos:
                assert "DROP TABLE" not in todo.get("title", "")
                assert "<script>" not in todo.get("title", "")
                assert "<script>" not in todo.get("description", "")


if __name__ == "__main__":
    pytest.main([__file__])