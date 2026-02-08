"""
Agent API router for the AI assistant integration.
This module defines the API endpoints for agent functionality.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
import uuid

from backend.database import get_session
from backend.auth.jwt import get_current_user_id
from backend.services.openai_agent_service import OpenAIAgentService
from backend.services.todo_tools import TodoTools
from backend.models.agent_session import AgentSession
from backend.models.agent_message import AgentMessage
from backend.config.agent_config import AgentConfig
import os

router = APIRouter(prefix="/api/{user_id}", tags=["agent"])


@router.post("/chat", response_model=Dict[str, Any])
async def agent_chat(
    user_id: str,
    message_request: Dict[str, Any],
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Handle chat interactions between user and AI agent.

    This endpoint processes user messages, routes them to the appropriate AI service,
    executes any required tools, and returns the agent's response.

    Args:
        user_id: ID of the authenticated user (from URL path)
        message_request: Request body containing message content and optional conversation ID
        session: Database session
        current_user_id: ID of the authenticated user (from token)

    Returns:
        Dict containing conversation_id, response, timestamp, message_id, and conversation_title
    """
    # Verify that the user_id in the URL matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's agent session"
        )

    try:
        # Validate user_id format
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        # Extract required parameters
        message_text = message_request.get("message")
        conversation_id_str = message_request.get("conversation_id")
        model_preferences = message_request.get("model_preferences", {})

        # Validate required parameters
        if not message_text or len(message_text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content is required and cannot be empty"
            )

        # Check if we should use stub AI
        use_stub = os.getenv("USE_STUB_AGENT", "false").lower() == "true"

        # Initialize OpenAI agent service
        openai_agent_service = OpenAIAgentService(session, use_stub=use_stub)

        # Process the message using OpenAI Agent service
        try:
            result = openai_agent_service.process_message(
                user_id=user_id,
                message=message_text,
                session_id=conversation_id_str
            )

            # Extract conversation info
            session_id = result.get("session_id")
            response_text = result.get("response")
            message_id = result.get("message_id")

            # Return response in the expected format
            return {
                "conversation_id": session_id,
                "response": response_text,
                "timestamp": result.get("timestamp"),
                "message_id": message_id,
                "conversation_title": f"Chat: {message_text[:50]}..." if len(message_text) > 50 else f"Chat: {message_text}",
                "tool_calls": result.get("tool_calls"),
                "tool_results": result.get("tool_results"),
                "using_stub": result.get("using_stub", False)
            }

        except Exception as e:
            # If OpenAI fails, fall back to stub AI
            from backend.ai.stub_ai import get_ai_response

            context = {
                "conversation_id": conversation_id_str,
                "user_id": user_id,
                "error": str(e)
            }

            ai_response = get_ai_response(message_text, context)

            # Create or use existing session
            if conversation_id_str:
                try:
                    conversation_id = uuid.UUID(conversation_id_str)
                except ValueError:
                    conversation_id = uuid.uuid4()
            else:
                conversation_id = uuid.uuid4()

            # Store messages using fallback
            agent_service = openai_agent_service
            user_message = agent_service.add_message_to_session(
                session_id=str(conversation_id),
                user_id=user_id,
                role="user",
                content=message_text
            )

            ai_message = agent_service.add_message_to_session(
                session_id=str(conversation_id),
                user_id=user_id,
                role="assistant",
                content=f"[Fallback AI: {str(e)}] {ai_response}"
            )

            return {
                "conversation_id": str(conversation_id),
                "response": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
                "message_id": str(ai_message.id),
                "conversation_title": f"Chat: {message_text[:50]}..." if len(message_text) > 50 else f"Chat: {message_text}",
                "using_stub": True,
                "error": str(e)
            }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/conversations", response_model=List[Dict[str, Any]])
async def get_agent_conversations(
    user_id: str,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve all agent conversations for the specified user, ordered by most recent activity.

    Args:
        user_id: ID of the authenticated user (from URL path)
        session: Database session
        current_user_id: ID of the authenticated user (from token)

    Returns:
        List of conversation details with id, title, timestamps, and message count
    """
    # Verify that the user_id in the URL matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's conversations"
        )

    try:
        # Validate user_id format
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        # Initialize OpenAI agent service
        use_stub = os.getenv("USE_STUB_AGENT", "false").lower() == "true"
        openai_agent_service = OpenAIAgentService(session, use_stub=use_stub)

        # Get user's conversations
        conversations = openai_agent_service.get_user_conversations(user_uuid)

        # Prepare response data
        result = []
        for conv in conversations:
            # Count messages in each conversation
            message_count_stmt = select(AgentMessage).where(AgentMessage.session_id == conv.id)
            messages = session.exec(message_count_stmt).all()
            message_count = len(messages)

            result.append({
                "id": str(conv.id),
                "title": conv.title or f"Chat: {conv.created_at.strftime('%Y-%m-%d')}",
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


@router.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_agent_conversation(
    user_id: str,
    conversation_id: str,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve a specific agent conversation and its message history.

    Args:
        user_id: ID of the authenticated user (from URL path)
        conversation_id: ID of the conversation to retrieve
        session: Database session
        current_user_id: ID of the authenticated user (from token)

    Returns:
        Dict containing conversation details and message history
    """
    # Verify that the user_id in the URL matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's conversation"
        )

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

        # Initialize OpenAI agent service
        use_stub = os.getenv("USE_STUB_AGENT", "false").lower() == "true"
        openai_agent_service = OpenAIAgentService(session, use_stub=use_stub)

        # Get the conversation
        conversation = openai_agent_service.get_agent_session(conv_uuid, user_uuid)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get messages for the conversation
        messages = openai_agent_service.get_session_messages(conv_uuid, user_uuid)

        # Prepare response
        conversation_data = {
            "conversation": {
                "id": str(conversation.id),
                "title": conversation.title or f"Chat: {conversation.created_at.strftime('%Y-%m-%d')}",
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
async def delete_agent_conversation(
    user_id: str,
    conversation_id: str,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete a specific agent conversation and all its messages.

    Args:
        user_id: ID of the authenticated user (from URL path)
        conversation_id: ID of the conversation to delete
        session: Database session
        current_user_id: ID of the authenticated user (from token)

    Returns:
        Success message if deletion is successful
    """
    # Verify that the user_id in the URL matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot delete another user's conversation"
        )

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

        # Initialize OpenAI agent service
        use_stub = os.getenv("USE_STUB_AGENT", "false").lower() == "true"
        openai_agent_service = OpenAIAgentService(session, use_stub=use_stub)

        # Delete the conversation
        success = openai_agent_service.delete_conversation(conv_uuid, user_uuid)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        return {"message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


from datetime import datetime
from sqlmodel import select