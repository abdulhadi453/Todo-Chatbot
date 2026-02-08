from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from backend.models.user import User  # Assuming User model exists from Phase II
    from backend.models.message import Message


class Conversation(SQLModel, table=True):
    """
    Represents a collection of messages between a user and the AI assistant.
    """
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(nullable=False)  # Reference to user (will be validated at application level)
    title: Optional[str] = Field(default=None, max_length=200)  # Optional auto-generated or user-defined title
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationship to user (who owns this conversation)
    user: "User" = Relationship(back_populates="conversations")

    # Relationship to messages in this conversation
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    def dict(self, **kwargs):
        """Override dict method to serialize properly"""
        d = super().dict(**kwargs)
        # Return the values as they are (UUIDs already converted to strings by the field factory)
        return d