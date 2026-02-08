"""
Configuration settings for the chatbot feature.
"""

import os
from typing import Optional


class ChatConfig:
    """
    Configuration class for chatbot feature settings.
    """

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./todo_backend.db")

    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-for-development")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # AI service settings
    USE_STUB_AI: bool = os.getenv("USE_STUB_AI", "true").lower() == "true"
    AI_RESPONSE_DELAY_MIN: float = float(os.getenv("AI_RESPONSE_DELAY_MIN", "0.5"))
    AI_RESPONSE_DELAY_MAX: float = float(os.getenv("AI_RESPONSE_DELAY_MAX", "1.5"))

    # Rate limiting
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "30"))
    RATE_LIMIT_WINDOW_SIZE: int = int(os.getenv("RATE_LIMIT_WINDOW_SIZE", "60"))  # in seconds

    # Message settings
    MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "10000"))
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))

    # Conversation settings
    CONVERSATION_TITLE_LENGTH: int = int(os.getenv("CONVERSATION_TITLE_LENGTH", "200"))
    MAX_CONVERSATIONS_PER_USER: int = int(os.getenv("MAX_CONVERSATIONS_PER_USER", "100"))
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "50"))

    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "chatbot.log")

    # Security settings
    ENABLE_RATE_LIMITING: bool = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() == "true"
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000").split(",")

    @classmethod
    def get_database_url(cls) -> str:
        """Get the database URL from environment or default."""
        return cls.DATABASE_URL

    @classmethod
    def get_jwt_secret_key(cls) -> str:
        """Get the JWT secret key from environment or default."""
        if cls.JWT_SECRET_KEY == "fallback-secret-key-for-development":
            print("WARNING: Using fallback JWT secret key. Please set JWT_SECRET_KEY environment variable.")
        return cls.JWT_SECRET_KEY

    @classmethod
    def get_max_message_length(cls) -> int:
        """Get the maximum allowed message length."""
        return cls.MAX_MESSAGE_LENGTH

    @classmethod
    def get_rate_limit_settings(cls) -> dict:
        """Get rate limiting configuration."""
        return {
            "max_requests": cls.RATE_LIMIT_MAX_REQUESTS,
            "window_size": cls.RATE_LIMIT_WINDOW_SIZE
        }

    @classmethod
    def get_ai_settings(cls) -> dict:
        """Get AI service configuration."""
        return {
            "use_stub": cls.USE_STUB_AI,
            "delay_min": cls.AI_RESPONSE_DELAY_MIN,
            "delay_max": cls.AI_RESPONSE_DELAY_MAX
        }

    @classmethod
    def get_cors_origins(cls) -> list:
        """Get the list of allowed origins for CORS."""
        return [origin.strip() for origin in cls.ALLOWED_ORIGINS if origin.strip()]

    @classmethod
    def is_rate_limiting_enabled(cls) -> bool:
        """Check if rate limiting is enabled."""
        return cls.ENABLE_RATE_LIMITING


# Create a global instance of the config
chat_config = ChatConfig()