"""
ErrorHandler class - Centralized error response handling.
This handler provides consistent error responses and logging across the application.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from backend.utils.response_utils import create_error_response
from backend.utils.error_utils import AppError, ValidationError, AuthenticationError, AuthorizationError, NotFoundError, DatabaseError, ServiceError
from backend.logging.app_logger import app_logger


class ErrorHandler:
    """
    Centralized error handling class.
    Provides consistent error responses and logging across the application.
    """

    def __init__(self):
        """
        Initialize the ErrorHandler.
        """
        pass

    def handle_error(
        self,
        request: Request,
        exc: Exception,
        context: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> JSONResponse:
        """
        Handle an exception and return a standardized error response.

        Args:
            request: The incoming request
            exc: The exception to handle
            context: Context where the error occurred
            user_id: ID of the user when applicable

        Returns:
            FastAPI JSONResponse with standardized error format
        """
        # Log the error
        app_logger.error(
            f"Error occurred: {type(exc).__name__}: {str(exc)}",
            extra_data={
                "type": "error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "request_method": request.method,
                "request_url": str(request.url),
                "context": context,
                "user_id": user_id
            }
        )

        # Handle different exception types
        if isinstance(exc, ValidationError):
            return self._handle_validation_error(exc, request)
        elif isinstance(exc, AuthenticationError):
            return self._handle_authentication_error(exc, request)
        elif isinstance(exc, AuthorizationError):
            return self._handle_authorization_error(exc, request)
        elif isinstance(exc, NotFoundError):
            return self._handle_not_found_error(exc, request)
        elif isinstance(exc, DatabaseError):
            return self._handle_database_error(exc, request)
        elif isinstance(exc, ServiceError):
            return self._handle_service_error(exc, request)
        elif isinstance(exc, AppError):
            return self._handle_app_error(exc, request)
        elif isinstance(exc, HTTPException):
            return self._handle_http_exception(exc, request)
        else:
            # Handle unexpected errors
            return self._handle_unexpected_error(exc, request, context)

    def _handle_validation_error(self, exc: ValidationError, request: Request) -> JSONResponse:
        """
        Handle validation errors specifically.

        Args:
            exc: ValidationError instance
            request: The incoming request

        Returns:
            JSONResponse with validation error details
        """
        response_data = create_error_response(
            error="VALIDATION_ERROR",
            message=exc.message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "field": exc.field,
                "value": exc.value,
                "error_code": exc.error_code
            }
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_400_BAD_REQUEST)

    def _handle_authentication_error(self, exc: AuthenticationError, request: Request) -> JSONResponse:
        """
        Handle authentication errors specifically.

        Args:
            exc: AuthenticationError instance
            request: The incoming request

        Returns:
            JSONResponse with authentication error details
        """
        response_data = create_error_response(
            error="AUTHENTICATION_ERROR",
            message=exc.message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_401_UNAUTHORIZED)

    def _handle_authorization_error(self, exc: AuthorizationError, request: Request) -> JSONResponse:
        """
        Handle authorization errors specifically.

        Args:
            exc: AuthorizationError instance
            request: The incoming request

        Returns:
            JSONResponse with authorization error details
        """
        response_data = create_error_response(
            error="AUTHORIZATION_ERROR",
            message=exc.message,
            status_code=status.HTTP_403_FORBIDDEN
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_403_FORBIDDEN)

    def _handle_not_found_error(self, exc: NotFoundError, request: Request) -> JSONResponse:
        """
        Handle not found errors specifically.

        Args:
            exc: NotFoundError instance
            request: The incoming request

        Returns:
            JSONResponse with not found error details
        """
        response_data = create_error_response(
            error="NOT_FOUND_ERROR",
            message=exc.message,
            status_code=status.HTTP_404_NOT_FOUND,
            details={
                "resource_type": exc.details.get("resource_type", ""),
                "resource_id": exc.details.get("resource_id", "")
            }
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_404_NOT_FOUND)

    def _handle_database_error(self, exc: DatabaseError, request: Request) -> JSONResponse:
        """
        Handle database errors specifically.

        Args:
            exc: DatabaseError instance
            request: The incoming request

        Returns:
            JSONResponse with database error details
        """
        response_data = create_error_response(
            error="DATABASE_ERROR",
            message=exc.message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={
                "operation": exc.details.get("operation", ""),
                "error_code": exc.error_code
            }
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_service_error(self, exc: ServiceError, request: Request) -> JSONResponse:
        """
        Handle service layer errors specifically.

        Args:
            exc: ServiceError instance
            request: The incoming request

        Returns:
            JSONResponse with service error details
        """
        response_data = create_error_response(
            error="SERVICE_ERROR",
            message=exc.message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={
                "service": exc.details.get("service", ""),
                "error_code": exc.error_code
            }
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_app_error(self, exc: AppError, request: Request) -> JSONResponse:
        """
        Handle application-specific errors.

        Args:
            exc: AppError instance
            request: The incoming request

        Returns:
            JSONResponse with application error details
        """
        response_data = create_error_response(
            error=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details
        )

        return JSONResponse(content=response_data, status_code=exc.status_code)

    def _handle_http_exception(self, exc: HTTPException, request: Request) -> JSONResponse:
        """
        Handle FastAPI HTTP exceptions.

        Args:
            exc: HTTPException instance
            request: The incoming request

        Returns:
            JSONResponse with HTTP exception details
        """
        response_data = create_error_response(
            error="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code,
            details=getattr(exc, 'headers', None)
        )

        return JSONResponse(content=response_data, status_code=exc.status_code)

    def _handle_unexpected_error(self, exc: Exception, request: Request, context: Optional[str] = None) -> JSONResponse:
        """
        Handle unexpected errors that don't fall into specific categories.

        Args:
            exc: Exception instance
            request: The incoming request
            context: Context where the error occurred

        Returns:
            JSONResponse with unexpected error details
        """
        # For security reasons, we don't expose internal error details to the client
        error_message = "An unexpected error occurred"
        error_code = "UNEXPECTED_ERROR"

        response_data = create_error_response(
            error=error_code,
            message=error_message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={
                "original_error_type": type(exc).__name__,
                "original_error_message": str(exc),
                "context": context,
                "request_method": request.method,
                "request_url": str(request.url)
            }
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_error_by_status_code(self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None) -> JSONResponse:
        """
        Create an error response based on a status code.

        Args:
            status_code: HTTP status code
            message: Error message
            details: Additional error details

        Returns:
            JSONResponse with the specified status code and message
        """
        # Map status codes to error codes
        error_codes_map = {
            status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
            status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
            status.HTTP_403_FORBIDDEN: "FORBIDDEN",
            status.HTTP_404_NOT_FOUND: "NOT_FOUND",
            status.HTTP_409_CONFLICT: "CONFLICT",
            status.HTTP_422_UNPROCESSABLE_ENTITY: "UNPROCESSABLE_ENTITY",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
            status.HTTP_502_BAD_GATEWAY: "BAD_GATEWAY",
            status.HTTP_503_SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
        }

        error_code = error_codes_map.get(status_code, "UNKNOWN_ERROR")

        response_data = create_error_response(
            error=error_code,
            message=message,
            status_code=status_code,
            details=details or {}
        )

        return JSONResponse(content=response_data, status_code=status_code)

    def handle_multiple_errors(self, errors: List[Dict[str, Any]], status_code: int = status.HTTP_400_BAD_REQUEST) -> JSONResponse:
        """
        Handle multiple errors at once.

        Args:
            errors: List of error dictionaries with 'field', 'message', and 'code' keys
            status_code: HTTP status code for the response

        Returns:
            JSONResponse with multiple error details
        """
        response_data = create_error_response(
            error="MULTIPLE_ERRORS",
            message=f"Validation failed with {len(errors)} error(s)",
            status_code=status_code,
            details={
                "errors": errors,
                "total_errors": len(errors)
            }
        )

        return JSONResponse(content=response_data, status_code=status_code)

    def handle_business_rule_violation(self, message: str, rule: str, context: Optional[Dict[str, Any]] = None) -> JSONResponse:
        """
        Handle business rule violations.

        Args:
            message: Error message
            rule: The violated business rule
            context: Additional context information

        Returns:
            JSONResponse with business rule violation details
        """
        response_data = create_error_response(
            error="BUSINESS_RULE_VIOLATION",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "rule_violated": rule,
                "context": context
            }
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_400_BAD_REQUEST)

    def handle_rate_limit_exceeded(self, retry_after: Optional[int] = None) -> JSONResponse:
        """
        Handle rate limit exceeded errors.

        Args:
            retry_after: Number of seconds after which the request may be retried

        Returns:
            JSONResponse with rate limit exceeded details
        """
        details = {}
        if retry_after:
            details["retry_after"] = retry_after

        response_data = create_error_response(
            error="RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )

        response_headers = {}
        if retry_after:
            response_headers["Retry-After"] = str(retry_after)

        return JSONResponse(content=response_data, status_code=status.HTTP_429_TOO_MANY_REQUESTS, headers=response_headers)

    def handle_timeout_error(self, message: str = "Request timed out", timeout_duration: Optional[int] = None) -> JSONResponse:
        """
        Handle timeout errors.

        Args:
            message: Error message
            timeout_duration: Duration that caused the timeout

        Returns:
            JSONResponse with timeout error details
        """
        details = {}
        if timeout_duration:
            details["timeout_duration"] = timeout_duration

        response_data = create_error_response(
            error="TIMEOUT_ERROR",
            message=message,
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            details=details
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_408_REQUEST_TIMEOUT)


# Global error handler instance
error_handler = ErrorHandler()


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch and handle errors globally.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Get user ID from request if available (may be in headers after authentication)
            user_id = request.headers.get("X-User-ID")  # This would come from authentication middleware

            # Handle the error using the centralized error handler
            return error_handler.handle_error(request, exc, user_id=user_id)