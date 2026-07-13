"""
AgentMessage model for the AI assistant integration.
Represents a message within an agent conversation session.
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import JSON

class AgentMessage(SQLModel, table=True):
    """
    Model representing a message in an agent conversation.
    Can be from user, AI assistant, or tool execution results.
    """

    __tablename__ = "agent_messages"
    __table_args__ = {"extend_existing": True}

    # Primary key - using string to match other models
    id: Optional[str] = Field(default=None, primary_key=True)

    # Foreign keys - using string to match User.id and AgentSession.id
    session_id: str = Field(foreign_key="agent_sessions.id", nullable=False)  # Link to conversation session
    user_id: str = Field(foreign_key="users.id", nullable=False)  # Who sent this message

    # Message content and metadata
    role: str  # Who sent the message
    content: str = Field(max_length=10000)  # The actual message content
    timestamp: Optional[datetime] = Field(default=None)  # When the message was created

    # Tool execution information (when role is 'tool')
    tool_calls: Optional[dict] = Field(default=None, sa_type=JSON)  # Details of tools called by agent
    tool_call_results: Optional[dict] = Field(default=None, sa_type=JSON)  # Results from tool executions

    def __repr__(self):
        """
        String representation of the AgentMessage.

        Returns:
            Formatted string representation
        """
        return f"<AgentMessage(id={self.id}, role='{self.role}', session_id={self.session_id})>"

    def dict(self, **kwargs):
        """
        Override dict method to properly serialize datetime objects.

        Args:
            **kwargs: Additional options for serialization

        Returns:
            Dictionary representation of the AgentMessage
        """
        d = super().dict(**kwargs)

        # Convert datetime to ISO format string
        if self.timestamp:
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
    def create_user_message(cls, session_id: str, user_id: str, content: str) -> "AgentMessage":
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
    def create_assistant_message(cls, session_id: str, user_id: str, content: str) -> "AgentMessage":
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
        session_id: str,
        user_id: str,
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