"""
Utility functions for creating standardized responses.
These utilities help maintain consistent response schemas across all endpoints.
"""

from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse


def create_success_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized success response.

    Args:
        data: The main data payload
        message: Optional success message
        status_code: HTTP status code (default 200)
        metadata: Optional additional metadata

    Returns:
        Dictionary with standardized success response format
    """
    response = {
        "success": True,
        "status_code": status_code,
        "data": data,
        "message": message or "Operation completed successfully"
    }

    if metadata:
        response["metadata"] = metadata

    return response


def create_error_response(
    error: str,
    message: Optional[str] = None,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        error: Error type or code
        message: Error message
        status_code: HTTP status code (default 400)
        details: Optional error details

    Returns:
        Dictionary with standardized error response format
    """
    response = {
        "success": False,
        "status_code": status_code,
        "error": error,
        "message": message or error
    }

    if details:
        response["details"] = details

    return response


def create_paginated_response(
    data: list,
    total: int,
    page: int,
    page_size: int,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized paginated response.

    Args:
        data: List of items in current page
        total: Total number of items
        page: Current page number
        page_size: Size of current page
        message: Optional message

    Returns:
        Dictionary with standardized paginated response format
    """
    pagination_info = {
        "current_page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": (total + page_size - 1) // page_size,  # Ceiling division
        "has_next": (page * page_size) < total,
        "has_previous": page > 1
    }

    return {
        "success": True,
        "status_code": 200,
        "data": data,
        "message": message or f"Retrieved {len(data)} of {total} items",
        "pagination": pagination_info
    }


def format_api_response(
    success: bool,
    data: Any = None,
    message: str = "",
    status_code: int = 200,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generic API response formatter.

    Args:
        success: Whether the operation was successful
        data: Response data payload
        message: Response message
        status_code: HTTP status code
        error: Error information if applicable

    Returns:
        Formatted API response dictionary
    """
    response = {
        "success": success,
        "status_code": status_code,
        "data": data,
        "message": message
    }

    if not success and error:
        response["error"] = error

    return response


def response_to_json(response_data: Dict[str, Any], status_code: int = 200) -> JSONResponse:
    """
    Convert response dictionary to FastAPI JSONResponse object.

    Args:
        response_data: Dictionary with response data
        status_code: HTTP status code

    Returns:
        FastAPI JSONResponse object
    """
    return JSONResponse(content=response_data, status_code=status_code)