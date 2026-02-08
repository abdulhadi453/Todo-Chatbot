"""
AuthValidator class - Handles authentication-specific validation rules.
This validator follows the single responsibility principle for authentication validation.
"""

from typing import Any, Dict, List, Tuple, Optional
from backend.validation.base_validator import BaseValidator, ValidationError
from backend.utils.validator_utils import validate_email


class AuthValidator(BaseValidator):
    """
    Validator class for authentication-specific operations.
    Validates user registration, login, password changes, and other auth-specific operations.
    """

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize the AuthValidator.

        Args:
            schema: Optional validation schema definition for auth operations
        """
        # Define default schema if not provided
        if schema is None:
            schema = {
                "required": [],
                "fields": {
                    "email": {
                        "type": str,
                        "required": True,
                        "is_email": True
                    },
                    "password": {
                        "type": str,
                        "required": True,
                        "min_length": 8,
                        "max_length": 128
                    },
                    "username": {
                        "type": str,
                        "min_length": 3,
                        "max_length": 50
                    },
                    "confirm_password": {
                        "type": str,
                        "required": True
                    }
                }
            }

        super().__init__(schema)

    def custom_validate(self, data: Dict[str, Any]) -> bool:
        """
        Custom validation logic specific to authentication operations.

        Args:
            data: Data to validate

        Returns:
            True if data is valid, False otherwise
        """
        is_valid = True

        # Validate email if present
        if "email" in data:
            email = data["email"]
            if not isinstance(email, str):
                self.add_error("Email must be a string", "email", email)
                is_valid = False
            elif not validate_email(email):
                self.add_error("Email must be a valid email address", "email", email)
                is_valid = False

        # Validate password if present
        if "password" in data:
            password = data["password"]
            if not isinstance(password, str):
                self.add_error("Password must be a string", "password", password)
                is_valid = False
            elif len(password) < 8:
                self.add_error("Password must be at least 8 characters long", "password", password)
                is_valid = False
            elif len(password) > 128:
                self.add_error("Password must be less than 128 characters long", "password", password)
                is_valid = False
            # Additional password strength validation could be added here
            elif not self._validate_password_strength(password):
                self.add_error("Password must contain at least one uppercase letter, lowercase letter, and number", "password", password)
                is_valid = False

        # Validate username if present
        if "username" in data:
            username = data["username"]
            if username is not None:
                if not isinstance(username, str):
                    self.add_error("Username must be a string", "username", username)
                    is_valid = False
                elif len(username) < 3 or len(username) > 50:
                    self.add_error("Username must be between 3 and 50 characters", "username", username)
                    is_valid = False
                elif not username.replace("_", "").replace("-", "").isalnum():  # Allow alphanumeric, underscore, hyphen
                    self.add_error("Username can only contain letters, numbers, underscores, and hyphens", "username", username)
                    is_valid = False

        # Validate confirm_password if present
        if "confirm_password" in data:
            confirm_password = data["confirm_password"]
            if not isinstance(confirm_password, str):
                self.add_error("Confirm password must be a string", "confirm_password", confirm_password)
                is_valid = False
            elif "password" in data and confirm_password != data["password"]:
                self.add_error("Password and confirm password must match", "confirm_password", confirm_password)
                is_valid = False

        # Validate first_name if present
        if "first_name" in data:
            first_name = data["first_name"]
            if first_name is not None:
                if not isinstance(first_name, str):
                    self.add_error("First name must be a string", "first_name", first_name)
                    is_valid = False
                elif len(first_name) > 100:
                    self.add_error("First name must be less than 100 characters", "first_name", first_name)
                    is_valid = False

        # Validate last_name if present
        if "last_name" in data:
            last_name = data["last_name"]
            if last_name is not None:
                if not isinstance(last_name, str):
                    self.add_error("Last name must be a string", "last_name", last_name)
                    is_valid = False
                elif len(last_name) > 100:
                    self.add_error("Last name must be less than 100 characters", "last_name", last_name)
                    is_valid = False

        # Validate bio if present
        if "bio" in data:
            bio = data["bio"]
            if bio is not None:
                if not isinstance(bio, str):
                    self.add_error("Bio must be a string", "bio", bio)
                    is_valid = False
                elif len(bio) > 500:
                    self.add_error("Bio must be less than 500 characters", "bio", bio)
                    is_valid = False

        return is_valid

    def validate_registration_data(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate user registration data.

        Args:
            data: Registration data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        required_fields = ["email", "password"]

        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
                self.add_error(f"Field '{field}' is required for registration", field, data.get(field))

        # Run general validation
        return self.validate(data)

    def validate_login_data(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate user login data.

        Args:
            data: Login data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        required_fields = ["email", "password"]

        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
                self.add_error(f"Field '{field}' is required for login", field, data.get(field))

        # Run general validation
        return self.validate(data)

    def validate_password_change(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate password change data.

        Args:
            data: Password change data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        required_fields = ["old_password", "new_password", "confirm_new_password"]

        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
                self.add_error(f"Field '{field}' is required for password change", field, data.get(field))

        # Validate that new passwords match
        if "new_password" in data and "confirm_new_password" in data:
            if data["new_password"] != data["confirm_new_password"]:
                self.add_error("New password and confirm new password must match", "confirm_new_password", data.get("confirm_new_password"))

        # Run general validation
        return self.validate(data)

    def validate_password_reset_request(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate password reset request data.

        Args:
            data: Password reset request data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        required_fields = ["email"]

        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
                self.add_error(f"Field '{field}' is required for password reset request", field, data.get(field))

        # Run general validation
        return self.validate(data)

    def validate_password_reset(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate password reset data.

        Args:
            data: Password reset data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        required_fields = ["email", "new_password", "confirm_new_password", "reset_token"]

        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
                self.add_error(f"Field '{field}' is required for password reset", field, data.get(field))

        # Validate that new passwords match
        if "new_password" in data and "confirm_new_password" in data:
            if data["new_password"] != data["confirm_new_password"]:
                self.add_error("New password and confirm new password must match", "confirm_new_password", data.get("confirm_new_password"))

        # Run general validation
        return self.validate(data)

    def validate_user_profile_update(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate user profile update data.

        Args:
            data: Profile update data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        # At least one field must be provided for update
        allowed_fields = ["email", "username", "first_name", "last_name", "bio", "avatar_url", "timezone", "language"]

        update_provided = any(field in data for field in allowed_fields)

        if not update_provided:
            self.add_error("At least one field must be provided for profile update", "profile_update", data)

        # Run general validation
        return self.validate(data)

    def validate_email(self, email: str) -> bool:
        """
        Validate an email address.

        Args:
            email: Email to validate

        Returns:
            True if email is valid, False otherwise
        """
        if not isinstance(email, str):
            return False

        return validate_email(email)

    def validate_password_strength(self, password: str) -> bool:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            True if password meets strength requirements, False otherwise
        """
        if not isinstance(password, str):
            return False

        return self._validate_password_strength(password)

    def _validate_password_strength(self, password: str) -> bool:
        """
        Internal method to validate password strength.
        This is a basic implementation - in a real app you'd want more sophisticated rules.

        Args:
            password: Password to validate

        Returns:
            True if password meets strength requirements, False otherwise
        """
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit

    def validate_username(self, username: str) -> bool:
        """
        Validate a username.

        Args:
            username: Username to validate

        Returns:
            True if username is valid, False otherwise
        """
        if username is None:
            return True  # Username is optional

        if not isinstance(username, str):
            return False

        if len(username) < 3 or len(username) > 50:
            return False

        # Allow only alphanumeric, underscore, and hyphen
        return username.replace("_", "").replace("-", "").isalnum()

    def validate_profile_field(self, field_name: str, field_value: Any) -> Tuple[bool, List[ValidationError]]:
        """
        Validate a single profile field.

        Args:
            field_name: Name of the field to validate
            field_value: Value of the field to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        data = {field_name: field_value}
        return self.validate(data)

    def validate_multi_factor_setup(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate multi-factor authentication setup data.

        Args:
            data: Multi-factor setup data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        required_fields = ["user_id", "factor_type"]

        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
                self.add_error(f"Field '{field}' is required for multi-factor setup", field, data.get(field))

        # Validate factor type
        if "factor_type" in data:
            factor_type = data["factor_type"]
            allowed_types = ["sms", "email", "totp", "backup_codes"]
            if factor_type not in allowed_types:
                self.add_error(f"Factor type must be one of: {', '.join(allowed_types)}", "factor_type", factor_type)

        # Run general validation
        return self.validate(data)

    def validate_token(self, token: str) -> bool:
        """
        Validate an authentication token.

        Args:
            token: Token to validate

        Returns:
            True if token is valid format, False otherwise
        """
        if not isinstance(token, str):
            return False

        # Basic validation - tokens should have a reasonable length and format
        return len(token) >= 10  # This is a basic check - real implementation would verify token structure