"""
Custom exceptions for the chatbot feature.
"""

from fastapi import HTTPException, status


class ChatException(HTTPException):
    """
    Base exception class for chat-related errors.
    """
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class UnauthorizedAccessException(ChatException):
    """
    Raised when a user attempts to access resources they don't have permission for.
    """
    def __init__(self, detail: str = "Access denied: Insufficient permissions"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class ConversationNotFoundException(ChatException):
    """
    Raised when a conversation is not found.
    """
    def __init__(self, detail: str = "Conversation not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class UserNotFoundException(ChatException):
    """
    Raised when a user is not found.
    """
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class InvalidMessageContentException(ChatException):
    """
    Raised when message content is invalid.
    """
    def __init__(self, detail: str = "Invalid message content"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class RateLimitExceededException(ChatException):
    """
    Raised when a user exceeds the rate limit for chat requests.
    """
    def __init__(self, detail: str = "Rate limit exceeded. Please try again later."):
        super().__init__(detail=detail, status_code=status.HTTP_429_TOO_MANY_REQUESTS)