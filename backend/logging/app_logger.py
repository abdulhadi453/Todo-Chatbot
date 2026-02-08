"""
Centralized application logging system.
Provides structured logging for various application components.
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum


class LogLevel(Enum):
    """
    Enum for log levels to ensure consistency.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppLogger:
    """
    Centralized application logger with structured logging capabilities.
    """

    def __init__(self, name: str = "app", level: str = "INFO"):
        """
        Initialize the application logger.

        Args:
            name: Name of the logger
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Avoid adding multiple handlers if logger already has them
        if not self.logger.handlers:
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # Create formatter for structured logging
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)

            # Add handler to logger
            self.logger.addHandler(console_handler)

    def _log(self, level: LogLevel, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """
        Internal logging method with structured data support.

        Args:
            level: Log level
            message: Log message
            extra_data: Additional structured data to log
        """
        if extra_data:
            # Log structured message with extra data
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level.value,
                "message": message,
                "extra": extra_data
            }
            self.logger.log(getattr(logging, level.value), json.dumps(log_entry))
        else:
            # Log simple message
            self.logger.log(getattr(logging, level.value), message)

    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """
        Log debug message.

        Args:
            message: Debug message
            extra_data: Additional structured data
        """
        self._log(LogLevel.DEBUG, message, extra_data)

    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """
        Log info message.

        Args:
            message: Info message
            extra_data: Additional structured data
        """
        self._log(LogLevel.INFO, message, extra_data)

    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """
        Log warning message.

        Args:
            message: Warning message
            extra_data: Additional structured data
        """
        self._log(LogLevel.WARNING, message, extra_data)

    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """
        Log error message.

        Args:
            message: Error message
            extra_data: Additional structured data
        """
        self._log(LogLevel.ERROR, message, extra_data)

    def critical(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """
        Log critical message.

        Args:
            message: Critical message
            extra_data: Additional structured data
        """
        self._log(LogLevel.CRITICAL, message, extra_data)

    def log_request(self, method: str, endpoint: str, status_code: int, duration: float, user_id: Optional[str] = None):
        """
        Log HTTP request information.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Request endpoint
            status_code: HTTP status code
            duration: Request duration in seconds
            user_id: ID of the user making the request
        """
        extra_data = {
            "type": "request",
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration * 1000,  # Convert to milliseconds
        }

        if user_id:
            extra_data["user_id"] = user_id

        self.info(f"HTTP {method} {endpoint} {status_code}", extra_data)

    def log_database_operation(self, operation: str, table: str, duration: float, rows_affected: Optional[int] = None):
        """
        Log database operation information.

        Args:
            operation: Type of operation (SELECT, INSERT, UPDATE, DELETE)
            table: Name of the table
            duration: Operation duration in seconds
            rows_affected: Number of affected rows (for write operations)
        """
        extra_data = {
            "type": "database",
            "operation": operation,
            "table": table,
            "duration_ms": duration * 1000,  # Convert to milliseconds
        }

        if rows_affected is not None:
            extra_data["rows_affected"] = rows_affected

        self.info(f"DB {operation} on {table}", extra_data)

    def log_security_event(self, event_type: str, user_id: Optional[str] = None, ip_address: Optional[str] = None, details: Optional[str] = None):
        """
        Log security-related events.

        Args:
            event_type: Type of security event
            user_id: ID of the user involved
            ip_address: IP address of the request
            details: Additional details about the event
        """
        extra_data = {
            "type": "security",
            "event": event_type,
        }

        if user_id:
            extra_data["user_id"] = user_id

        if ip_address:
            extra_data["ip_address"] = ip_address

        if details:
            extra_data["details"] = details

        self.warning(f"Security event: {event_type}", extra_data)

    def log_performance_metric(self, metric_name: str, value: float, unit: str = "", tags: Optional[Dict[str, str]] = None):
        """
        Log performance metrics.

        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            tags: Additional tags for categorization
        """
        extra_data = {
            "type": "performance",
            "metric": metric_name,
            "value": value,
        }

        if unit:
            extra_data["unit"] = unit

        if tags:
            extra_data["tags"] = tags

        self.info(f"Performance: {metric_name} = {value}{unit}", extra_data)


class ErrorTracker:
    """
    Specialized error tracking and reporting component.
    """

    def __init__(self, logger: AppLogger):
        """
        Initialize error tracker with logger.

        Args:
            logger: AppLogger instance for logging errors
        """
        self.logger = logger

    def log_exception(self, exception: Exception, context: Optional[str] = None, user_id: Optional[str] = None):
        """
        Log exception with detailed information.

        Args:
            exception: Exception instance
            context: Context where the exception occurred
            user_id: ID of the user when applicable
        """
        extra_data = {
            "type": "exception",
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        }

        if context:
            extra_data["context"] = context

        if user_id:
            extra_data["user_id"] = user_id

        self.logger.error(f"Exception occurred: {type(exception).__name__}: {str(exception)}", extra_data)

    def log_error_with_trace(self, message: str, traceback_info: Optional[str] = None, context: Optional[str] = None):
        """
        Log error with optional traceback information.

        Args:
            message: Error message
            traceback_info: Traceback information
            context: Context where the error occurred
        """
        extra_data = {
            "type": "error_with_trace",
            "message": message,
        }

        if traceback_info:
            extra_data["traceback"] = traceback_info

        if context:
            extra_data["context"] = context

        self.logger.error(message, extra_data)

    def track_error_frequency(self, error_code: str, error_message: str, endpoint: str = ""):
        """
        Track frequency of specific errors.

        Args:
            error_code: Code or identifier for the error
            error_message: Error message
            endpoint: Endpoint where error occurred
        """
        extra_data = {
            "type": "error_frequency",
            "error_code": error_code,
            "error_message": error_message,
        }

        if endpoint:
            extra_data["endpoint"] = endpoint

        self.logger.warning(f"Error occurred: {error_code}", extra_data)


# Global application logger instance
app_logger = AppLogger()
error_tracker = ErrorTracker(app_logger)