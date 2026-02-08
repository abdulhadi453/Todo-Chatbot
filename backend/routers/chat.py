"""
Chat API router for the AI chatbot feature.
This module defines the API endpoints for chat functionality.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
import uuid

from backend.database import get_session
from backend.auth.jwt import get_user_id_from_token
from backend.services.chat_service import ChatService
from backend.services.agent_service import AgentService
from backend.ai.stub_ai import get_ai_response
from backend.models.conversation import Conversation
from backend.models.message import Message
from backend.exceptions.chat_exceptions import UnauthorizedAccessException, ConversationNotFoundException

router = APIRouter(prefix="/api/{user_id}", tags=["chat"])


@router.post("/chat", response_model=Dict[str, Any])
async def chat_endpoint(
    user_id: str,
    message_request: Dict[str, Any],
    session: Session = Depends(get_session)
):
    """
    Handle chat interactions between user and AI assistant.
    Creates new conversation if none provided, adds user message, processes with AI, and returns AI response.

    Args:
        user_id: ID of the authenticated user
        message_request: Request body containing conversation_id (optional), message (required), and model_preferences (optional)
        session: Database session

    Returns:
        Dict: Response containing conversation_id, response, timestamp, message_id, and conversation_title
    """
    try:
        # Validate user_id format
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        # Extract request parameters
        conversation_id_str = message_request.get("conversation_id")
        user_message = message_request.get("message")
        model_preferences = message_request.get("model_preferences", {})

        # Validate required parameters
        if not user_message or len(user_message.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content is required and cannot be empty"
            )

        # Validate message length
        if len(user_message) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content exceeds maximum length of 10,000 characters"
            )

        # Initialize chat service
        chat_service = ChatService(session)

        # Validate message content
        is_valid, error_msg = chat_service.validate_message_content(user_message)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Get or create conversation
        conversation: Conversation
        if conversation_id_str:
            # Validate conversation ID format
            try:
                conversation_id = uuid.UUID(conversation_id_str)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation ID format"
                )

            # Verify user has access to this conversation
            conversation = chat_service.get_conversation_by_id(conversation_id, user_uuid)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have access to this conversation"
                )
        else:
            # Create new conversation
            conversation = chat_service.create_conversation(user_uuid)
            # Auto-generate a title based on the first message if none provided
            if not conversation.title:
                title_preview = user_message[:50] + "..." if len(user_message) > 50 else user_message
                conversation.title = f"Chat: {title_preview}"
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)
                session.commit()

        # Create user message in the conversation
        user_message_obj = chat_service.create_message(
            conversation_id=conversation.id,
            user_id=user_uuid,
            content=user_message,
            role="user"
        )

        # Generate AI response
        try:
            # Create context for AI response generation
            conversation_context = {
                "conversation_id": str(conversation.id),
                "user_id": str(user_uuid),
                "message_count": len(conversation.messages) + 1  # Including the one we just added
            }

            ai_response = get_ai_response(user_message, context=conversation_context)
        except Exception as e:
            # If AI response generation fails, return an error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate AI response: {str(e)}"
            )

        # Save AI response to the conversation
        ai_message_obj = chat_service.create_message(
            conversation_id=conversation.id,
            user_id=user_uuid,  # The AI message is still associated with the user's conversation
            content=ai_response,
            role="assistant"
        )

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        # Prepare response
        response_data = {
            "conversation_id": str(conversation.id),
            "response": ai_response,
            "timestamp": datetime.utcnow().isoformat(),
            "message_id": str(ai_message_obj.id),
            "conversation_title": conversation.title
        }

        return response_data

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation(
    user_id: str,
    conversation_id: str,
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific conversation and its message history.

    Args:
        user_id: ID of the authenticated user
        conversation_id: ID of the conversation to retrieve
        session: Database session

    Returns:
        Dict containing conversation details and message history
    """
    try:
        # Validate user_id format
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        # Validate conversation_id format
        try:
            conv_uuid = uuid.UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID format"
            )

        # Initialize chat service
        chat_service = ChatService(session)

        # Verify user has access to this conversation
        conversation = chat_service.get_conversation_by_id(conv_uuid, user_uuid)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have access to this conversation"
            )

        # Get all messages for this conversation
        messages = chat_service.get_messages_for_conversation(conv_uuid, user_uuid)

        # Prepare response
        conversation_data = {
            "conversation": {
                "id": str(conversation.id),
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat()
            },
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        }

        return conversation_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: str,
    session: Session = Depends(get_session)
):
    """
    Delete a specific conversation and all its messages.

    Args:
        user_id: ID of the authenticated user
        conversation_id: ID of the conversation to delete
        session: Database session

    Returns:
        Empty response with 204 status code on success
    """
    try:
        # Validate user_id format
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        # Validate conversation_id format
        try:
            conv_uuid = uuid.UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID format"
            )

        # Initialize chat service
        chat_service = ChatService(session)

        # Attempt to delete the conversation
        success = chat_service.delete_conversation(conv_uuid, user_uuid)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have access to this conversation or conversation not found"
            )

        return {"message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/conversations", response_model=List[Dict[str, Any]])
async def get_user_conversations(
    user_id: str,
    session: Session = Depends(get_session)
):
    """
    Retrieve all conversations for the specified user, ordered by most recent activity.

    Args:
        user_id: ID of the authenticated user
        session: Database session

    Returns:
        List of conversations with id, title, created_at, updated_at, and message_count
    """
    try:
        # Validate user_id format
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        # Initialize chat service
        chat_service = ChatService(session)

        # Get user's conversations
        conversations = chat_service.get_user_conversations(user_uuid)

        # Prepare response data
        result = []
        for conv in conversations:
            # Count messages in each conversation
            message_count_stmt = select(Message).where(Message.conversation_id == conv.id)
            messages = session.exec(message_count_stmt).all()
            message_count = len(messages)

            result.append({
                "id": str(conv.id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": message_count
            })

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


from sqlalchemy import func