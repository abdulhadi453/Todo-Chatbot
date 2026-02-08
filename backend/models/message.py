from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
from sqlalchemy import JSON

if TYPE_CHECKING:
    from backend.models.user import User  # Assuming User model exists from Phase II
    from backend.models.conversation import Conversation


class Message(SQLModel, table=True):
    """
    Represents an individual message in a conversation.
    """
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(nullable=False)  # Reference to conversation (validated at application level)
    user_id: str = Field(nullable=False)  # Who sent this message (validated at application level)
    role: str = Field(nullable=False)
    content: str = Field(nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    parent_message_id: Optional[str] = Field(default=None)  # Reference to parent message (validated at application level)
    metadata_json: Optional[str] = Field(default=None)  # Store as JSON string for simplicity

    # Relationship to the conversation this message belongs to
    conversation: "Conversation" = Relationship(back_populates="messages")

    # Relationship to the user who sent this message
    user: "User" = Relationship(back_populates="messages")

    def dict(self, **kwargs):
        """Override dict method to serialize properly"""
        d = super().dict(**kwargs)
        # Return the values as they are (UUIDs already converted to strings by the field factory)
        return d