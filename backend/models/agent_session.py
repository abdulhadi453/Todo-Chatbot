"""
AgentSession model for the AI assistant integration.
Represents a conversation session between a user and the AI agent.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from backend.models.agent_message import AgentMessage  # Forward reference for type checking
    from backend.models.user import User  # Assuming User model exists from Phase II


class AgentSession(SQLModel, table=True):
    """
    Model representing a session between a user and the AI agent.
    Tracks conversation state and metadata for chat interactions.
    """

    __tablename__ = "agent_sessions"

    # Primary key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Foreign key to user (maintaining user isolation)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)

    # Session metadata
    title: Optional[str] = Field(default=None, max_length=200)  # Auto-generated or user-provided title
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with messages in this session
    messages: List["AgentMessage"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"}
    )

    # Relationship with user (optional if User model exists)
    # user: Optional["User"] = Relationship(back_populates="agent_sessions")


    def __repr__(self):
        """
        String representation of the AgentSession.

        Returns:
            Formatted string representation
        """
        return f"<AgentSession(id={self.id}, user_id={self.user_id}, title='{self.title}')>"

    def dict(self, **kwargs):
        """
        Override dict method to properly serialize UUIDs and datetime objects.

        Args:
            **kwargs: Additional options for serialization

        Returns:
            Dictionary representation of the AgentSession
        """
        d = super().dict(**kwargs)

        # Convert UUID to string for serialization
        d["id"] = str(d["id"])
        d["user_id"] = str(d["user_id"])

        # Convert datetime to ISO format string
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()

        # Remove the related objects to prevent circular references unless explicitly requested
        if "include_relationships" not in kwargs or not kwargs["include_relationships"]:
            d.pop("messages", None)

        return d