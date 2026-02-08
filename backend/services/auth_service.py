"""
AuthService class - Manages authentication and user-related operations.
This service follows the single responsibility principle for authentication functionality.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
import hashlib
import secrets
from backend.models.user import User  # Assuming a User model exists
from backend.core.dependency_injection import register_service, Injectable
from backend.utils.validator_utils import validate_email, validate_required_fields
from backend.utils.error_utils import ValidationError, AuthenticationError, AuthorizationError


@register_service
class AuthService(Injectable):
    """
    Service class for managing authentication and user-related operations.
    Handles user registration, login, password management, and session handling.
    """

    def __init__(self, salt_length: int = 16, hash_iterations: int = 100000):
        """
        Initialize the AuthService.

        Args:
            salt_length: Length of salt for password hashing
            hash_iterations: Number of iterations for password hashing
        """
        self.salt_length = salt_length
        self.hash_iterations = hash_iterations

    def register_user(self, session: Session, email: str, password: str, username: Optional[str] = None) -> User:
        """
        Register a new user.

        Args:
            session: Database session
            email: User's email address
            password: User's password
            username: Optional username

        Returns:
            Created User instance

        Raises:
            ValidationError: If required fields are invalid
        """
        # Validate required fields
        data = {"email": email, "password": password}
        missing_fields = validate_required_fields(data, ["email", "password"])

        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

        # Validate email format
        if not validate_email(email):
            raise ValidationError("Invalid email format")

        # Validate password strength
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        # Check if user already exists
        existing_user = self.get_user_by_email(session, email)
        if existing_user:
            raise ValidationError("User with this email already exists")

        # Create password hash
        password_hash, salt = self._hash_password(password)

        # Create user instance
        user = User(
            email=email,
            password_hash=password_hash,
            salt=salt,
            username=username,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )

        # Add to session and commit
        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    def authenticate_user(self, session: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            session: Database session
            email: User's email address
            password: User's password

        Returns:
            User instance if authentication is successful, None otherwise
        """
        # Get user by email
        user = self.get_user_by_email(session, email)

        if not user:
            return None

        # Verify password
        if not self._verify_password(password, user.password_hash, user.salt):
            return None

        # Check if user is active
        if not user.is_active:
            return None

        return user

    def get_user_by_email(self, session: Session, email: str) -> Optional[User]:
        """
        Get a user by email address.

        Args:
            session: Database session
            email: Email address to search for

        Returns:
            User instance if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        return user

    def get_user_by_id(self, session: Session, user_id: str) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            session: Database session
            user_id: ID of the user to retrieve

        Returns:
            User instance if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        return user

    def change_password(self, session: Session, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change a user's password.

        Args:
            session: Database session
            user_id: ID of the user changing password
            old_password: Current password
            new_password: New password

        Returns:
            True if password was changed successfully, False otherwise

        Raises:
            ValidationError: If passwords don't meet requirements
        """
        # Validate new password strength
        if len(new_password) < 8:
            raise ValidationError("New password must be at least 8 characters long")

        # Get user
        user = self.get_user_by_id(session, user_id)
        if not user:
            return False

        # Verify old password
        if not self._verify_password(old_password, user.password_hash, user.salt):
            return False

        # Create new password hash
        new_password_hash, new_salt = self._hash_password(new_password)

        # Update user
        user.password_hash = new_password_hash
        user.salt = new_salt
        user.updated_at = datetime.utcnow()

        # Commit changes
        session.add(user)
        session.commit()

        return True

    def reset_password(self, session: Session, email: str, new_password: str) -> bool:
        """
        Reset a user's password (typically via reset token).

        Args:
            session: Database session
            email: Email address of the user
            new_password: New password

        Returns:
            True if password was reset successfully, False otherwise

        Raises:
            ValidationError: If password doesn't meet requirements
        """
        # Validate new password strength
        if len(new_password) < 8:
            raise ValidationError("New password must be at least 8 characters long")

        # Get user
        user = self.get_user_by_email(session, email)
        if not user:
            return False

        # Create new password hash
        new_password_hash, new_salt = self._hash_password(new_password)

        # Update user
        user.password_hash = new_password_hash
        user.salt = new_salt
        user.updated_at = datetime.utcnow()

        # Commit changes
        session.add(user)
        session.commit()

        return True

    def generate_reset_token(self) -> str:
        """
        Generate a password reset token.

        Returns:
            Randomly generated token string
        """
        return secrets.token_urlsafe(32)

    def invalidate_sessions(self, session: Session, user_id: str) -> bool:
        """
        Invalidate all sessions for a user (logout everywhere).

        Args:
            session: Database session
            user_id: ID of the user to invalidate sessions for

        Returns:
            True if successful, False otherwise
        """
        # In a real implementation, this would invalidate session records
        # For now, we'll just update the user's last_modified time
        user = self.get_user_by_id(session, user_id)
        if not user:
            return False

        user.updated_at = datetime.utcnow()
        session.add(user)
        session.commit()

        return True

    def activate_user(self, session: Session, user_id: str) -> bool:
        """
        Activate a user account.

        Args:
            session: Database session
            user_id: ID of the user to activate

        Returns:
            True if activation was successful, False otherwise
        """
        user = self.get_user_by_id(session, user_id)
        if not user:
            return False

        user.is_active = True
        user.updated_at = datetime.utcnow()

        session.add(user)
        session.commit()

        return True

    def deactivate_user(self, session: Session, user_id: str) -> bool:
        """
        Deactivate a user account.

        Args:
            session: Database session
            user_id: ID of the user to deactivate

        Returns:
            True if deactivation was successful, False otherwise
        """
        user = self.get_user_by_id(session, user_id)
        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()

        session.add(user)
        session.commit()

        return True

    def update_profile(self, session: Session, user_id: str, **updates) -> Optional[User]:
        """
        Update user profile information.

        Args:
            session: Database session
            user_id: ID of the user to update
            **updates: Profile fields to update

        Returns:
            Updated User instance if successful, None otherwise
        """
        # Get user
        user = self.get_user_by_id(session, user_id)
        if not user:
            return None

        # Define allowed profile fields to update
        allowed_fields = {"username", "email", "first_name", "last_name", "bio"}

        # Check for invalid fields
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise ValidationError(f"Invalid profile fields: {', '.join(invalid_fields)}")

        # Update allowed fields
        for field, value in updates.items():
            if hasattr(user, field):
                # If updating email, validate it
                if field == "email" and value != user.email:
                    if not validate_email(value):
                        raise ValidationError("Invalid email format")

                    # Check if new email is already taken
                    existing_user = self.get_user_by_email(session, value)
                    if existing_user and existing_user.id != user_id:
                        raise ValidationError("Email is already in use by another account")

                setattr(user, field, value)

        # Update timestamp
        user.updated_at = datetime.utcnow()

        # Commit changes
        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    def _hash_password(self, password: str) -> tuple[str, str]:
        """
        Hash a password with a random salt.

        Args:
            password: Password to hash

        Returns:
            Tuple of (hashed_password, salt)
        """
        # Generate a random salt
        salt = secrets.token_hex(self.salt_length)

        # Hash the password with the salt and multiple iterations
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            self.hash_iterations
        )

        # Convert to hex string
        hashed_password = hashed.hex()

        return hashed_password, salt

    def _verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            hashed_password: Stored hashed password
            salt: Salt used for the stored password

        Returns:
            True if password matches hash, False otherwise
        """
        # Hash the provided password with the stored salt
        hashed_input = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            self.hash_iterations
        )

        # Compare with the stored hash
        return hashed_input.hex() == hashed_password

    def validate_credentials(self, email: str, password: str) -> Dict[str, Any]:
        """
        Validate user credentials without accessing database.

        Args:
            email: Email to validate
            password: Password to validate

        Returns:
            Dictionary with validation results and error messages
        """
        errors = []

        # Validate email format
        if not validate_email(email):
            errors.append("Invalid email format")

        # Validate password length
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }