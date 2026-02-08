"""
Chat service for handling conversation and message operations.
This service provides business logic for the chatbot feature.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, asc, desc
import uuid
from backend.models.conversation import Conversation
from backend.models.message import Message
from backend.models.user import User  # Assuming User model exists from Phase II
from backend.auth.jwt import verify_user_owns_resource


class ChatService:
    """
    Service class for handling chat operations including:
    - Creating and managing conversations
    - Saving and retrieving messages
    - Validating user permissions
    """

    def __init__(self, session: Session):
        """
        Initialize the chat service with a database session.

        Args:
            session: Database session for database operations
        """
        self.session = session

    def create_conversation(self, user_id: uuid.UUID, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            user_id: ID of the user creating the conversation
            title: Optional title for the conversation

        Returns:
            Conversation: The newly created conversation object
        """
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation_by_id(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID, ensuring the user has access to it.

        Args:
            conversation_id: ID of the conversation to retrieve
            user_id: ID of the requesting user

        Returns:
            Conversation: The conversation object if found and accessible, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = self.session.exec(statement).first()
        return conversation

    def get_user_conversations(self, user_id: uuid.UUID) -> List[Conversation]:
        """
        Get all conversations for a specific user.

        Args:
            user_id: ID of the user whose conversations to retrieve

        Returns:
            List[Conversation]: List of conversations belonging to the user
        """
        statement = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(desc(Conversation.updated_at))
        conversations = self.session.exec(statement).all()
        return conversations

    def create_message(self, conversation_id: uuid.UUID, user_id: uuid.UUID,
                      content: str, role: str = "user", metadata: Optional[Dict] = None) -> Message:
        """
        Create a new message in a conversation.

        Args:
            conversation_id: ID of the conversation to add the message to
            user_id: ID of the user sending the message
            content: Content of the message
            role: Role of the message sender (user, assistant, system)
            metadata: Optional metadata for the message

        Returns:
            Message: The newly created message object
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            metadata=metadata
        )
        self.session.add(message)

        # Update the conversation's updated_at timestamp
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages_for_conversation(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> List[Message]:
        """
        Get all messages for a specific conversation, ensuring the user has access.

        Args:
            conversation_id: ID of the conversation to get messages from
            user_id: ID of the requesting user

        Returns:
            List[Message]: List of messages in the conversation
        """
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id  # Ensures user can only see their own messages in the conversation
        ).order_by(asc(Message.timestamp))
        messages = self.session.exec(statement).all()
        return messages

    def get_full_conversation_history(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> List[Message]:
        """
        Get the complete history of messages for a conversation.

        Args:
            conversation_id: ID of the conversation to get history for
            user_id: ID of the requesting user

        Returns:
            List[Message]: Complete message history for the conversation
        """
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(asc(Message.timestamp))

        all_messages = self.session.exec(statement).all()

        # Verify that the user owns the conversation before returning messages
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return []  # Return empty list if user doesn't own the conversation

        # Additional check: ensure all messages belong to this user in this conversation
        user_messages = [msg for msg in all_messages if str(msg.user_id) == str(user_id)]
        return user_messages

    def validate_user_conversation_access(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Validate that a user has access to a specific conversation.

        Args:
            conversation_id: ID of the conversation to check
            user_id: ID of the user requesting access

        Returns:
            bool: True if user has access, False otherwise
        """
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        return conversation is not None

    def update_conversation_title(self, conversation_id: uuid.UUID, user_id: uuid.UUID, title: str) -> bool:
        """
        Update the title of a conversation.

        Args:
            conversation_id: ID of the conversation to update
            user_id: ID of the user requesting the update
            title: New title for the conversation

        Returns:
            bool: True if update was successful, False otherwise
        """
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False

        conversation.title = title
        conversation.updated_at = datetime.utcnow()
        self.session.add(conversation)
        self.session.commit()
        return True

    def delete_conversation(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: ID of the conversation to delete
            user_id: ID of the user requesting deletion

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False

        # Delete the conversation (and its messages due to cascade delete)
        self.session.delete(conversation)
        self.session.commit()
        return True

    def validate_message_content(self, content: str) -> tuple[bool, Optional[str]]:
        """
        Validate message content according to business rules.

        Args:
            content: Content to validate

        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message if not valid)
        """
        if not content or len(content.strip()) == 0:
            return False, "Message content cannot be empty"

        if len(content) > 10000:  # As specified in API contract
            return False, "Message content exceeds maximum length of 10,000 characters"

        return True, None