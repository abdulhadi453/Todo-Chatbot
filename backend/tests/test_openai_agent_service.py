"""
Unit tests for the OpenAI Agent Service.
Tests both real OpenAI integration and stub AI fallback.
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from backend.services.openai_agent_service import OpenAIAgentService
from backend.services.todo_tools import TodoTools
from backend.models.agent_session import AgentSession
from backend.models.agent_message import AgentMessage
from backend.models.task import Task
from backend.exceptions.chat_exceptions import ValidationError


@pytest.fixture(name="session")
def session_fixture():
    """
    Create an in-memory SQLite database for testing.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="user_id")
def user_id_fixture():
    """
    Generate a test user ID.
    """
    return str(uuid.uuid4())


@pytest.fixture(name="agent_service")
def agent_service_fixture(session):
    """
    Create an OpenAI Agent Service instance with stub AI enabled.
    """
    return OpenAIAgentService(session, use_stub=True)


class TestOpenAIAgentServiceInit:
    """
    Test initialization of the OpenAI Agent Service.
    """

    def test_init_with_stub(self, session):
        """Test initialization with stub AI enabled."""
        service = OpenAIAgentService(session, use_stub=True)
        assert service.use_stub is True
        assert service.client is None
        assert len(service.tools) == 5  # 5 tools defined

    def test_init_without_api_key(self, session):
        """Test initialization without API key falls back to stub."""
        with patch("backend.config.agent_config.AgentConfig.OPENAI_API_KEY", ""):
            service = OpenAIAgentService(session, use_stub=False)
            assert service.use_stub is True
            assert service.client is None

    @patch("backend.config.agent_config.AgentConfig.OPENAI_API_KEY", "sk-test-key")
    def test_init_with_api_key(self, session):
        """Test initialization with valid API key."""
        service = OpenAIAgentService(session, use_stub=False)
        assert service.use_stub is False
        assert service.client is not None

    def test_tool_functions_registered(self, agent_service):
        """Test that all tool functions are registered."""
        expected_tools = ["list_todos", "add_todo", "update_todo", "delete_todo", "get_user_context"]
        for tool_name in expected_tools:
            assert tool_name in agent_service.tool_functions


class TestToolDefinitions:
    """
    Test the tool definitions for OpenAI function calling.
    """

    def test_tools_count(self, agent_service):
        """Test that all expected tools are defined."""
        assert len(agent_service.tools) == 5

    def test_list_todos_definition(self, agent_service):
        """Test list_todos tool definition."""
        list_todos_tool = next(
            (tool for tool in agent_service.tools if tool["function"]["name"] == "list_todos"),
            None
        )
        assert list_todos_tool is not None
        assert list_todos_tool["type"] == "function"
        assert "user_id" in list_todos_tool["function"]["parameters"]["properties"]
        assert "limit" in list_todos_tool["function"]["parameters"]["properties"]

    def test_add_todo_definition(self, agent_service):
        """Test add_todo tool definition."""
        add_todo_tool = next(
            (tool for tool in agent_service.tools if tool["function"]["name"] == "add_todo"),
            None
        )
        assert add_todo_tool is not None
        assert "user_id" in add_todo_tool["function"]["parameters"]["required"]
        assert "title" in add_todo_tool["function"]["parameters"]["required"]


class TestToolExecution:
    """
    Test tool execution functionality.
    """

    def test_execute_unknown_tool(self, agent_service):
        """Test execution of an unknown tool returns error."""
        result = agent_service._execute_tool("unknown_tool", {})
        assert "error" in result
        assert result["success"] is False

    def test_execute_list_todos_success(self, agent_service, user_id):
        """Test successful execution of list_todos tool."""
        result = agent_service._execute_tool("list_todos", {"user_id": user_id})
        assert "todos" in result
        assert "pagination" in result
        assert isinstance(result["todos"], list)

    def test_execute_add_todo_success(self, agent_service, user_id):
        """Test successful execution of add_todo tool."""
        result = agent_service._execute_tool(
            "add_todo",
            {"user_id": user_id, "title": "Test Task", "description": "Test Description"}
        )
        assert result["success"] is True
        assert "todo" in result
        assert result["todo"]["title"] == "Test Task"

    def test_execute_add_todo_validation_error(self, agent_service, user_id):
        """Test add_todo with validation error."""
        result = agent_service._execute_tool(
            "add_todo",
            {"user_id": user_id, "title": ""}  # Empty title should fail
        )
        assert "error" in result
        assert result["success"] is False


