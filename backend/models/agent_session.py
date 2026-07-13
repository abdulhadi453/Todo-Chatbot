"""
AgentSession model for the AI assistant integration.
Represents a conversation session between a user and the AI agent.
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class AgentSession(SQLModel, table=True):
    """
    Model representing a session between a user and the AI agent.
    Tracks conversation state and metadata for chat interactions.
    """

    __tablename__ = "agent_sessions"
    __table_args__ = {"extend_existing": True}

    # Primary key - using string to match User.id type
    id: Optional[str] = Field(default=None, primary_key=True)

    # Foreign key to user (maintaining user isolation) - using string to match User.id
    user_id: str = Field(foreign_key="users.id", nullable=False)

    # Session metadata
    title: Optional[str] = Field(default=None, max_length=200)  # Auto-generated or user-provided title
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


    def __repr__(self):
        """
        String representation of the AgentSession.

        Returns:
            Formatted string representation
        """
        return f"<AgentSession(id={self.id}, user_id={self.user_id}, title='{self.title}')>"

    def dict(self, **kwargs):
        """
        Override dict method to properly serialize datetime objects.

        Args:
            **kwargs: Additional options for serialization

        Returns:
            Dictionary representation of the AgentSession
        """
        d = super().dict(**kwargs)

        # Convert datetime to ISO format string
        if self.created_at:
            d["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            d["updated_at"] = self.updated_at.isoformat()

        # Remove the related objects to prevent circular references unless explicitly requested
        if "include_relationships" not in kwargs or not kwargs["include_relationships"]:
            d.pop("messages", None)

        return d