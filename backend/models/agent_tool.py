"""
AgentTool model for the AI assistant integration.
Represents tools available to the AI agent for performing operations.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from backend.models.user import User  # Assuming User model exists from Phase II


class AgentTool(SQLModel, table=True):
    """
    Model representing a tool available to the AI agent.
    Defines the capabilities that an agent can use to interact with the system.
    """

    __tablename__ = "agent_tools"

    # Primary key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Tool identification and metadata
    name: str = Field(sa_column_kwargs={"unique": True, "nullable": False, "max_length": 100})  # Unique tool name
    description: str = Field(max_length=500)  # Description of what the tool does
    schema_def: Optional[Dict[str, Any]] = Field(default=None, sa_column='JSON')  # JSON schema definition for tool parameters
    enabled: bool = Field(default=True)  # Whether the tool is currently available
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user (who can access/use this tool - for user-specific tools)
    # Note: This could be null for system-wide tools
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    def __repr__(self):
        """
        String representation of the AgentTool.

        Returns:
            Formatted string representation
        """
        return f"<AgentTool(id={self.id}, name='{self.name}', enabled={self.enabled})>"

    def dict(self, **kwargs):
        """
        Override dict method to properly serialize UUIDs and datetime objects.

        Args:
            **kwargs: Additional options for serialization

        Returns:
            Dictionary representation of the AgentTool
        """
        d = super().dict(**kwargs)

        # Convert UUID to string for serialization
        d["id"] = str(d["id"])
        if d.get("user_id"):
            d["user_id"] = str(d["user_id"])

        # Convert datetime to ISO format string
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()

        return d

    @classmethod
    def create_builtin_tool(cls, name: str, description: str, schema_def: Optional[Dict[str, Any]] = None) -> "AgentTool":
        """
        Create a built-in tool available to all users.

        Args:
            name: Name of the tool
            description: Description of the tool
            schema_def: JSON schema definition for the tool's parameters

        Returns:
            New AgentTool instance with no user restriction
        """
        return cls(
            name=name,
            description=description,
            schema_def=schema_def,
            enabled=True,
            user_id=None  # No user restriction for built-in tools
        )

    @property
    def is_system_tool(self) -> bool:
        """
        Check if this is a system-wide tool available to all users.

        Returns:
            True if the tool is available to all users, False if user-specific
        """
        return self.user_id is None

    @property
    def is_user_tool(self) -> bool:
        """
        Check if this is a user-specific tool.

        Returns:
            True if the tool is restricted to a specific user, False if system-wide
        """
        return self.user_id is not None