"""
AgentMessage model for the AI assistant integration.
Represents a message within an agent conversation session.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from backend.models.agent_session import AgentSession  # Forward reference for type checking
    from backend.models.user import User  # Assuming User model exists from Phase II


class AgentMessage(SQLModel, table=True):
    """
    Model representing a message in an agent conversation.
    Can be from user, AI assistant, or tool execution results.
    """

    __tablename__ = "agent_messages"

    # Primary key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Foreign keys
    session_id: uuid.UUID = Field(foreign_key="agent_sessions.id", nullable=False)  # Link to conversation session
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)  # Who sent this message

    # Message content and metadata
    role: str = Field(sa_column_kwargs={"check": "role IN ('user', 'assistant', 'tool')"})  # Who sent the message
    content: str = Field(max_length=10000)  # The actual message content
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # When the message was created

    # Tool execution information (when role is 'tool')
    tool_calls: Optional[Dict[str, Any]] = Field(default=None, sa_column='JSON')  # Details of tools called by agent
    tool_call_results: Optional[Dict[str, Any]] = Field(default=None, sa_column='JSON')  # Results from tool executions

    # Relationships
    session: "AgentSession" = Relationship(back_populates="messages")

    def __repr__(self):
        """
        String representation of the AgentMessage.

        Returns:
            Formatted string representation
        """
        return f"<AgentMessage(id={self.id}, role='{self.role}', session_id={self.session_id})>"

    def dict(self, **kwargs):
        """
        Override dict method to properly serialize UUIDs and datetime objects.

        Args:
            **kwargs: Additional options for serialization

        Returns:
            Dictionary representation of the AgentMessage
        """
        d = super().dict(**kwargs)

        # Convert UUID to string for serialization
        d["id"] = str(d["id"])
        d["session_id"] = str(d["session_id"])
        d["user_id"] = str(d["user_id"])

        # Convert datetime to ISO format string
        d["timestamp"] = self.timestamp.isoformat()

        # Handle potential None values for optional fields
        if d.get("tool_calls") is None:
            d.pop("tool_calls", None)
        if d.get("tool_call_results") is None:
            d.pop("tool_call_results", None)

        return d

    @property
    def is_user_message(self) -> bool:
        """
        Check if this message was sent by a user.

        Returns:
            True if role is 'user', False otherwise
        """
        return self.role == "user"

    @property
    def is_assistant_message(self) -> bool:
        """
        Check if this message was sent by the AI assistant.

        Returns:
            True if role is 'assistant', False otherwise
        """
        return self.role == "assistant"

    @property
    def is_tool_message(self) -> bool:
        """
        Check if this message is a tool execution result.

        Returns:
            True if role is 'tool', False otherwise
        """
        return self.role == "tool"

    @classmethod
    def create_user_message(cls, session_id: uuid.UUID, user_id: uuid.UUID, content: str) -> "AgentMessage":
        """
        Create a new user message.

        Args:
            session_id: ID of the session this message belongs to
            user_id: ID of the user sending the message
            content: Content of the message

        Returns:
            New AgentMessage instance
        """
        return cls(
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=content
        )

    @classmethod
    def create_assistant_message(cls, session_id: uuid.UUID, user_id: uuid.UUID, content: str) -> "AgentMessage":
        """
        Create a new assistant message.

        Args:
            session_id: ID of the session this message belongs to
            user_id: ID of the user this message is for
            content: Content of the message

        Returns:
            New AgentMessage instance
        """
        return cls(
            session_id=session_id,
            user_id=user_id,
            role="assistant",
            content=content
        )

    @classmethod
    def create_tool_message(
        cls,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        tool_calls: Optional[Dict[str, Any]] = None,
        tool_results: Optional[Dict[str, Any]] = None
    ) -> "AgentMessage":
        """
        Create a new tool message.

        Args:
            session_id: ID of the session this message belongs to
            user_id: ID of the user this message is for
            tool_calls: Details of tools called
            tool_results: Results from tool executions

        Returns:
            New AgentMessage instance
        """
        return cls(
            session_id=session_id,
            user_id=user_id,
            role="tool",
            content="Tool execution results",
            tool_calls=tool_calls,
            tool_call_results=tool_results
        )