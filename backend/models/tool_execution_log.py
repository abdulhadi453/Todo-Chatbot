"""
ToolExecutionLog model for the AI assistant integration.
Tracks all tool executions for monitoring, debugging, and security purposes.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from backend.models.user import User  # Assuming User model exists from Phase II
    from backend.models.agent_session import AgentSession


class ToolExecutionLog(SQLModel, table=True):
    """
    Model for logging tool executions by the AI agent.
    Used for monitoring, debugging, security auditing, and performance analysis.
    """

    __tablename__ = "tool_execution_logs"

    # Primary key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Foreign keys for tracking execution context
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)  # User who initiated the tool call
    session_id: Optional[uuid.UUID] = Field(default=None, foreign_key="agent_sessions.id")  # Session where tool was called
    tool_id: uuid.UUID = Field(foreign_key="agent_tools.id", nullable=False)  # Tool that was executed

    # Execution details
    tool_name: str = Field(max_length=100, nullable=False)  # Name of the tool (denormalized for performance)
    parameters: Optional[Dict[str, Any]] = Field(default=None, sa_column='JSON')  # Input parameters passed to the tool
    result: Optional[Dict[str, Any]] = Field(default=None, sa_column='JSON')  # Output from the tool execution
    error_message: Optional[str] = Field(default=None, max_length=1000)  # Error message if execution failed
    execution_time_ms: Optional[float] = Field(default=None)  # Time taken to execute the tool in milliseconds
    status: str = Field(sa_column_kwargs={"check": "status IN ('success', 'error', 'cancelled')"})  # Execution status

    # Timestamps
    executed_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        """
        String representation of the ToolExecutionLog.

        Returns:
            Formatted string representation
        """
        return f"<ToolExecutionLog(id={self.id}, tool_name='{self.tool_name}', status='{self.status}', executed_at={self.executed_at})>"

    def dict(self, **kwargs):
        """
        Override dict method to properly serialize UUIDs and datetime objects.

        Args:
            **kwargs: Additional options for serialization

        Returns:
            Dictionary representation of the ToolExecutionLog
        """
        d = super().dict(**kwargs)

        # Convert UUIDs to string for serialization
        d["id"] = str(d["id"])
        d["user_id"] = str(d["user_id"])
        if d.get("session_id"):
            d["session_id"] = str(d["session_id"])
        d["tool_id"] = str(d["tool_id"])

        # Convert datetime to ISO format string
        d["executed_at"] = self.executed_at.isoformat()

        return d

    @classmethod
    def create_log(
        cls,
        user_id: uuid.UUID,
        tool_id: uuid.UUID,
        tool_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        session_id: Optional[uuid.UUID] = None
    ) -> "ToolExecutionLog":
        """
        Create a tool execution log entry.

        Args:
            user_id: ID of the user who initiated the tool call
            tool_id: ID of the tool being executed
            tool_name: Name of the tool (for denormalization)
            parameters: Parameters passed to the tool
            result: Result from the tool execution
            error_message: Error message if execution failed
            execution_time_ms: Execution time in milliseconds
            session_id: Session ID where the tool was called (optional)

        Returns:
            New ToolExecutionLog instance
        """
        status = "error" if error_message else "success"

        return cls(
            user_id=user_id,
            tool_id=tool_id,
            tool_name=tool_name,
            parameters=parameters,
            result=result,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            status=status,
            session_id=session_id
        )

    @property
    def was_successful(self) -> bool:
        """
        Check if the tool execution was successful.

        Returns:
            True if status is 'success', False otherwise
        """
        return self.status == "success"

    @property
    def has_error(self) -> bool:
        """
        Check if the tool execution had an error.

        Returns:
            True if error_message is present, False otherwise
        """
        return self.error_message is not None

    @property
    def execution_duration(self) -> Optional[str]:
        """
        Get formatted execution duration.

        Returns:
            Formatted string of execution time or None if not available
        """
        if self.execution_time_ms is not None:
            if self.execution_time_ms < 1000:
                return f"{self.execution_time_ms:.0f}ms"
            else:
                seconds = self.execution_time_ms / 1000
                return f"{seconds:.2f}s"
        return None