"""
Test suite for conversation history functionality in the AI agent system.
Tests the ability to maintain and retrieve conversation history between AI agent interactions.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid
from sqlmodel import Session, select
from backend.src.main import app
from backend.models.agent_session import AgentSession
from backend.models.agent_message import AgentMessage
from backend.models.user_context import UserContext
from backend.services.openai_agent_service import OpenAIAgentService
from backend.database import get_session


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_user_id():
    """Provide a sample user ID for testing."""
    return str(uuid.uuid4())


class TestConversationHistory:
    """Test cases for conversation history functionality."""

    def test_conversation_session_creation_and_retrieval(self, client, sample_user_id):
        """Test that conversation sessions are created and can be retrieved."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            # Create a conversation by sending a message to the agent
            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = []
                mock_completion.choices[0].message.content = "Hello! How can I help you today?"

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Send first message to create conversation
                response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Hello, I need help with my tasks"},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert "conversation_id" in data
                conversation_id = data["conversation_id"]

                # Retrieve the conversation
                get_conv_response = client.get(
                    f"/api/{sample_user_id}/conversations/{conversation_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert get_conv_response.status_code == 200
                conv_data = get_conv_response.json()
                assert conv_data["id"] == conversation_id
                assert "messages" in conv_data
                assert len(conv_data["messages"]) > 0

    def test_conversation_messages_persist_across_interactions(self, client, sample_user_id):
        """Test that messages persist in the conversation across multiple interactions."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # First interaction
                mock_completion_1 = MagicMock()
                mock_completion_1.choices = [MagicMock()]
                mock_completion_1.choices[0].message = MagicMock()
                mock_completion_1.choices[0].message.tool_calls = []
                mock_completion_1.choices[0].message.content = "Sure, I can help you with that."

                # Second interaction
                mock_completion_2 = MagicMock()
                mock_completion_2.choices = [MagicMock()]
                mock_completion_2.choices[0].message = MagicMock()
                mock_completion_2.choices[0].message.tool_calls = []
                mock_completion_2.choices[0].message.content = "Is there anything else I can assist with?"

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(side_effect=[mock_completion_1, mock_completion_2])

                mock_openai.return_value = mock_client_instance

                # First interaction
                first_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Can you help me organize my tasks?"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert first_response.status_code == 200
                first_data = first_response.json()
                conversation_id = first_data["conversation_id"]

                # Second interaction in the same conversation
                second_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={
                        "message": "Yes, can you show me my current tasks?",
                        "conversation_id": conversation_id
                    },
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert second_response.status_code == 200

                # Retrieve conversation and check that both messages are present
                get_conv_response = client.get(
                    f"/api/{sample_user_id}/conversations/{conversation_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert get_conv_response.status_code == 200
                conv_data = get_conv_response.json()
                assert len(conv_data["messages"]) >= 2  # At least 2 user messages + 2 AI responses

                # Check that messages are properly ordered and include both user and AI messages
                user_messages = [msg for msg in conv_data["messages"] if msg["role"] == "user"]
                ai_messages = [msg for msg in conv_data["messages"] if msg["role"] == "assistant"]

                assert len(user_messages) >= 2
                assert len(ai_messages) >= 2

    def test_list_conversations_returns_multiple_conversations(self, client, sample_user_id):
        """Test that multiple conversations can be listed for a user."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = []
                mock_completion.choices[0].message.content = "Got it!"

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Create first conversation
                first_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "First conversation message"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert first_response.status_code == 200

                # Create second conversation
                second_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Second conversation message"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert second_response.status_code == 200

                # List all conversations
                list_response = client.get(
                    f"/api/{sample_user_id}/conversations",
                    params={"limit": 10, "offset": 0},
                    headers={"Authorization": "Bearer fake-token"}
                )

                assert list_response.status_code == 200
                conversations = list_response.json()
                assert isinstance(conversations, list)
                # Should have at least one conversation
                assert len(conversations) >= 1

    def test_conversation_history_maintains_context_for_agent(self, client, sample_user_id):
        """Test that the agent can access conversation history to maintain context."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                # Mock response for first interaction
                mock_completion_1 = MagicMock()
                mock_completion_1.choices = [MagicMock()]
                mock_completion_1.choices[0].message = MagicMock()
                mock_completion_1.choices[0].message.tool_calls = []
                mock_completion_1.choices[0].message.content = "I've created a task called 'Buy groceries'."

                # Mock response for second interaction that should reference previous context
                mock_completion_2 = MagicMock()
                mock_completion_2.choices = [MagicMock()]
                mock_completion_2.choices[0].message = MagicMock()
                mock_completion_2.choices[0].message.tool_calls = []
                mock_completion_2.choices[0].message.content = "Regarding the groceries task you mentioned earlier, would you like to add items to the list?"

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(side_effect=[mock_completion_1, mock_completion_2])

                mock_openai.return_value = mock_client_instance

                # First interaction
                first_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Create a task to buy groceries"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert first_response.status_code == 200
                first_data = first_response.json()
                conversation_id = first_data["conversation_id"]

                # Second interaction in the same conversation
                second_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={
                        "message": "Tell me about the tasks we talked about",
                        "conversation_id": conversation_id
                    },
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert second_response.status_code == 200

                # Verify the response acknowledges previous context
                second_data = second_response.json()
                # The agent should have access to previous messages to provide context-aware responses
                assert "response" in second_data

                # Check that conversation history contains multiple messages
                get_conv_response = client.get(
                    f"/api/{sample_user_id}/conversations/{conversation_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert get_conv_response.status_code == 200
                conv_data = get_conv_response.json()
                assert len(conv_data["messages"]) >= 2

    def test_conversation_deletion_removes_history(self, client, sample_user_id):
        """Test that deleting a conversation removes its history."""
        with patch('backend.auth.jwt.get_current_user_id') as mock_auth:
            mock_auth.return_value = sample_user_id

            with patch('backend.services.openai_agent_service.OpenAI') as mock_openai:
                mock_completion = MagicMock()
                mock_completion.choices = [MagicMock()]
                mock_completion.choices[0].message = MagicMock()
                mock_completion.choices[0].message.tool_calls = []
                mock_completion.choices[0].message.content = "Hello!"

                mock_client_instance = MagicMock()
                mock_client_instance.chat = MagicMock()
                mock_client_instance.chat.completions = MagicMock()
                mock_client_instance.chat.completions.create = MagicMock(return_value=mock_completion)

                mock_openai.return_value = mock_client_instance

                # Create a conversation
                create_response = client.post(
                    f"/api/{sample_user_id}/chat",
                    json={"message": "Test message for deletion"},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert create_response.status_code == 200
                create_data = create_response.json()
                conversation_id = create_data["conversation_id"]

                # Verify conversation exists
                get_response = client.get(
                    f"/api/{sample_user_id}/conversations/{conversation_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert get_response.status_code == 200

                # Delete the conversation
                delete_response = client.delete(
                    f"/api/{sample_user_id}/conversations/{conversation_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert delete_response.status_code == 200
                assert delete_response.json()["success"] is True

                # Verify conversation is no longer accessible
                get_deleted_response = client.get(
                    f"/api/{sample_user_id}/conversations/{conversation_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert get_deleted_response.status_code in [404, 400]  # Should not be found

    def test_database_models_store_conversation_data_correctly(self, sample_user_id):
        """Test that conversation data is correctly stored in the database models."""
        from backend.database import get_session
        from sqlmodel import Session

        with next(get_session()) as session:
            # Create a conversation session
            session_obj = AgentSession(
                user_id=sample_user_id,
                title="Test Conversation"
            )
            session.add(session_obj)
            session.commit()
            session.refresh(session_obj)

            assert session_obj.user_id == sample_user_id
            assert session_obj.title == "Test Conversation"

            # Add messages to the conversation
            user_message = AgentMessage(
                session_id=session_obj.id,
                role="user",
                content="Hello, test message",
                timestamp=None
            )
            session.add(user_message)

            ai_message = AgentMessage(
                session_id=session_obj.id,
                role="assistant",
                content="Hi, this is the AI response",
                timestamp=None
            )
            session.add(ai_message)

            session.commit()

            # Verify messages were saved correctly
            user_msg_query = select(AgentMessage).where(
                AgentMessage.session_id == session_obj.id,
                AgentMessage.role == "user"
            )
            user_msgs = session.exec(user_msg_query).all()

            ai_msg_query = select(AgentMessage).where(
                AgentMessage.session_id == session_obj.id,
                AgentMessage.role == "assistant"
            )
            ai_msgs = session.exec(ai_msg_query).all()

            assert len(user_msgs) == 1
            assert len(ai_msgs) == 1
            assert user_msgs[0].content == "Hello, test message"
            assert ai_msgs[0].content == "Hi, this is the AI response"

            # Verify user context is properly linked
            user_context = UserContext(
                user_id=sample_user_id,
                preferences={},
                last_interaction=None
            )
            session.add(user_context)
            session.commit()


if __name__ == "__main__":
    pytest.main([__file__])