"""
UserService class - Handles user-specific operations and profile management.
This service follows the single responsibility principle for user management functionality.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
from backend.handlers.user_handler import User  # Assuming a User model exists
from backend.core.dependency_injection import register_service, Injectable
from backend.utils.validator_utils import validate_email, validate_required_fields
from backend.utils.error_utils import ValidationError, NotFoundError, ServiceError


@register_service
class UserService(Injectable):
    """
    Service class for handling user-specific operations and profile management.
    Manages user profiles, settings, and user-related data operations.
    """

    def __init__(self):
        """
        Initialize the UserService.
        """
        pass

    def get_user(self, session: Session, user_id: str) -> Optional[User]:
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

    def get_user_by_email(self, session: Session, email: str) -> Optional[User]:
        """
        Get a user by email address.

        Args:
            session: Database session
            email: Email address of the user to retrieve

        Returns:
            User instance if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        return user

    def update_user_profile(self, session: Session, user_id: str, **updates) -> Optional[User]:
        """
        Update user profile information.

        Args:
            session: Database session
            user_id: ID of the user to update
            **updates: Profile fields to update

        Returns:
            Updated User instance if successful, None otherwise

        Raises:
            ValidationError: If invalid fields are provided
        """
        # Define allowed profile fields
        allowed_fields = {
            "username", "email", "first_name", "last_name", "bio",
            "avatar_url", "timezone", "language", "theme_preference"
        }

        # Check for invalid fields
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise ValidationError(f"Invalid fields for profile update: {', '.join(invalid_fields)}")

        # Get user
        user = self.get_user(session, user_id)
        if not user:
            return None

        # Validate email if being updated
        if "email" in updates:
            new_email = updates["email"]
            if not validate_email(new_email):
                raise ValidationError("Invalid email format")

            # Check if email is already in use by another user
            existing_user = self.get_user_by_email(session, new_email)
            if existing_user and existing_user.id != user_id:
                raise ValidationError("Email is already in use by another account")

        # Update allowed fields
        for field, value in updates.items():
            if hasattr(user, field):
                setattr(user, field, value)

        # Update timestamp
        user.updated_at = datetime.utcnow()

        # Commit changes
        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    def get_users_by_role(self, session: Session, role: str, limit: int = 50, offset: int = 0) -> List[User]:
        """
        Get users by role.

        Args:
            session: Database session
            role: Role to filter users by
            limit: Maximum number of users to return
            offset: Offset for pagination

        Returns:
            List of User instances with the specified role
        """
        statement = select(User).where(User.role == role).offset(offset).limit(limit)
        users = session.exec(statement).all()
        return users

    def deactivate_user(self, session: Session, user_id: str, deactivation_reason: Optional[str] = None) -> bool:
        """
        Deactivate a user account.

        Args:
            session: Database session
            user_id: ID of the user to deactivate
            deactivation_reason: Optional reason for deactivation

        Returns:
            True if deactivation was successful, False otherwise
        """
        user = self.get_user(session, user_id)
        if not user:
            return False

        user.is_active = False
        user.deactivated_at = datetime.utcnow()
        if deactivation_reason:
            user.deactivation_reason = deactivation_reason

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
        user = self.get_user(session, user_id)
        if not user:
            return False

        user.is_active = True
        user.deactivated_at = None
        user.deactivation_reason = None

        session.add(user)
        session.commit()

        return True

    def update_user_preferences(self, session: Session, user_id: str, **preferences) -> Optional[User]:
        """
        Update user preferences.

        Args:
            session: Database session
            user_id: ID of the user to update
            **preferences: Preference fields to update

        Returns:
            Updated User instance if successful, None otherwise
        """
        user = self.get_user(session, user_id)
        if not user:
            return None

        # Define allowed preference fields
        allowed_preferences = {
            "notifications_enabled", "email_notifications", "sms_notifications",
            "theme_preference", "language", "timezone", "two_factor_enabled"
        }

        # Check for invalid preferences
        invalid_prefs = set(preferences.keys()) - allowed_preferences
        if invalid_prefs:
            raise ValidationError(f"Invalid preferences: {', '.join(invalid_prefs)}")

        # Update preferences
        for pref, value in preferences.items():
            if hasattr(user, pref):
                setattr(user, pref, value)

        # Update timestamp
        user.updated_at = datetime.utcnow()

        # Commit changes
        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    def get_user_statistics(self, session: Session, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics.

        Args:
            session: Database session
            user_id: ID of the user to get statistics for

        Returns:
            Dictionary with user statistics
        """
        user = self.get_user(session, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found", "User", user_id)

        # In a real implementation, this would aggregate statistics from related models
        # For now, we'll return basic information
        stats = {
            "user_id": user.id,
            "account_created": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
            "profile_complete": bool(user.first_name and user.last_name and user.email),
        }

        return stats

    def search_users(self, session: Session, search_term: str, limit: int = 50, offset: int = 0) -> List[User]:
        """
        Search users by email or username.

        Args:
            session: Database session
            search_term: Term to search for in emails and usernames
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of matching User instances
        """
        statement = select(User).where(
            (User.email.contains(search_term)) |
            (User.username.contains(search_term)) |
            ((User.first_name + " " + User.last_name).contains(search_term))
        ).offset(offset).limit(limit)

        users = session.exec(statement).all()
        return users

    def get_users_with_filters(
        self,
        session: Session,
        is_active: Optional[bool] = None,
        role: Optional[str] = None,
        created_after: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[User]:
        """
        Get users with various filters.

        Args:
            session: Database session
            is_active: Filter by active status
            role: Filter by role
            created_after: Filter by creation date
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of User instances matching the filters
        """
        statement = select(User)

        # Apply filters
        if is_active is not None:
            statement = statement.where(User.is_active == is_active)

        if role:
            statement = statement.where(User.role == role)

        if created_after:
            statement = statement.where(User.created_at >= created_after)

        statement = statement.offset(offset).limit(limit)

        users = session.exec(statement).all()
        return users

    def get_user_count(self, session: Session, is_active: Optional[bool] = None, role: Optional[str] = None) -> int:
        """
        Get the count of users with optional filters.

        Args:
            session: Database session
            is_active: Filter by active status
            role: Filter by role

        Returns:
            Count of users matching the filters
        """
        statement = select(User)

        # Apply filters
        if is_active is not None:
            statement = statement.where(User.is_active == is_active)

        if role:
            statement = statement.where(User.role == role)

        users = session.exec(statement).all()
        return len(users)

    def transfer_user_data(self, session: Session, source_user_id: str, target_user_id: str, data_types: List[str]) -> Dict[str, Any]:
        """
        Transfer user data from one user to another.

        Args:
            session: Database session
            source_user_id: ID of the source user
            target_user_id: ID of the target user
            data_types: List of data types to transfer

        Returns:
            Dictionary with transfer results
        """
        # Verify both users exist
        source_user = self.get_user(session, source_user_id)
        target_user = self.get_user(session, target_user_id)

        if not source_user:
            raise NotFoundError(f"Source user with ID {source_user_id} not found", "User", source_user_id)

        if not target_user:
            raise NotFoundError(f"Target user with ID {target_user_id} not found", "User", target_user_id)

        # This would implement data transfer logic depending on the specific data types
        # For now, we'll return a placeholder implementation
        results = {
            "success": True,
            "transferred_data_types": [],
            "failed_transfers": [],
            "summary": f"Transfer of {data_types} from user {source_user_id} to {target_user_id} initiated"
        }

        return results

    def get_user_activity_summary(self, session: Session, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get user activity summary for the specified number of days.

        Args:
            session: Database session
            user_id: ID of the user to get activity for
            days: Number of days to include in the summary

        Returns:
            Dictionary with user activity summary
        """
        # In a real implementation, this would aggregate activity data from logs
        # For now, we'll return a basic placeholder
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        activity_summary = {
            "user_id": user_id,
            "period_days": days,
            "start_date": cutoff_date.isoformat(),
            "last_active": None,  # Would come from user logs
            "activity_count": 0,  # Would be calculated from logs
            "most_active_period": "morning",  # Would be calculated from logs
        }

        return activity_summary