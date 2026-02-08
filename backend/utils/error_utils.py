"""
Utility functions for error handling.
These utilities provide consistent error handling patterns across the application.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from backend.utils.response_utils import create_error_response


class AppError(Exception):
    """
    Base application error class.
    All custom application errors should inherit from this.
    """
    def __init__(self, message: str, error_code: str = "APP_ERROR", details: Optional[Dict[str, Any]] = None, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary representation.

        Returns:
            Dictionary representation of the error
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }


class ValidationError(AppError):
    """
    Error for validation failures.
    """
    def __init__(self, message: str, field: str = "", value: Any = None):
        details = {"field": field, "value": value} if field else {}
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class AuthenticationError(AppError):
    """
    Error for authentication failures.
    """
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(AppError):
    """
    Error for authorization failures.
    """
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundError(AppError):
    """
    Error for resource not found.
    """
    def __init__(self, message: str = "Resource not found", resource_type: str = "", resource_id: str = ""):
        details = {"resource_type": resource_type, "resource_id": resource_id} if resource_type else {}
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )


class DatabaseError(AppError):
    """
    Error for database operations failures.
    """
    def __init__(self, message: str = "Database operation failed", operation: str = ""):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ServiceError(AppError):
    """
    Error for service layer failures.
    """
    def __init__(self, message: str = "Service operation failed", service: str = ""):
        details = {"service": service} if service else {}
        super().__init__(
            message=message,
            error_code="SERVICE_ERROR",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def handle_error(
    error: Exception,
    context: str = "",
    user_id: Optional[str] = None,
    request_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Handle an error and return a standardized error response.

    Args:
        error: The exception to handle
        context: Context where the error occurred
        user_id: ID of the user when applicable
        request_details: Details about the request that caused the error

    Returns:
        Standardized error response dictionary
    """
    # Log error details for debugging
    error_details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "user_id": user_id
    }

    if request_details:
        error_details.update(request_details)

    # Determine the error type and return appropriate response
    if isinstance(error, AppError):
        # Return custom application error response
        return create_error_response(
            error=error.error_code,
            message=error.message,
            status_code=error.status_code,
            details=error.details
        )
    elif isinstance(error, HTTPException):
        # Return HTTP exception response
        return create_error_response(
            error="HTTP_ERROR",
            message=error.detail,
            status_code=error.status_code,
            details={"headers": getattr(error, "headers", None)}
        )
    else:
        # Handle unexpected errors
        return create_error_response(
            error="UNEXPECTED_ERROR",
            message="An unexpected error occurred",
            status_code=500,
            details={
                "original_error_type": type(error).__name__,
                "original_error_message": str(error),
                "context": context
            }
        )


def raise_validation_error(
    field: str,
    value: Any,
    message: str = ""
) -> None:
    """
    Raise a validation error.

    Args:
        field: Field that failed validation
        value: Value that failed validation
        message: Custom error message
    """
    if not message:
        message = f"Validation failed for field '{field}' with value '{value}'"

    raise ValidationError(message, field, value)


def raise_authentication_error(message: str = "Authentication failed") -> None:
    """
    Raise an authentication error.

    Args:
        message: Custom error message
    """
    raise AuthenticationError(message)


def raise_authorization_error(message: str = "Access denied") -> None:
    """
    Raise an authorization error.

    Args:
        message: Custom error message
    """
    raise AuthorizationError(message)


def raise_not_found_error(resource_type: str, resource_id: str) -> None:
    """
    Raise a not found error.

    Args:
        resource_type: Type of resource that wasn't found
        resource_id: ID of the resource that wasn't found
    """
    message = f"{resource_type} with ID '{resource_id}' not found"
    raise NotFoundError(message, resource_type, resource_id)


def create_http_exception(
    status_code: int,
    detail: str,
    headers: Optional[Dict[str, str]] = None
) -> HTTPException:
    """
    Create an HTTP exception with standardized structure.

    Args:
        status_code: HTTP status code
        detail: Detail message
        headers: Additional headers

    Returns:
        HTTPException instance
    """
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers
    )


def convert_error_to_http_response(
    error: Exception,
    context: str = "",
    user_id: Optional[str] = None,
    request_details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Convert an error to an HTTP response.

    Args:
        error: The exception to convert
        context: Context where the error occurred
        user_id: ID of the user when applicable
        request_details: Details about the request that caused the error

    Returns:
        FastAPI JSONResponse object
    """
    error_response = handle_error(error, context, user_id, request_details)
    status_code = error_response.get("status_code", 500)
    return JSONResponse(content=error_response, status_code=status_code)


def safe_execute(
    func,
    *args,
    error_handler=None,
    default_return=None,
    **kwargs
):
    """
    Safely execute a function, catching exceptions and handling them appropriately.

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        error_handler: Custom error handler function
        default_return: Default value to return if an error occurs
        **kwargs: Keyword arguments for the function

    Returns:
        Result of the function or default_return if error occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if error_handler:
            return error_handler(e)
        else:
            # Log the error or handle it as needed
            print(f"Error in safe_execute: {e}")
            return default_return


def validate_and_handle(
    data: Dict[str, Any],
    required_fields: list,
    custom_validators: Optional[Dict[str, callable]] = None
) -> Dict[str, Any]:
    """
    Validate data and handle validation errors.

    Args:
        data: Data to validate
        required_fields: List of required fields
        custom_validators: Dictionary mapping field names to validation functions

    Returns:
        Dictionary with 'valid' boolean and 'errors' list if invalid
    """
    errors = []

    # Check required fields
    for field in required_fields:
        if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
            errors.append(f"Missing required field: {field}")

    # Run custom validators
    if custom_validators:
        for field, validator in custom_validators.items():
            if field in data and data[field] is not None:
                try:
                    if not validator(data[field]):
                        errors.append(f"Validation failed for field: {field}")
                except Exception as e:
                    errors.append(f"Validation error for field '{field}': {str(e)}")

    if errors:
        return {"valid": False, "errors": errors}

    return {"valid": True, "data": data}


def handle_database_error(db_exception: Exception, operation: str = "") -> AppError:
    """
    Handle database-specific errors and return appropriate AppError.

    Args:
        db_exception: The database exception that occurred
        operation: The operation that was being performed

    Returns:
        AppError instance with appropriate details
    """
    error_msg = str(db_exception)

    # Identify specific database error types and return appropriate error
    if "duplicate" in error_msg.lower() or "unique constraint" in error_msg.lower():
        return DatabaseError(f"A record with this identifier already exists", operation)
    elif "foreign key" in error_msg.lower() or "referential integrity" in error_msg.lower():
        return DatabaseError(f"A related record does not exist", operation)
    elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
        return DatabaseError(f"Database connection failed", operation)
    else:
        return DatabaseError(f"Database operation failed: {error_msg}", operation)