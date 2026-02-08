"""
Test suite to verify that Phase II Todo functionality remains intact after AI agent integration.
Ensures backward compatibility and that existing features still work as expected.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid
from sqlmodel import Session
from backend.src.main import app
from backend.src.models.todo_model import TodoTask
from backend.services.todo_tools import TodoTools


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_user_id():
    """Provide a sample user ID for testing."""
    return str(uuid.uuid4())


class TestPhaseIIIntegrity:
    """Test cases to ensure Phase II functionality remains intact after agent integration."""

    def test_todo_crud_operations_still_work(self, client, sample_user_id):
        """Test that basic Todo CRUD operations still work after agent integration."""
        # Mock authentication to bypass auth requirements for this test
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # 1. Create a new todo (CREATE)
            create_response = client.post(
                f"/api/users/{sample_user_id}/todos",
                json={
                    "title": "Test task after agent integration",
                    "description": "This should still work after AI agent addition",
                    "completed": False
                },
                headers={"Authorization": "Bearer fake-token"}
            )

            assert create_response.status_code == 200
            create_data = create_response.json()
            assert "id" in create_data
            assert create_data["title"] == "Test task after agent integration"
            assert create_data["completed"] is False

            todo_id = create_data["id"]

            # 2. Retrieve the created todo (READ)
            get_response = client.get(
                f"/api/users/{sample_user_id}/todos/{todo_id}",
                headers={"Authorization": "Bearer fake-token"}
            )

            assert get_response.status_code == 200
            get_data = get_response.json()
            assert get_data["id"] == todo_id
            assert get_data["title"] == "Test task after agent integration"

            # 3. Update the todo (UPDATE)
            update_response = client.patch(
                f"/api/users/{sample_user_id}/todos/{todo_id}",
                json={"completed": True},
                headers={"Authorization": "Bearer fake-token"}
            )

            assert update_response.status_code == 200
            update_data = update_response.json()
            assert update_data["id"] == todo_id
            assert update_data["completed"] is True

            # 4. List all todos (READ ALL)
            list_response = client.get(
                f"/api/users/{sample_user_id}/todos",
                params={"limit": 10, "offset": 0},
                headers={"Authorization": "Bearer fake-token"}
            )

            assert list_response.status_code == 200
            list_data = list_response.json()
            assert isinstance(list_data, list)
            assert any(todo["id"] == todo_id for todo in list_data)

            # 5. Delete the todo (DELETE)
            delete_response = client.delete(
                f"/api/users/{sample_user_id}/todos/{todo_id}",
                headers={"Authorization": "Bearer fake-token"}
            )

            assert delete_response.status_code == 200
            assert delete_response.json()["success"] is True

    def test_todo_filtering_still_works(self, client, sample_user_id):
        """Test that todo filtering functionality still works."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # Create multiple todos with different completion statuses
            todos_to_create = [
                {"title": "Completed task", "completed": True},
                {"title": "Pending task", "completed": False},
                {"title": "Another completed task", "completed": True}
            ]

            created_todos = []
            for todo_data in todos_to_create:
                response = client.post(
                    f"/api/users/{sample_user_id}/todos",
                    json=todo_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert response.status_code == 200
                created_todos.append(response.json())

            # Test filtering for completed todos
            completed_response = client.get(
                f"/api/users/{sample_user_id}/todos",
                params={"completed": "true", "limit": 10, "offset": 0},
                headers={"Authorization": "Bearer fake-token"}
            )

            assert completed_response.status_code == 200
            completed_todos = completed_response.json()
            assert len(completed_todos) == 2  # Should have 2 completed todos
            assert all(todo["completed"] is True for todo in completed_todos)

            # Test filtering for pending todos
            pending_response = client.get(
                f"/api/users/{sample_user_id}/todos",
                params={"completed": "false", "limit": 10, "offset": 0},
                headers={"Authorization": "Bearer fake-token"}
            )

            assert pending_response.status_code == 200
            pending_todos = pending_response.json()
            assert len(pending_todos) == 1  # Should have 1 pending todo
            assert all(todo["completed"] is False for todo in pending_todos)

            # Clean up created todos
            for todo in created_todos:
                client.delete(
                    f"/api/users/{sample_user_id}/todos/{todo['id']}",
                    headers={"Authorization": "Bearer fake-token"}
                )

    def test_user_isolation_still_enforced(self, client, sample_user_id):
        """Test that user isolation is still properly enforced after agent integration."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            # Authenticate as the original user
            mock_auth.return_value = sample_user_id

            # Create a todo as the original user
            create_response = client.post(
                f"/api/users/{sample_user_id}/todos",
                json={"title": "Original user's task", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )

            assert create_response.status_code == 200
            created_todo = create_response.json()
            original_todo_id = created_todo["id"]

            # Try to access as a different user - should fail with auth mock manipulation
            different_user_id = str(uuid.uuid4())
            mock_auth.return_value = different_user_id

            # Attempt to access the original user's todo with different user ID in URL
            # This should fail due to authorization checks
            get_response = client.get(
                f"/api/users/{sample_user_id}/todos/{original_todo_id}",
                headers={"Authorization": "Bearer fake-token"}
            )

            # Should fail with 403 Forbidden or 404 Not Found depending on implementation
            assert get_response.status_code in [403, 404]

            # Clean up as original user
            mock_auth.return_value = sample_user_id
            client.delete(
                f"/api/users/{sample_user_id}/todos/{original_todo_id}",
                headers={"Authorization": "Bearer fake-token"}
            )

    def test_todo_service_layer_still_works(self, sample_user_id):
        """Test that the TodoService layer still works correctly after agent integration."""
        from backend.src.services.todo_service import TodoService
        from backend.database import get_session

        # Create a real session for testing
        with next(get_session()) as session:
            todo_service = TodoService(session)

            # Test creating a todo
            created_todo = todo_service.create_task(
                user_id=sample_user_id,
                title="Service layer test task",
                description="Testing service layer after agent integration"
            )

            assert created_todo is not None
            assert created_todo.user_id == sample_user_id
            assert created_todo.title == "Service layer test task"

            # Test retrieving the todo
            retrieved_todo = todo_service.get_task_by_id(
                task_id=created_todo.id,
                user_id=sample_user_id
            )

            assert retrieved_todo is not None
            assert retrieved_todo.id == created_todo.id

            # Test updating the todo
            updated_todo = todo_service.update_task(
                task_id=created_todo.id,
                user_id=sample_user_id,
                title="Updated service layer test task",
                completed=True
            )

            assert updated_todo is not None
            assert updated_todo.title == "Updated service layer test task"
            assert updated_todo.completed is True

            # Test listing todos
            todos_list = todo_service.get_user_tasks(
                user_id=sample_user_id,
                limit=10,
                offset=0
            )

            assert isinstance(todos_list, list)
            assert any(todo.id == created_todo.id for todo in todos_list)

            # Test deleting the todo
            deletion_result = todo_service.delete_task(
                task_id=created_todo.id,
                user_id=sample_user_id
            )

            assert deletion_result is True

    def test_todo_models_still_intact(self, sample_user_id):
        """Test that TodoTask model and its functionality remain intact."""
        from backend.src.models.todo_model import TodoTask

        # Test creating a model instance
        todo = TodoTask(
            user_id=sample_user_id,
            title="Model integrity test",
            description="Testing that the model still works properly"
        )

        assert todo.user_id == sample_user_id
        assert todo.title == "Model integrity test"
        assert todo.description == "Testing that the model still works properly"
        assert todo.completed is False  # Default value

        # Test that all expected fields exist
        expected_fields = ['id', 'user_id', 'title', 'description', 'completed', 'category', 'priority', 'due_date', 'created_at', 'updated_at']
        todo_dict = todo.dict() if hasattr(todo, 'dict') else todo.__dict__

        for field in expected_fields:
            assert field in dir(todo) or field in todo_dict

    def test_agent_integration_doesnt_break_existing_routes(self, client, sample_user_id):
        """Test that agent integration doesn't interfere with existing API routes."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # Test basic route that existed before agent integration
            user_profile_response = client.get(
                f"/api/users/{sample_user_id}",
                headers={"Authorization": "Bearer fake-token"}
            )

            # This might return 404 if user doesn't exist, but shouldn't return server error
            assert user_profile_response.status_code in [200, 404, 400]

            # Test creating and getting a todo still works
            create_response = client.post(
                f"/api/users/{sample_user_id}/todos",
                json={"title": "Agent integration test", "completed": False},
                headers={"Authorization": "Bearer fake-token"}
            )

            assert create_response.status_code == 200
            created_data = create_response.json()
            todo_id = created_data["id"]

            get_response = client.get(
                f"/api/users/{sample_user_id}/todos/{todo_id}",
                headers={"Authorization": "Bearer fake-token"}
            )

            assert get_response.status_code == 200
            get_data = get_response.json()
            assert get_data["id"] == todo_id

            # Clean up
            client.delete(
                f"/api/users/{sample_user_id}/todos/{todo_id}",
                headers={"Authorization": "Bearer fake-token"}
            )

    def test_concurrent_access_still_safe(self, client, sample_user_id):
        """Test that concurrent access to todo functionality is still safe after agent integration."""
        import threading
        import time

        results = []

        def create_todo(title):
            with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
                mock_auth.return_value = sample_user_id

                response = client.post(
                    f"/api/users/{sample_user_id}/todos",
                    json={"title": title, "completed": False},
                    headers={"Authorization": "Bearer fake-token"}
                )
                results.append((title, response.status_code, response.json() if response.status_code == 200 else None))

        # Create multiple threads trying to create todos simultaneously
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_todo, args=[f"Concurrent task {i}"])
            threads.append(thread)
            thread.start()
            time.sleep(0.01)  # Small delay to ensure they overlap

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify that all operations succeeded
        for title, status_code, data in results:
            assert status_code == 200, f"Thread operation for {title} failed with status {status_code}"

        # Clean up created todos
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            all_todos = client.get(
                f"/api/users/{sample_user_id}/todos",
                params={"limit": 10, "offset": 0},
                headers={"Authorization": "Bearer fake-token"}
            ).json()

            for todo in all_todos:
                if "Concurrent task" in todo.get("title", ""):
                    client.delete(
                        f"/api/users/{sample_user_id}/todos/{todo['id']}",
                        headers={"Authorization": "Bearer fake-token"}
                    )


if __name__ == "__main__":
    pytest.main([__file__])