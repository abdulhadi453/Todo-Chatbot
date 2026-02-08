"""
Configuration settings for the AI agent functionality.
This module defines all configuration values for the agent system.
"""

import os
from typing import Optional
from datetime import timedelta


class AgentConfig:
    """
    Configuration class for AI agent settings.
    Contains all configuration values needed for agent functionality.
    """

    # API Keys and Service Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AGENT_MODEL_NAME: str = os.getenv("AGENT_MODEL_NAME", "gpt-4-turbo-preview")

    # JWT and Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-for-development")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Agent Settings
    AGENT_TEMPERATURE: float = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
    AGENT_MAX_TOKENS: int = int(os.getenv("AGENT_MAX_TOKENS", "1000"))
    AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))

    # MCP (Model Context Protocol) Server Settings
    MCP_SERVER_ENABLED: bool = os.getenv("MCP_SERVER_ENABLED", "true").lower() == "true"
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:8080")
    MCP_CLIENT_TIMEOUT: int = int(os.getenv("MCP_CLIENT_TIMEOUT", "10"))

    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/todo_db")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))

    # Rate Limiting
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "30"))
    RATE_LIMIT_WINDOW_MINUTES: int = int(os.getenv("RATE_LIMIT_WINDOW_MINUTES", "1"))

    # Message and Conversation Limits
    MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "10000"))  # Characters
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))  # Number of messages
    CONVERSATION_AUTO_EXPIRY_HOURS: int = int(os.getenv("CONVERSATION_AUTO_EXPIRY_HOURS", "24"))

    # Security Settings
    ENABLE_INPUT_SANITIZATION: bool = os.getenv("ENABLE_INPUT_SANITIZATION", "true").lower() == "true"
    ENABLE_OUTPUT_FILTERING: bool = os.getenv("ENABLE_OUTPUT_FILTERING", "true").lower() == "true"
    BLOCK_SUSPICIOUS_CONTENT: bool = os.getenv("BLOCK_SUSPICIOUS_CONTENT", "true").lower() == "true"

    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/agent.log")

    # Caching Settings
    ENABLE_AGENT_CACHE: bool = os.getenv("ENABLE_AGENT_CACHE", "false").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes

    # Error Handling
    ENABLE_DETAILED_ERROR_MESSAGES: bool = os.getenv("ENABLE_DETAILED_ERROR_MESSAGES", "false").lower() == "true"
    ERROR_RESPONSE_TEMPLATE: str = os.getenv("ERROR_RESPONSE_TEMPLATE", "An error occurred while processing your request.")

    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate that required configuration values are set.

        Returns:
            True if all required configurations are present, False otherwise
        """
        # Check that we have an OpenAI API key if not using stub
        if not os.getenv("USE_STUB_AGENT", "false").lower() == "true":
            if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "":
                print("WARNING: OPENAI_API_KEY is not set. Agent functionality may not work properly.")
                return False

        # Validate numeric values are positive
        if cls.ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
            print("ERROR: ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
            return False

        if cls.AGENT_MAX_TOKENS <= 0:
            print("ERROR: AGENT_MAX_TOKENS must be positive")
            return False

        if cls.AGENT_TIMEOUT_SECONDS <= 0:
            print("ERROR: AGENT_TIMEOUT_SECONDS must be positive")
            return False

        if cls.RATE_LIMIT_MAX_REQUESTS <= 0:
            print("ERROR: RATE_LIMIT_MAX_REQUESTS must be positive")
            return False

        if cls.MAX_MESSAGE_LENGTH <= 0:
            print("ERROR: MAX_MESSAGE_LENGTH must be positive")
            return False

        return True

    @classmethod
    def get_access_token_expire_delta(cls) -> timedelta:
        """
        Get the access token expiration time as a timedelta.

        Returns:
            Timedelta representing the expiration duration
        """
        return timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)

    @classmethod
    def get_rate_limit_window_delta(cls) -> timedelta:
        """
        Get the rate limit window as a timedelta.

        Returns:
            Timedelta representing the rate limit window duration
        """
        return timedelta(minutes=cls.RATE_LIMIT_WINDOW_MINUTES)

    @classmethod
    def get_conversation_expiry_delta(cls) -> timedelta:
        """
        Get the conversation expiry time as a timedelta.

        Returns:
            Timedelta representing the conversation expiry duration
        """
        return timedelta(hours=cls.CONVERSATION_AUTO_EXPIRY_HOURS)

    @classmethod
    def is_production_mode(cls) -> bool:
        """
        Check if the application is running in production mode.

        Returns:
            True if in production mode, False otherwise
        """
        env = os.getenv("ENVIRONMENT", "development").lower()
        return env == "production"

    @classmethod
    def get_database_connection_kwargs(cls) -> dict:
        """
        Get database connection parameters.

        Returns:
            Dictionary with database connection parameters
        """
        return {
            "pool_size": cls.DATABASE_POOL_SIZE,
            "pool_timeout": cls.DATABASE_POOL_TIMEOUT,
            "echo": not cls.is_production_mode()  # Enable SQL logging in non-production
        }

    @classmethod
    def get_agent_parameters(cls) -> dict:
        """
        Get parameters for agent configuration.

        Returns:
            Dictionary with agent configuration parameters
        """
        return {
            "model": cls.AGENT_MODEL_NAME,
            "temperature": cls.AGENT_TEMPERATURE,
            "max_tokens": cls.AGENT_MAX_TOKENS,
            "timeout": cls.AGENT_TIMEOUT_SECONDS
        }

    @classmethod
    def get_mcp_client_config(cls) -> dict:
        """
        Get MCP client configuration.

        Returns:
            Dictionary with MCP client settings
        """
        return {
            "server_url": cls.MCP_SERVER_URL,
            "timeout": cls.MCP_CLIENT_TIMEOUT,
            "enabled": cls.MCP_SERVER_ENABLED
        }

    @classmethod
    def get_rate_limit_settings(cls) -> dict:
        """
        Get rate limiting configuration.

        Returns:
            Dictionary with rate limit settings
        """
        return {
            "max_requests": cls.RATE_LIMIT_MAX_REQUESTS,
            "window_minutes": cls.RATE_LIMIT_WINDOW_MINUTES
        }

    @classmethod
    def get_security_settings(cls) -> dict:
        """
        Get security-related configuration.

        Returns:
            Dictionary with security settings
        """
        return {
            "input_sanitization": cls.ENABLE_INPUT_SANITIZATION,
            "output_filtering": cls.ENABLE_OUTPUT_FILTERING,
            "block_suspicious_content": cls.BLOCK_SUSPICIOUS_CONTENT
        }

    @classmethod
    def get_logging_config(cls) -> dict:
        """
        Get logging configuration.

        Returns:
            Dictionary with logging settings
        """
        return {
            "level": cls.LOG_LEVEL,
            "to_file": cls.LOG_TO_FILE,
            "file_path": cls.LOG_FILE_PATH
        }

    @classmethod
    def get_cache_config(cls) -> dict:
        """
        Get caching configuration.

        Returns:
            Dictionary with cache settings
        """
        return {
            "enabled": cls.ENABLE_AGENT_CACHE,
            "ttl_seconds": cls.CACHE_TTL_SECONDS
        }


# Global instance of the configuration
agent_config = AgentConfig()

# Validate configuration on import
if not AgentConfig.validate_config():
    if not agent_config.is_production_mode():
        print("WARNING: Some configuration values are invalid or missing. Using defaults.")
    else:
        print("ERROR: Invalid configuration. Please check your environment variables.")
        exit(1)