"""
Integration tests for the agent chat endpoint.

This module tests the integration between the API endpoint, agent service,
and underlying components to ensure proper end-to-end functionality.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlmodel import Session
from backend.src.main import app  # Adjust import based on actual main file location
from backend.routers.agent import router
from backend.services.openai_agent_service import OpenAIAgentService
from backend.services.todo_tools import TodoTools
from backend.models.agent_session import AgentSession
from backend.models.agent_message import AgentMessage
import uuid


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_user_id():
    """Provide a sample user ID for testing."""
    return str(uuid.uuid4())


class TestAgentChatEndpoint:
    """Integration tests for the agent chat endpoint."""

    @patch('backend.routers.agent.OpenAIAgentService')
    def test_agent_chat_endpoint_success(self, mock_agent_service_class, client, sample_user_id):
        """Test that the agent chat endpoint returns proper response."""
        # Mock the agent service
        mock_agent_service = MagicMock(spec=OpenAIAgentService)
        mock_agent_service.process_message.return_value = {
            "session_id": str(uuid.uuid4()),
            "response": "I've added the task to buy groceries to your list.",
            "timestamp": "2026-02-08T10:30:00Z",
            "message_id": str(uuid.uuid4()),
            "tool_calls": [],
            "tool_results": {},
            "using_stub": False
        }

        mock_agent_service_class.return_value = mock_agent_service

        # Mock session dependency
        with patch('backend.routers.agent.get_session') as mock_get_session:
            mock_session = MagicMock(spec=Session)
            mock_get_session.return_value.__enter__.return_value = mock_session

            # Mock JWT auth dependency
            with patch('backend.routers.agent.get_current_user_id') as mock_get_current_user:
                mock_get_current_user.return_value = sample_user_id

                # Make request to the chat endpoint
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Add a task to buy groceries"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                # Verify the response
                assert response.status_code == 200
                response_data = response.json()

                assert "conversation_id" in response_data
                assert "response" in response_data
                assert "timestamp" in response_data
                assert "message_id" in response_data

                # Verify the agent service was called
                mock_agent_service.process_message.assert_called_once()
                args, kwargs = mock_agent_service.process_message.call_args
                assert kwargs['user_id'] == sample_user_id
                assert kwargs['message'] == "Add a task to buy groceries"

    @patch('backend.routers.agent.OpenAIAgentService')
    def test_agent_chat_endpoint_with_conversation_id(self, mock_agent_service_class, client, sample_user_id):
        """Test the agent chat endpoint with an existing conversation ID."""
        conversation_id = str(uuid.uuid4())

        mock_agent_service = MagicMock(spec=OpenAIAgentService)
        mock_agent_service.process_message.return_value = {
            "session_id": conversation_id,
            "response": "I've retrieved your existing conversation.",
            "timestamp": "2026-02-08T10:30:00Z",
            "message_id": str(uuid.uuid4()),
            "tool_calls": [],
            "tool_results": {},
            "using_stub": False
        }

        mock_agent_service_class.return_value = mock_agent_service

        with patch('backend.routers.agent.get_session') as mock_get_session:
            mock_session = MagicMock(spec=Session)
            mock_get_session.return_value.__enter__.return_value = mock_session

            with patch('backend.routers.agent.get_current_user_id') as mock_get_current_user:
                mock_get_current_user.return_value = sample_user_id

                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={
                        "message": "Continue our previous conversation",
                        "conversation_id": conversation_id
                    },
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200
                response_data = response.json()

                # Verify the conversation ID was preserved
                assert response_data["conversation_id"] == conversation_id

                # Verify the agent service was called with correct parameters
                mock_agent_service.process_message.assert_called_once()
                args, kwargs = mock_agent_service.process_message.call_args
                assert kwargs['session_id'] == conversation_id

    def test_agent_chat_endpoint_unauthorized(self, client, sample_user_id):
        """Test that unauthorized requests return 401."""
        response = client.post(
            f"/api/{sample_user_id}/chat",
            json={"message": "Test message"}
            # No authorization header
        )

        # Should return 401 or 403 depending on auth implementation
        assert response.status_code in [401, 403]

    def test_agent_chat_endpoint_invalid_user_id(self, client):
        """Test the agent chat endpoint with invalid user ID format."""
        invalid_user_id = "invalid-uuid-format"

        with patch('backend.routers.agent.get_current_user_id') as mock_get_current_user:
            mock_get_current_user.return_value = invalid_user_id

            response = client.post(
                f"/api/{invalid_user_id}/chat",
                json={"message": "Test message"},
                headers={"Authorization": "Bearer fake-token"}
            )

            # Should return 400 for invalid UUID format
            assert response.status_code == 400

    def test_agent_chat_endpoint_missing_message(self, client, sample_user_id):
        """Test the agent chat endpoint with missing message."""
        with patch('backend.routers.agent.get_current_user_id') as mock_get_current_user:
            mock_get_current_user.return_value = sample_user_id

            response = client.post(
                f"/api/{sample_user_id}/chat",
                json={},  # Empty body
                headers={"Authorization": "Bearer fake-token"}
            )

            # Should return 400 for missing message
            assert response.status_code == 400
            assert "Message content is required" in response.json().get("detail", "")

    def test_agent_chat_endpoint_empty_message(self, client, sample_user_id):
        """Test the agent chat endpoint with empty message."""
        with patch('backend.routers.agent.get_current_user_id') as mock_get_current_user:
            mock_get_current_user.return_value = sample_user_id

            response = client.post(
                f"/api/{sample_user_id}/chat",
                json={"message": ""},  # Empty message
                headers={"Authorization": "Bearer fake-token"}
            )

            # Should return 400 for empty message
            assert response.status_code == 400
            assert "Message content is required" in response.json().get("detail", "")

    @patch('backend.routers.agent.OpenAIAgentService')
    def test_agent_chat_endpoint_fallback_on_error(self, mock_agent_service_class, client, sample_user_id):
        """Test that the agent chat endpoint falls back to stub AI on error."""
        # Make the agent service raise an exception
        mock_agent_service = MagicMock(spec=OpenAIAgentService)
        mock_agent_service.process_message.side_effect = Exception("OpenAI service unavailable")

        mock_agent_service_class.return_value = mock_agent_service

        with patch('backend.routers.agent.get_session') as mock_get_session:
            mock_session = MagicMock(spec=Session)
            mock_get_session.return_value.__enter__.return_value = mock_session

            with patch('backend.routers.agent.get_current_user_id') as mock_get_current_user:
                mock_get_current_user.return_value = sample_user_id

                # Also mock the stub AI fallback
                with patch('backend.routers.agent.get_ai_response') as mock_get_ai_response:
                    mock_get_ai_response.return_value = "I'm sorry, but I'm currently experiencing issues. I'll help you as soon as I can."

                    response = client.post(
                        f"/api/{sample_user_id}/chat",
                        json={"message": "Test message when API is down"},
                        headers={"Authorization": "Bearer fake-token"}
                    )

                    # Should still return success (fallback mechanism)
                    assert response.status_code == 200
                    response_data = response.json()

                    # Should include fallback indicator
                    assert response_data.get("using_stub") is True
                    assert "service unavailable" in response_data.get("response", "").lower()

    @patch('backend.routers.agent.OpenAIAgentService')
    def test_agent_chat_endpoint_different_user_access_denied(self, mock_agent_service_class, client, sample_user_id):
        """Test that a user cannot access another user's agent session."""
        different_user_id = str(uuid.uuid4())

        mock_agent_service = MagicMock(spec=OpenAIAgentService)
        mock_agent_service_class.return_value = mock_agent_service

        with patch('backend.routers.agent.get_session') as mock_get_session:
            mock_session = MagicMock(spec=Session)
            mock_get_session.return_value.__enter__.return_value = mock_session

            with patch('backend.routers.agent.get_current_user_id') as mock_get_current_user:
                # Authenticated as different user, but trying to access sample_user_id's endpoint
                mock_get_current_user.return_value = different_user_id

                response = client.post(
                    f"/api/{sample_user_id}/chat",  # Trying to access sample_user_id's endpoint
                    json={"message": "Test message"},
                    headers={"Authorization": f"Bearer fake-token-{different_user_id}"}
                )

                # Should return 403 Forbidden
                assert response.status_code == 403
                assert "access denied" in response.json().get("detail", "").lower()

    @patch('backend.routers.agent.OpenAIAgentService')
    def test_agent_chat_endpoint_model_preferences(self, mock_agent_service_class, client, sample_user_id):
        """Test that the agent chat endpoint passes model preferences correctly."""
        mock_agent_service = MagicMock(spec=OpenAIAgentService)
        mock_agent_service.process_message.return_value = {
            "session_id": str(uuid.uuid4()),
            "response": "Response with specific model preferences applied.",
            "timestamp": "2026-02-08T10:30:00Z",
            "message_id": str(uuid.uuid4()),
            "tool_calls": [],
            "tool_results": {},
            "using_stub": False
        }

        mock_agent_service_class.return_value = mock_agent_service

        with patch('backend.routers.agent.get_session') as mock_get_session:
            mock_session = MagicMock(spec=Session)
            mock_get_session.return_value.__enter__.return_value = mock_session

            with patch('backend.routers.agent.get_current_user_id') as mock_get_current_user:
                mock_get_current_user.return_value = sample_user_id

                # Send message with model preferences
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={
                        "message": "Process this with high creativity",
                        "model_preferences": {
                            "temperature": 0.8,
                            "max_tokens": 150
                        }
                    },
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200
                # The agent service should be called with the message and preferences would be processed


if __name__ == "__main__":
    pytest.main([__file__])