class TestProcessMessage:
    """
    Test the main message processing functionality.
    """

    def test_process_message_with_stub(self, agent_service, user_id):
        """Test message processing with stub AI."""
        result = agent_service.process_message(
            user_id=user_id,
            message="Hello, can you help me with my todos?"
        )
        assert "session_id" in result
        assert "response" in result
        assert "message_id" in result
        assert "timestamp" in result
        assert result.get("using_stub") is True

    def test_process_message_creates_session(self, agent_service, user_id):
        """Test that message processing creates a new session."""
        result = agent_service.process_message(
            user_id=user_id,
            message="Test message"
        )
        session_id = result["session_id"]
        assert session_id is not None

        # Verify session exists in database
        session_uuid = uuid.UUID(session_id)
        session = agent_service.get_agent_session(session_uuid, uuid.UUID(user_id))
        assert session is not None

    def test_process_message_with_existing_session(self, agent_service, user_id):
        """Test message processing with existing session."""
        # Create first message to establish session
        result1 = agent_service.process_message(
            user_id=user_id,
            message="First message"
        )
        session_id = result1["session_id"]

        # Send second message in same session
        result2 = agent_service.process_message(
            user_id=user_id,
            message="Second message",
            session_id=session_id
        )

        # Should use same session
        assert result2["session_id"] == session_id

    def test_process_message_empty_message(self, agent_service, user_id):
        """Test that empty message raises validation error."""
        with pytest.raises(ValidationError):
            agent_service.process_message(
                user_id=user_id,
                message=""
            )

    def test_process_message_invalid_user_id(self, agent_service):
        """Test that invalid user ID raises validation error."""
        with pytest.raises(ValidationError):
            agent_service.process_message(
                user_id="invalid-uuid",
                message="Test message"
            )

    def test_process_message_stores_messages(self, agent_service, user_id):
        """Test that messages are stored in database."""
        result = agent_service.process_message(
            user_id=user_id,
            message="Test message"
        )

        session_id = uuid.UUID(result["session_id"])
        user_uuid = uuid.UUID(user_id)

        # Get messages from database
        messages = agent_service.get_session_messages(session_id, user_uuid)

        # Should have user message and assistant response
        assert len(messages) >= 2
        assert any(msg.role == "user" for msg in messages)
        assert any(msg.role == "assistant" for msg in messages)


class TestConversationManagement:
    """
    Test conversation management functionality.
    """

    def test_get_user_conversations(self, agent_service, user_id):
        """Test retrieving user's conversations."""
        # Create a conversation
        agent_service.process_message(user_id=user_id, message="Test")

        user_uuid = uuid.UUID(user_id)
        conversations = agent_service.get_user_conversations(user_uuid)

        assert len(conversations) > 0
        assert all(isinstance(conv, AgentSession) for conv in conversations)

    def test_delete_conversation(self, agent_service, user_id):
        """Test deleting a conversation."""
        # Create a conversation
        result = agent_service.process_message(user_id=user_id, message="Test")
        session_id = uuid.UUID(result["session_id"])
        user_uuid = uuid.UUID(user_id)

        # Delete the conversation
        success = agent_service.delete_conversation(session_id, user_uuid)
        assert success is True

        # Verify it's deleted
        session = agent_service.get_agent_session(session_id, user_uuid)
        assert session is None

    def test_delete_nonexistent_conversation(self, agent_service, user_id):
        """Test deleting a nonexistent conversation returns False."""
        user_uuid = uuid.UUID(user_id)
        random_session_id = uuid.uuid4()

        success = agent_service.delete_conversation(random_session_id, user_uuid)
        assert success is False


class TestBuildConversationHistory:
    """
    Test conversation history building for OpenAI context.
    """

    def test_build_empty_history(self, agent_service, user_id):
        """Test building history for new session."""
        session = agent_service.create_agent_session(user_id, "Initial message")
        user_uuid = uuid.UUID(user_id)

        history = agent_service._build_conversation_history(session.id, user_uuid)
        assert isinstance(history, list)
        assert len(history) == 0  # No messages yet

    def test_build_history_with_messages(self, agent_service, user_id):
        """Test building history with existing messages."""
        # Create conversation with messages
        result = agent_service.process_message(user_id=user_id, message="Test message")
        session_id = uuid.UUID(result["session_id"])
        user_uuid = uuid.UUID(user_id)

        # Build history
        history = agent_service._build_conversation_history(session_id, user_uuid)

        assert len(history) > 0
        assert all("role" in msg and "content" in msg for msg in history)


class TestErrorHandling:
    """
    Test error handling and fallback mechanisms.
    """

    def test_fallback_to_stub_on_openai_error(self, session, user_id):
        """Test that service falls back to stub on OpenAI error."""
        # Create service with real OpenAI client (mocked)
        with patch("backend.config.agent_config.AgentConfig.OPENAI_API_KEY", "sk-test"):
            service = OpenAIAgentService(session, use_stub=False)

            # Mock OpenAI client to raise error
            with patch.object(service, "client") as mock_client:
                mock_client.chat.completions.create.side_effect = Exception("API Error")

                # Should fall back to stub
                result = service.process_message(user_id=user_id, message="Test")

                assert "response" in result
                # Should indicate using stub due to error
                assert result.get("using_stub") is True or result.get("error") is not None

    def test_validation_on_max_message_length(self, agent_service, user_id):
        """Test that excessively long messages are rejected."""
        long_message = "a" * 20000  # Exceeds MAX_MESSAGE_LENGTH

        with pytest.raises(ValidationError):
            agent_service.process_message(user_id=user_id, message=long_message)


class TestIntegration:
    """
    Integration tests for end-to-end workflows.
    """

    def test_full_todo_workflow(self, agent_service, user_id):
        """Test a complete todo management workflow."""
        # Start conversation
        result1 = agent_service.process_message(
            user_id=user_id,
            message="Hello, I need help with my tasks"
        )
        session_id = result1["session_id"]
        assert "response" in result1

        # List todos (should be empty)
        result2 = agent_service.process_message(
            user_id=user_id,
            message="Show me my todos",
            session_id=session_id
        )
        assert "response" in result2

        # Add a todo via direct tool call (simulating agent behavior)
        add_result = agent_service._execute_tool(
            "add_todo",
            {"user_id": user_id, "title": "Test Task"}
        )
        assert add_result["success"] is True

        # Verify todo was added
        list_result = agent_service._execute_tool(
            "list_todos",
            {"user_id": user_id}
        )
        assert len(list_result["todos"]) == 1
        assert list_result["todos"][0]["title"] == "Test Task"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
