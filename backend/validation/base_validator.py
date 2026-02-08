"""
Base validation classes and schemas.
These classes provide standardized validation patterns across the application.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from backend.utils.validator_utils import validate_required_fields, validate_email, validate_length


class ValidationError(Exception):
    """
    Exception raised when validation fails.
    """
    def __init__(self, message: str, field: str = "", value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value


class BaseValidator(ABC):
    """
    Abstract base class for all validators.
    Provides common functionality and interface for validation operations.
    """

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize validator with optional schema.

        Args:
            schema: Optional validation schema definition
        """
        self.schema = schema or {}
        self.errors: List[ValidationError] = []

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate data against schema and custom rules.

        Args:
            data: Data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        self.errors.clear()
        is_valid = self._validate_data(data)
        return is_valid, self.errors

    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Internal method to validate data.
        Subclasses should implement specific validation logic.

        Args:
            data: Data to validate

        Returns:
            True if data is valid, False otherwise
        """
        # Call abstract method for custom validation
        custom_valid = self.custom_validate(data)

        # Validate required fields
        required_fields = self.schema.get("required", [])
        missing_fields = validate_required_fields(data, required_fields)

        for field in missing_fields:
            self.errors.append(ValidationError(
                f"Field '{field}' is required",
                field=field,
                value=None
            ))

        # Validate field rules
        field_rules = self.schema.get("fields", {})
        for field, rules in field_rules.items():
            if field in data:
                self._validate_field(field, data[field], rules)

        return custom_valid and len(missing_fields) == 0 and len(self.errors) == 0

    def _validate_field(self, field_name: str, field_value: Any, rules: Dict[str, Any]) -> None:
        """
        Validate individual field based on rules.

        Args:
            field_name: Name of the field
            field_value: Value of the field
            rules: Validation rules for the field
        """
        # Check type
        if "type" in rules:
            expected_type = rules["type"]
            if not isinstance(field_value, expected_type):
                self.errors.append(ValidationError(
                    f"Field '{field_name}' must be of type {expected_type.__name__}",
                    field=field_name,
                    value=field_value
                ))
                return  # Skip further validation if type is wrong

        # Check required
        if rules.get("required", False) and (field_value is None or field_value == ""):
            self.errors.append(ValidationError(
                f"Field '{field_name}' is required",
                field=field_name,
                value=field_value
            ))

        # Check length
        if "min_length" in rules or "max_length" in rules:
            min_len = rules.get("min_length", 0)
            max_len = rules.get("max_length", float('inf'))
            if isinstance(field_value, str) and not validate_length(field_value, min_len, max_len):
                self.errors.append(ValidationError(
                    f"Field '{field_name}' length must be between {min_len} and {max_len} characters",
                    field=field_name,
                    value=field_value
                ))

        # Check email format
        if rules.get("is_email", False):
            if not validate_email(str(field_value)):
                self.errors.append(ValidationError(
                    f"Field '{field_name}' must be a valid email address",
                    field=field_name,
                    value=field_value
                ))

        # Check custom validation function
        if "custom_validator" in rules:
            validator_func = rules["custom_validator"]
            if callable(validator_func) and not validator_func(field_value):
                self.errors.append(ValidationError(
                    f"Field '{field_name}' failed custom validation",
                    field=field_name,
                    value=field_value
                ))

        # Check allowed values
        if "allowed_values" in rules:
            allowed = rules["allowed_values"]
            if field_value not in allowed:
                self.errors.append(ValidationError(
                    f"Field '{field_name}' must be one of {allowed}",
                    field=field_name,
                    value=field_value
                ))

    @abstractmethod
    def custom_validate(self, data: Dict[str, Any]) -> bool:
        """
        Custom validation logic specific to the validator subclass.

        Args:
            data: Data to validate

        Returns:
            True if data is valid, False otherwise
        """
        pass

    def add_error(self, message: str, field: str = "", value: Any = None) -> None:
        """
        Add a validation error.

        Args:
            message: Error message
            field: Field name associated with error
            value: Value that caused the error
        """
        self.errors.append(ValidationError(message, field, value))

    def get_errors(self) -> List[ValidationError]:
        """
        Get list of validation errors.

        Returns:
            List of ValidationError instances
        """
        return self.errors

    def clear_errors(self) -> None:
        """
        Clear all validation errors.
        """
        self.errors.clear()


class SchemaValidator(BaseValidator):
    """
    Concrete validator that uses JSON Schema-like structure.
    """

    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize with schema definition.

        Args:
            schema: Schema definition in JSON Schema-like format
        """
        super().__init__(schema)

    def custom_validate(self, data: Dict[str, Any]) -> bool:
        """
        Custom validation for schema validation.

        Args:
            data: Data to validate

        Returns:
            True if data matches schema, False otherwise
        """
        # Additional schema-specific validation can be added here
        return True

    def validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validate data against schema definition.

        Args:
            data: Data to validate
            schema: Schema to validate against

        Returns:
            True if valid, False otherwise
        """
        # This would contain more complex schema validation logic
        return True


class RequestValidator(BaseValidator):
    """
    Base class for request validation.
    Provides common patterns for validating HTTP requests.
    """

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize with optional schema.

        Args:
            schema: Validation schema for the request
        """
        super().__init__(schema)

    def validate_request_params(self, params: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate request parameters.

        Args:
            params: Request parameters to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        return self.validate(params)

    def validate_request_body(self, body: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate request body.

        Args:
            body: Request body to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        return self.validate(body)

    def custom_validate(self, data: Dict[str, Any]) -> bool:
        """
        Custom validation logic for request validation.

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        # Default implementation - subclasses should override
        return True


class UserValidator(RequestValidator):
    """
    Validator for user-related data.
    """

    def custom_validate(self, data: Dict[str, Any]) -> bool:
        """
        Custom validation for user data.

        Args:
            data: User data to validate

        Returns:
            True if valid, False otherwise
        """
        # Add any user-specific validation logic here
        return True


class TaskValidator(RequestValidator):
    """
    Validator for task-related data.
    """

    def custom_validate(self, data: Dict[str, Any]) -> bool:
        """
        Custom validation for task data.

        Args:
            data: Task data to validate

        Returns:
            True if valid, False otherwise
        """
        # Add any task-specific validation logic here
        return True