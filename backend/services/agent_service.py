"""
Agent service for the AI assistant integration.
Handles core agent operations, conversation management, and tool execution.
"""

import uuid
from typing import Dict, Any, Optional, List
from sqlmodel import Session, select
from datetime import datetime

from backend.models.agent_session import AgentSession
from backend.models.agent_message import AgentMessage
from backend.models.user_context import UserContext
from backend.exceptions.chat_exceptions import UnauthorizedAccessException
from backend.services.todo_tools import TodoTools


class AgentService:
    """
    Service class for handling AI agent operations.
    Manages agent sessions, message history, and tool execution.
    """

    def __init__(self, session: Session):
        """
        Initialize the agent service with a database session.

        Args:
            session: Database session for data access
        """
        self.session = session

    def create_agent_session(self, user_id: str, initial_message: Optional[str] = None) -> AgentSession:
        """
        Create a new agent session for a user.

        Args:
            user_id: ID of the user creating the session
            initial_message: Optional initial message for the session

        Returns:
            Created AgentSession object
        """
        session_id = str(uuid.uuid4())

        agent_session = AgentSession(
            id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.session.add(agent_session)
        self.session.commit()
        self.session.refresh(agent_session)

        return agent_session

    def get_agent_session(self, session_id: str, user_id: str) -> Optional[AgentSession]:
        """
        Retrieve an agent session by ID for a specific user.

        Args:
            session_id: ID of the session to retrieve
            user_id: ID of the user requesting the session

        Returns:
            AgentSession object if found and owned by user, None otherwise
        """
        statement = select(AgentSession).where(
            AgentSession.id == session_id,
            AgentSession.user_id == user_id
        )
        agent_session = self.session.exec(statement).first()
        return agent_session

    def get_user_sessions(self, user_id: str, limit: int = 50, offset: int = 0) -> List[AgentSession]:
        """
        Get all agent sessions for a user.

        Args:
            user_id: ID of the user
            limit: Maximum number of sessions to return
            offset: Offset for pagination

        Returns:
            List of AgentSession objects
        """
        statement = select(AgentSession).where(
            AgentSession.user_id == user_id
        ).order_by(AgentSession.updated_at.desc()).offset(offset).limit(limit)

        sessions = self.session.exec(statement).all()
        return sessions

    def add_message_to_session(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        tool_calls: Optional[Dict[str, Any]] = None,
        tool_results: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """
        Add a message to an agent session.

        Args:
            session_id: ID of the session to add message to
            user_id: ID of the user adding the message
            role: Role of the message sender (user, assistant, tool)
            content: Content of the message
            tool_calls: Optional tool calls made in the message
            tool_results: Optional results from tool executions

        Returns:
            Created AgentMessage object
        """
        # Verify user owns the session
        agent_session = self.get_agent_session(session_id, user_id)
        if not agent_session:
            raise UnauthorizedAccessException(f"User {user_id} does not have access to session {session_id}")

        message_id = str(uuid.uuid4())

        agent_message = AgentMessage(
            id=message_id,
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            tool_calls=tool_calls,
            tool_call_results=tool_results
        )

        self.session.add(agent_message)

        # Update session timestamp
        agent_session.updated_at = datetime.utcnow()
        self.session.add(agent_session)

        self.session.commit()
        self.session.refresh(agent_message)

        return agent_message

    def get_session_messages(self, session_id: str, user_id: str, limit: int = 100, offset: int = 0) -> List[AgentMessage]:
        """
        Get messages for a specific session.

        Args:
            session_id: ID of the session
            user_id: ID of the user requesting messages
            limit: Maximum number of messages to return
            offset: Offset for pagination

        Returns:
            List of AgentMessage objects
        """
        # Verify user owns the session
        agent_session = self.get_agent_session(session_id, user_id)
        if not agent_session:
            raise UnauthorizedAccessException(f"User {user_id} does not have access to session {session_id}")

        statement = select(AgentMessage).where(
            AgentMessage.session_id == session_id
        ).order_by(AgentMessage.timestamp.asc()).offset(offset).limit(limit)

        messages = self.session.exec(statement).all()
        return messages

    def get_user_context(self, user_id: str) -> Optional[UserContext]:
        """
        Get the user context for the specified user.

        Args:
            user_id: ID of the user

        Returns:
            UserContext object if found, None otherwise
        """
        from backend.models.user_context import UserContext  # Import here to avoid circular dependency

        statement = select(UserContext).where(UserContext.user_id == user_id)
        user_context = self.session.exec(statement).first()
        return user_context

    def validate_user_access(self, session_id: str, user_id: str) -> bool:
        """
        Validate that a user has access to a specific session.

        Args:
            session_id: ID of the session to check
            user_id: ID of the user requesting access

        Returns:
            True if user has access, False otherwise
        """
        agent_session = self.get_agent_session(session_id, user_id)
        return agent_session is not None

    def update_user_context(self, user_id: str, **context_data) -> Optional[UserContext]:
        """
        Update user context with new information.

        Args:
            user_id: ID of the user
            **context_data: Context data to update

        Returns:
            Updated UserContext object if successful, None otherwise
        """
        from backend.models.user_context import UserContext  # Import here to avoid circular dependency

        user_context = self.get_user_context(user_id)
        if not user_context:
            return None

        # Update allowed fields
        allowed_fields = {"preferences", "usage_stats", "last_accessed"}
        for field, value in context_data.items():
            if field in allowed_fields and hasattr(user_context, field):
                setattr(user_context, field, value)

        user_context.updated_at = datetime.utcnow()

        self.session.add(user_context)
        self.session.commit()
        self.session.refresh(user_context)

        return user_context

    def update_session_metadata(self, session_id: str, user_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a specific agent session.

        Args:
            session_id: ID of the session to update
            user_id: ID of the user requesting the update
            metadata: Metadata dictionary to update

        Returns:
            True if update was successful, False otherwise
        """
        agent_session = self.get_agent_session(session_id, user_id)
        if not agent_session:
            return False

        # Update session title if provided in metadata
        if 'title' in metadata:
            agent_session.title = str(metadata['title'])

        # In a more advanced implementation, we might want to store arbitrary metadata
        # For now, we'll update common fields like title

        agent_session.updated_at = datetime.utcnow()
        self.session.add(agent_session)
        self.session.commit()

        return True

    def archive_session(self, session_id: str, user_id: str) -> bool:
        """
        Archive a session (mark as inactive without deleting).

        Args:
            session_id: ID of the session to archive
            user_id: ID of the user requesting archiving

        Returns:
            True if archiving was successful, False otherwise
        """
        agent_session = self.get_agent_session(session_id, user_id)
        if not agent_session:
            return False

        # Add archiving functionality - though our model may not have an archived field
        # We could implement this by updating title or using the description field for status
        if agent_session.title:
            agent_session.title = f"[ARCHIVED] {agent_session.title}"
        else:
            agent_session.title = "[ARCHIVED] Archived Session"

        agent_session.updated_at = datetime.utcnow()
        self.session.add(agent_session)
        self.session.commit()

        return True

    def get_session_summary(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a session including metadata and statistics.

        Args:
            session_id: ID of the session to summarize
            user_id: ID of the user requesting the summary

        Returns:
            Dictionary with session summary information, or None if not found
        """
        agent_session = self.get_agent_session(session_id, user_id)
        if not agent_session:
            return None

        # Get messages in the session
        messages = self.get_session_messages(session_id, user_id, limit=1000)

        # Calculate session statistics
        message_count = len(messages)
        user_messages = sum(1 for msg in messages if msg.role == "user")
        assistant_messages = sum(1 for msg in messages if msg.role == "assistant")

        # Determine session activity period
        if messages:
            start_time = min(msg.timestamp for msg in messages)
            end_time = max(msg.timestamp for msg in messages)
            duration_seconds = (end_time - start_time).total_seconds()
        else:
            start_time = agent_session.created_at
            end_time = agent_session.updated_at
            duration_seconds = (end_time - start_time).total_seconds()

        return {
            "session_id": session_id,
            "user_id": user_id,
            "title": agent_session.title,
            "created_at": agent_session.created_at.isoformat(),
            "updated_at": agent_session.updated_at.isoformat(),
            "message_count": message_count,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration_seconds,
            "is_active": True  # Simple implementation, could be based on last activity
        }

    def get_active_sessions(self, user_id: str, minutes_since_activity: int = 30) -> List[AgentSession]:
        """
        Get all sessions that have been active within a certain time period.

        Args:
            user_id: ID of the user
            minutes_since_activity: Number of minutes to look back for activity

        Returns:
            List of recently active AgentSession objects
        """
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes_since_activity)

        statement = select(AgentSession).where(
            AgentSession.user_id == user_id,
            AgentSession.updated_at >= cutoff_time
        ).order_by(AgentSession.updated_at.desc())

        active_sessions = self.session.exec(statement).all()
        return active_sessions

    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Cleanup sessions older than specified days (mark for archival or deletion).
        This is a soft cleanup that marks sessions as archived rather than deleting them.

        Args:
            days_old: Number of days old a session must be to be cleaned up

        Returns:
            Number of sessions processed
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        statement = select(AgentSession).where(
            AgentSession.created_at < cutoff_date
        )
        old_sessions = self.session.exec(statement).all()

        processed_count = 0
        for session in old_sessions:
            # Instead of deleting, we'll update the title to indicate archival
            if session.title:
                session.title = f"[AUTO-ARCHIVED] {session.title}"
            else:
                session.title = "[AUTO-ARCHIVED] Old Session"
            session.updated_at = datetime.utcnow()
            self.session.add(session)
            processed_count += 1

        if processed_count > 0:
            self.session.commit()

        return processed_count