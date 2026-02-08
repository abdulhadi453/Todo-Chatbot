"""
Secure logging utilities for the AI agent feature.
Provides structured, secure logging for agent interactions while protecting sensitive data.
"""

import logging
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class SecurityLogLevel(Enum):
    """
    Security-focused log levels that indicate the sensitivity of the logged information.
    """
    LOW = "low"           # General operational info
    MEDIUM = "medium"     # User actions and standard requests
    HIGH = "high"         # Potentially sensitive data access
    CRITICAL = "critical" # Security events, errors, violations


class SecureAgentLogger:
    """
    Secure logger specifically designed for AI agent interactions.
    Implements data sanitization and structured logging for security and compliance.
    """

    def __init__(self, name: str = "secure_agent", level: int = logging.INFO):
        """
        Initialize the secure agent logger.

        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Avoid duplicate handlers
        if not self.logger.handlers:
            # Create a handler that writes to a file
            file_handler = logging.FileHandler("agent_secure.log")
            file_handler.setLevel(level)

            # Create a handler that writes to console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # Create a formatter for the log messages
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.propagate = False  # Prevent propagation to root logger

        # Patterns for sensitive data that should be masked
        self.sensitive_patterns = [
            # Email patterns
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            # Common password fields
            r'(?i)(password|pass|pwd|token|key)["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
            # Credit card patterns
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            # Phone number patterns (simple)
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        ]

    def _sanitize_sensitive_data(self, data: str) -> str:
        """
        Sanitize sensitive data in the provided string.

        Args:
            data: String to sanitize

        Returns:
            Sanitized string with sensitive data masked
        """
        if not isinstance(data, str):
            data = str(data)

        sanitized = data

        for pattern in self.sensitive_patterns:
            if "password" in pattern.lower() or "token" in pattern.lower():
                # Special handling for key-value pairs like passwords and tokens
                sanitized = re.sub(
                    pattern,
                    lambda m: f'{m.group(1)}: "***REDACTED***"',
                    sanitized
                )
            else:
                # Mask other sensitive patterns
                sanitized = re.sub(pattern, "***REDACTED***", sanitized)

        return sanitized

    def _log_structure(self,
                     level: SecurityLogLevel,
                     user_id: Optional[str],
                     event_type: str,
                     details: Dict[str, Any],
                     message: str = ""):
        """
        Create a structured log entry with security considerations.

        Args:
            level: Security level of the log
            user_id: ID of the user involved
            event_type: Type of event being logged
            details: Additional details about the event
            message: Human-readable message
        """
        timestamp = datetime.utcnow().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "security_level": level.value,
            "user_id": user_id,
            "event_type": event_type,
            "message": message,
            "details": self._sanitize_sensitive_data(json.dumps(details)) if details else "{}"
        }

        # Sanitize the entire entry to remove any sensitive data
        sanitized_message = self._sanitize_sensitive_data(f"{event_type}: {message}")
        log_entry_sanitized = {**log_entry, "message": sanitized_message}

        # Format the entry for logging
        log_message = json.dumps(log_entry_sanitized, indent=2, default=str)

        if level == SecurityLogLevel.CRITICAL:
            self.logger.critical(log_message)
        elif level in [SecurityLogLevel.HIGH, SecurityLogLevel.CRITICAL]:
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)

    def log_user_interaction(self,
                           user_id: str,
                           message: str,
                           response: str,
                           tools_used: list = None,
                           execution_time: float = 0.0):
        """
        Log user interaction with the AI agent.

        Args:
            user_id: ID of the interacting user
            message: Original user message
            response: Agent's response
            tools_used: List of tools invoked during processing
            execution_time: Time taken to process the interaction
        """
        details = {
            "original_message_length": len(message) if message else 0,
            "response_length": len(response) if response else 0,
            "tools_used": tools_used or [],
            "execution_time_ms": execution_time * 1000,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Don't log the actual message content for privacy, just metadata
        sanitized_msg = f"User interaction with {len(message) if message else 0} char message"
        self._log_structure(
            level=SecurityLogLevel.MEDIUM,
            user_id=user_id,
            event_type="agent_interaction",
            details=details,
            message=sanitized_msg
        )

    def log_tool_execution(self,
                         user_id: str,
                         tool_name: str,
                         arguments: Dict[str, Any],
                         result: Dict[str, Any],
                         success: bool = True):
        """
        Log execution of an AI agent tool.

        Args:
            user_id: ID of the user who triggered the tool
            tool_name: Name of the tool executed
            arguments: Arguments passed to the tool (sanitized)
            result: Result of the tool execution (summary only)
            success: Whether the tool execution was successful
        """
        # Only log argument keys and value types, not actual values for sensitive data
        arg_summary = {}
        for key, value in arguments.items():
            if key.lower() in ['password', 'token', 'key', 'auth', 'secret', 'credential']:
                arg_summary[key] = "***REDACTED***"
            elif isinstance(value, (str, int, float, bool)):
                arg_summary[key] = f"<{type(value).__name__}>"
            else:
                arg_summary[key] = f"<{type(value).__name__}_value>"

        details = {
            "tool_name": tool_name,
            "arguments_summary": arg_summary,
            "result_success": success,
            "result_summary": {k: v for k, v in result.items() if k in ['success', 'message', 'id']} if result else {},
            "timestamp": datetime.utcnow().isoformat()
        }

        status = "successful" if success else "failed"
        message = f"Tool '{tool_name}' execution {status} for user {user_id[:8]}..."

        self._log_structure(
            level=SecurityLogLevel.MEDIUM if success else SecurityLogLevel.HIGH,
            user_id=user_id,
            event_type="tool_execution",
            details=details,
            message=message
        )

    def log_security_event(self,
                         event_type: str,
                         user_id: Optional[str],
                         details: Dict[str, Any],
                         severity: SecurityLogLevel = SecurityLogLevel.HIGH):
        """
        Log a security-related event.

        Args:
            event_type: Type of security event
            user_id: ID of the user involved (if any)
            details: Additional details about the security event
            severity: Severity level of the event
        """
        message = f"Security event: {event_type}"
        self._log_structure(
            level=severity,
            user_id=user_id,
            event_type=event_type,
            details=details,
            message=message
        )

    def log_authentication_event(self,
                               user_id: str,
                               event_type: str,
                               success: bool,
                               source_ip: Optional[str] = None):
        """
        Log authentication-related events for the agent system.

        Args:
            user_id: ID of the user involved
            event_type: Type of authentication event (login, logout, token_refresh, etc.)
            success: Whether the authentication action was successful
            source_ip: IP address of the request (if available)
        """
        details = {
            "event_type": event_type,
            "success": success,
            "source_ip": source_ip,
            "timestamp": datetime.utcnow().isoformat()
        }

        status = "successful" if success else "failed"
        message = f"Authentication {event_type} {status} for user {user_id[:8]}..."

        security_level = SecurityLogLevel.LOW if success else SecurityLogLevel.HIGH
        self._log_structure(
            level=security_level,
            user_id=user_id,
            event_type="auth_event",
            details=details,
            message=message
        )

    def log_error(self,
                 user_id: Optional[str],
                 error_type: str,
                 error_message: str,
                 context: Optional[Dict[str, Any]] = None):
        """
        Log an error in the agent system.

        Args:
            user_id: ID of the user when error occurred (if applicable)
            error_type: Type/classification of the error
            error_message: Error message (sensitive parts will be sanitized)
            context: Additional context about the error
        """
        sanitized_error = self._sanitize_sensitive_data(error_message)

        details = {
            "error_type": error_type,
            "error_message_preview": sanitized_error[:200] + ("..." if len(sanitized_error) > 200 else ""),
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }

        message = f"Error occurred: {error_type} - {sanitized_error[:100]}..."

        self._log_structure(
            level=SecurityLogLevel.HIGH,
            user_id=user_id,
            event_type="system_error",
            details=details,
            message=message
        )


# Global instance of the secure logger
secure_agent_logger = SecureAgentLogger("secure_agent")


# Convenience functions for common logging scenarios
def log_agent_interaction(user_id: str, message: str, response: str, execution_time: float = 0.0):
    """Convenience function to log agent interactions."""
    secure_agent_logger.log_user_interaction(user_id, message, response, execution_time=execution_time)


def log_tool_usage(user_id: str, tool_name: str, arguments: Dict[str, Any], result: Dict[str, Any], success: bool):
    """Convenience function to log tool usage."""
    secure_agent_logger.log_tool_execution(user_id, tool_name, arguments, result, success)


def log_security_incident(event_type: str, user_id: Optional[str], details: Dict[str, Any]):
    """Convenience function to log security incidents."""
    secure_agent_logger.log_security_event(event_type, user_id, details, SecurityLogLevel.HIGH)


def log_system_error(user_id: Optional[str], error_type: str, error_message: str, context: Dict[str, Any] = None):
    """Convenience function to log system errors."""
    secure_agent_logger.log_error(user_id, error_type, error_message, context)


# Preserve backward compatibility with the original chat_logger
chat_logger = logging.getLogger("chatbot")
chat_logger.setLevel(logging.INFO)

# Create a handler that writes to a file
file_handler = logging.FileHandler("chatbot.log")
file_handler.setLevel(logging.INFO)

# Create a handler that writes to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter for the log messages
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
if not chat_logger.handlers:
    chat_logger.addHandler(file_handler)
    chat_logger.addHandler(console_handler)
    chat_logger.propagate = False  # Prevent propagation to root logger


def log_chat_interaction(
    user_id: str,
    conversation_id: str,
    user_message: str,
    ai_response: str,
    duration_ms: Optional[float] = None,
    extra_data: Optional[Dict[str, Any]] = None
):
    """
    Log a chat interaction with structured data.

    Args:
        user_id: ID of the user
        conversation_id: ID of the conversation
        user_message: The message sent by the user
        ai_response: The response from the AI
        duration_ms: Time taken for processing in milliseconds
        extra_data: Additional data to include in the log
    """
    log_data = {
        "event": "chat_interaction",
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "conversation_id": conversation_id,
        "user_message": user_message,
        "ai_response": ai_response,
        "duration_ms": duration_ms,
        "extra": extra_data or {}
    }

    chat_logger.info(json.dumps(log_data))


def log_conversation_start(user_id: str, conversation_id: str, initial_message: str):
    """
    Log the start of a new conversation.

    Args:
        user_id: ID of the user
        conversation_id: ID of the new conversation
        initial_message: The first message in the conversation
    """
    log_data = {
        "event": "conversation_start",
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "conversation_id": conversation_id,
        "initial_message": initial_message
    }

    chat_logger.info(json.dumps(log_data))


def log_conversation_end(user_id: str, conversation_id: str, message_count: int):
    """
    Log the end of a conversation.

    Args:
        user_id: ID of the user
        conversation_id: ID of the ended conversation
        message_count: Total number of messages in the conversation
    """
    log_data = {
        "event": "conversation_end",
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "conversation_id": conversation_id,
        "message_count": message_count
    }

    chat_logger.info(json.dumps(log_data))


def log_error(error_message: str, user_id: Optional[str] = None, conversation_id: Optional[str] = None):
    """
    Log an error with optional context.

    Args:
        error_message: The error message to log
        user_id: ID of the user related to the error
        conversation_id: ID of the conversation related to the error
    """
    log_data = {
        "event": "error",
        "timestamp": datetime.utcnow().isoformat(),
        "error_message": error_message,
        "user_id": user_id,
        "conversation_id": conversation_id
    }

    chat_logger.error(json.dumps(log_data))


def log_api_request(
    user_id: str,
    endpoint: str,
    method: str,
    ip_address: str,
    duration_ms: float,
    status_code: int
):
    """
    Log an API request for monitoring and analytics.

    Args:
        user_id: ID of the user making the request
        endpoint: The API endpoint that was called
        method: HTTP method (GET, POST, etc.)
        ip_address: IP address of the client
        duration_ms: Time taken to process the request
        status_code: HTTP status code returned
    """
    log_data = {
        "event": "api_request",
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "endpoint": endpoint,
        "method": method,
        "ip_address": ip_address,
        "duration_ms": duration_ms,
        "status_code": status_code
    }

    chat_logger.info(json.dumps(log_data))


__all__ = [
    'SecureAgentLogger',
    'SecurityLogLevel',
    'secure_agent_logger',
    'log_agent_interaction',
    'log_tool_usage',
    'log_security_incident',
    'log_system_error',
    'log_chat_interaction',
    'log_conversation_start',
    'log_conversation_end',
    'log_error',
    'log_api_request'
]