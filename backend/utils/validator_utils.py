"""
Utility functions for validation operations.
These utilities provide common validation patterns and helpers.
"""

import re
from typing import Any, Dict, List, Union, Optional
from datetime import datetime, date
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """
    Validate email format using regex pattern.

    Args:
        email: Email string to validate

    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (simple pattern).

    Args:
        phone: Phone number string to validate

    Returns:
        True if phone number is valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False

    # Allow digits, spaces, hyphens, parentheses, and plus signs
    pattern = r'^[\d\s\-\(\+)\+]+$'
    return re.match(pattern, phone) is not None


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        True if URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that all required fields are present in the data.

    Args:
        data: Dictionary of data to validate
        required_fields: List of required field names

    Returns:
        List of missing field names
    """
    missing_fields = []

    for field in required_fields:
        if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
            missing_fields.append(field)

    return missing_fields


def validate_length(text: str, min_length: Optional[int] = None, max_length: Optional[int] = None) -> bool:
    """
    Validate string length.

    Args:
        text: String to validate
        min_length: Minimum allowed length (optional)
        max_length: Maximum allowed length (optional)

    Returns:
        True if length is valid, False otherwise
    """
    if text is None:
        return False

    if not isinstance(text, str):
        return False

    length = len(text)

    if min_length is not None and length < min_length:
        return False

    if max_length is not None and length > max_length:
        return False

    return True


def validate_date(date_string: str, format_string: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format.

    Args:
        date_string: Date string to validate
        format_string: Expected date format

    Returns:
        True if date is valid, False otherwise
    """
    if not date_string or not isinstance(date_string, str):
        return False

    try:
        datetime.strptime(date_string, format_string)
        return True
    except ValueError:
        return False


def validate_datetime(datetime_string: str, format_string: str = "%Y-%m-%d %H:%M:%S") -> bool:
    """
    Validate datetime string format.

    Args:
        datetime_string: Datetime string to validate
        format_string: Expected datetime format

    Returns:
        True if datetime is valid, False otherwise
    """
    if not datetime_string or not isinstance(datetime_string, str):
        return False

    try:
        datetime.strptime(datetime_string, format_string)
        return True
    except ValueError:
        return False


def sanitize_input(text: str, allowed_patterns: Optional[List[str]] = None) -> str:
    """
    Sanitize input string by removing potentially dangerous characters.

    Args:
        text: String to sanitize
        allowed_patterns: Optional list of regex patterns to allow

    Returns:
        Sanitized string
    """
    if not text or not isinstance(text, str):
        return ""

    # Remove potentially dangerous characters by default
    sanitized = text.strip()

    # Remove script tags and other potentially harmful content
    harmful_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>'
    ]

    for pattern in harmful_patterns:
        import re
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

    return sanitized


def validate_numeric_range(
    value: Union[int, float, str],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None
) -> bool:
    """
    Validate numeric value is within specified range.

    Args:
        value: Value to validate
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)

    Returns:
        True if value is valid, False otherwise
    """
    try:
        num_value = float(value)
    except (TypeError, ValueError):
        return False

    if min_value is not None and num_value < min_value:
        return False

    if max_value is not None and num_value > max_value:
        return False

    return True


def validate_list_items(items: List[Any], validator_func, *args, **kwargs) -> bool:
    """
    Validate all items in a list using a validator function.

    Args:
        items: List of items to validate
        validator_func: Function to use for validation
        *args, **kwargs: Arguments to pass to validator function

    Returns:
        True if all items are valid, False otherwise
    """
    if not isinstance(items, list):
        return False

    for item in items:
        if not validator_func(item, *args, **kwargs):
            return False

    return True


def validate_dict_structure(data: Dict[str, Any], structure: Dict[str, type]) -> Dict[str, List[str]]:
    """
    Validate that a dictionary matches the expected structure.

    Args:
        data: Dictionary to validate
        structure: Expected structure mapping field names to types

    Returns:
        Dictionary with validation results including any errors
    """
    errors = []

    for field, expected_type in structure.items():
        if field not in data:
            errors.append(f"Missing field: {field}")
        else:
            value = data[field]
            if value is not None and not isinstance(value, expected_type):
                errors.append(f"Field {field} has wrong type: expected {expected_type.__name__}, got {type(value).__name__}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_alphanumeric(text: str, allow_spaces: bool = False) -> bool:
    """
    Validate that string contains only alphanumeric characters (optionally with spaces).

    Args:
        text: String to validate
        allow_spaces: Whether to allow spaces

    Returns:
        True if string is valid, False otherwise
    """
    if not text or not isinstance(text, str):
        return False

    pattern = r'^[a-zA-Z0-9\s]+$' if allow_spaces else r'^[a-zA-Z0-9]+$'
    return re.match(pattern, text) is not None


def validate_json_serializable(obj: Any) -> bool:
    """
    Validate that an object is JSON serializable.

    Args:
        obj: Object to validate

    Returns:
        True if object is JSON serializable, False otherwise
    """
    import json

    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False