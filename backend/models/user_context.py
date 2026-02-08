"""
UserContext model for the AI assistant integration.
Stores user-specific information and preferences for AI interactions.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from backend.models.user import User  # Assuming User model exists from Phase II


class UserContext(SQLModel, table=True):
    """
    Model representing user-specific context and preferences for AI interactions.
    Stores information that helps the AI agent provide personalized responses.
    """

    __tablename__ = "user_contexts"

    # Primary key - using user_id as primary key since each user has exactly one context
    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)

    # Personalization information
    preferred_name: Optional[str] = Field(default=None, max_length=100)  # Preferred name for addressing the user
    communication_style: Optional[str] = Field(default="professional", max_length=50)  # E.g., casual, professional, formal
    timezone: Optional[str] = Field(default="UTC", max_length=50)  # User's timezone
    language: Optional[str] = Field(default="en", max_length=10)  # Language preference

    # AI interaction preferences
    preferred_temperature: float = Field(default=0.7)  # Temperature setting for AI responses (0.0 to 1.0)
    response_length_preference: str = Field(default="medium", sa_column_kwargs={"check": "response_length_preference IN ('short', 'medium', 'long')"})  # Preferred response length
    ai_personality_preference: Optional[str] = Field(default=None, max_length=100)  # Personality traits the user prefers

    # Context information
    user_profile_summary: Optional[str] = Field(default=None, max_length=500)  # Summary of user's work/interests
    frequent_topics: Optional[list[str]] = Field(default=[], sa_column='JSON')  # Topics the user frequently asks about
    context_notes: Optional[Dict[str, Any]] = Field(default=None, sa_column='JSON')  # Additional context notes for AI

    # Usage statistics
    total_interactions: int = Field(default=0)  # Total number of AI interactions
    last_interaction_at: Optional[datetime] = Field(default=None)  # Last time the user interacted with the AI
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        """
        String representation of the UserContext.

        Returns:
            Formatted string representation
        """
        return f"<UserContext(user_id={self.user_id}, preferred_name='{self.preferred_name}', communication_style='{self.communication_style}')>"

    def dict(self, **kwargs):
        """
        Override dict method to properly serialize UUIDs and datetime objects.

        Args:
            **kwargs: Additional options for serialization

        Returns:
            Dictionary representation of the UserContext
        """
        d = super().dict(**kwargs)

        # Convert UUID to string for serialization
        d["user_id"] = str(d["user_id"])

        # Convert datetime to ISO format string
        if d.get("created_at"):
            d["created_at"] = self.created_at.isoformat()
        if d.get("updated_at"):
            d["updated_at"] = self.updated_at.isoformat()
        if d.get("last_interaction_at") and self.last_interaction_at:
            d["last_interaction_at"] = self.last_interaction_at.isoformat()

        return d

    @classmethod
    def create_default_context(cls, user_id: uuid.UUID) -> "UserContext":
        """
        Create a default user context for a new user.

        Args:
            user_id: ID of the user for whom to create context

        Returns:
            New UserContext instance with default values
        """
        return cls(
            user_id=user_id,
            communication_style="professional",
            timezone="UTC",
            language="en",
            preferred_temperature=0.7,
            response_length_preference="medium"
        )

    def increment_interaction_count(self) -> None:
        """
        Increment the total interactions counter and update the last interaction timestamp.
        """
        self.total_interactions += 1
        self.last_interaction_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_communication_style(self, style: str) -> bool:
        """
        Update the user's communication style preference.

        Args:
            style: New communication style (casual, professional, formal)

        Returns:
            True if the update was successful, False otherwise
        """
        valid_styles = ["casual", "professional", "formal"]
        if style not in valid_styles:
            return False

        self.communication_style = style
        self.updated_at = datetime.utcnow()
        return True

    def update_response_length_preference(self, length_pref: str) -> bool:
        """
        Update the user's response length preference.

        Args:
            length_pref: New length preference (short, medium, long)

        Returns:
            True if the update was successful, False otherwise
        """
        valid_prefs = ["short", "medium", "long"]
        if length_pref not in valid_prefs:
            return False

        self.response_length_preference = length_pref
        self.updated_at = datetime.utcnow()
        return True

    def add_frequent_topic(self, topic: str) -> None:
        """
        Add a topic to the user's frequent topics list.

        Args:
            topic: Topic to add to the list
        """
        if not self.frequent_topics:
            self.frequent_topics = []

        if topic not in self.frequent_topics:
            self.frequent_topics.append(topic)
            self.updated_at = datetime.utcnow()

    def update_preferred_temperature(self, temperature: float) -> bool:
        """
        Update the user's preferred AI response temperature.

        Args:
            temperature: New temperature setting (0.0 to 1.0)

        Returns:
            True if the update was successful, False otherwise
        """
        if not 0.0 <= temperature <= 1.0:
            return False

        self.preferred_temperature = temperature
        self.updated_at = datetime.utcnow()
        return True