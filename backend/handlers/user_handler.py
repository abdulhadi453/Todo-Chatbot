"""
UserHandler class - Manages user-related HTTP operations.
This handler delegates to the UserService for business logic while handling HTTP concerns.
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from sqlmodel import Session
from backend.services.user_service import UserService
from backend.validation.base_validator import UserValidator
from backend.utils.response_utils import create_success_response, create_error_response
from backend.utils.error_utils import handle_error, ValidationError, NotFoundError
from backend.logging.app_logger import app_logger
from backend.core.dependency_injection import get_service


class UserHandler:
    """
    Handler class for processing user-related HTTP operations.
    Delegates business logic to UserService while handling HTTP concerns like
    request parsing, response formatting, and error handling.
    """

    def __init__(self):
        """
        Initialize the UserHandler with required services.
        """
        self.user_service = get_service(UserService)
        self.validator = UserValidator()

    def handle_get_user(self, session: Session, user_id: str) -> Dict[str, Any]:
        """
        Handle request to get a specific user.

        Args:
            session: Database session
            user_id: ID of the user to retrieve

        Returns:
            Response dictionary with user information
        """
        try:
            # Validate input parameters
            data = {"user_id": user_id}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Get user via service
            user = self.user_service.get_user(session, user_id)

            if not user:
                app_logger.warning(
                    f"User not found: {user_id}",
                    extra_data={
                        "user_id": user_id,
                        "operation": "get_user",
                        "result": "user_not_found"
                    }
                )
                return create_error_response(
                    error="USER_NOT_FOUND",
                    message="User not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Format response
            return create_success_response(
                data={
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "bio": user.bio,
                        "avatar_url": user.avatar_url,
                        "timezone": user.timezone,
                        "language": user.language,
                        "role": user.role,
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                        "deactivated_at": user.deactivated_at.isoformat() if user.deactivated_at else None
                    }
                },
                message="User retrieved successfully"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in get_user: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error getting user {user_id}: {str(e)}")
            return handle_error(e, context="get_user", user_id=user_id)

    def handle_get_users_by_role(
        self,
        session: Session,
        role: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Handle request to get users by role.

        Args:
            session: Database session
            role: Role to filter users by
            limit: Maximum number of users to return
            offset: Offset for pagination

        Returns:
            Response dictionary with list of users
        """
        try:
            # Validate input parameters
            data = {"role": role, "limit": limit, "offset": offset}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Validate limit range
            if not (1 <= limit <= 100):
                return create_error_response(
                    error="INVALID_LIMIT",
                    message="Limit must be between 1 and 100",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Get users by role via service
            users = self.user_service.get_users_by_role(session, role, limit, offset)

            # Format response
            users_data = [
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]

            return create_success_response(
                data={
                    "users": users_data,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total": len(users_data)
                    },
                    "role": role
                },
                message=f"Retrieved {len(users_data)} users with role '{role}'"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in get_users_by_role: {ve}")
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error getting users with role {role}: {str(e)}")
            return handle_error(e, context="get_users_by_role", request_details={"role": role})

    def handle_update_user_profile(
        self,
        session: Session,
        user_id: str,
        **updates
    ) -> Dict[str, Any]:
        """
        Handle request to update user profile.

        Args:
            session: Database session
            user_id: ID of the user to update
            **updates: Profile fields to update

        Returns:
            Response dictionary with updated user information
        """
        try:
            # Validate input parameters
            data = {"user_id": user_id, **updates}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Update user profile via service
            updated_user = self.user_service.update_user_profile(session, user_id, **updates)

            if not updated_user:
                app_logger.warning(
                    f"User profile update failed for user: {user_id}",
                    extra_data={
                        "user_id": user_id,
                        "operation": "update_user_profile",
                        "result": "user_not_found"
                    }
                )
                return create_error_response(
                    error="USER_NOT_FOUND",
                    message="User not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Log successful operation
            app_logger.info(
                f"User profile updated successfully: {user_id}",
                extra_data={
                    "user_id": user_id,
                    "operation": "update_user_profile",
                    "updated_fields": list(updates.keys())
                }
            )

            # Format response
            return create_success_response(
                data={
                    "user": {
                        "id": updated_user.id,
                        "email": updated_user.email,
                        "username": updated_user.username,
                        "first_name": updated_user.first_name,
                        "last_name": updated_user.last_name,
                        "bio": updated_user.bio,
                        "avatar_url": updated_user.avatar_url,
                        "timezone": updated_user.timezone,
                        "language": updated_user.language,
                        "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
                    }
                },
                message="Profile updated successfully"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in update_user_profile: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error updating user profile for user {user_id}: {str(e)}")
            return handle_error(e, context="update_user_profile", user_id=user_id)

    def handle_activate_user(self, session: Session, user_id: str) -> Dict[str, Any]:
        """
        Handle request to activate a user.

        Args:
            session: Database session
            user_id: ID of the user to activate

        Returns:
            Response dictionary confirming activation
        """
        try:
            # Activate user via service
            success = self.user_service.activate_user(session, user_id)

            if not success:
                app_logger.warning(
                    f"User activation failed for user: {user_id}",
                    extra_data={
                        "user_id": user_id,
                        "operation": "activate_user",
                        "result": "user_not_found"
                    }
                )
                return create_error_response(
                    error="USER_NOT_FOUND",
                    message="User not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Log successful operation
            app_logger.info(
                f"User activated successfully: {user_id}",
                extra_data={
                    "user_id": user_id,
                    "operation": "activate_user"
                }
            )

            return create_success_response(
                message="User activated successfully"
            )

        except Exception as e:
            app_logger.error(f"Error activating user {user_id}: {str(e)}")
            return handle_error(e, context="activate_user", user_id=user_id)

    def handle_deactivate_user(self, session: Session, user_id: str, deactivation_reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle request to deactivate a user.

        Args:
            session: Database session
            user_id: ID of the user to deactivate
            deactivation_reason: Optional reason for deactivation

        Returns:
            Response dictionary confirming deactivation
        """
        try:
            # Deactivate user via service
            success = self.user_service.deactivate_user(session, user_id, deactivation_reason)

            if not success:
                app_logger.warning(
                    f"User deactivation failed for user: {user_id}",
                    extra_data={
                        "user_id": user_id,
                        "operation": "deactivate_user",
                        "result": "user_not_found"
                    }
                )
                return create_error_response(
                    error="USER_NOT_FOUND",
                    message="User not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Log successful operation
            app_logger.info(
                f"User deactivated successfully: {user_id}",
                extra_data={
                    "user_id": user_id,
                    "operation": "deactivate_user",
                    "reason": deactivation_reason
                }
            )

            return create_success_response(
                message="User deactivated successfully"
            )

        except Exception as e:
            app_logger.error(f"Error deactivating user {user_id}: {str(e)}")
            return handle_error(e, context="deactivate_user", user_id=user_id)

    def handle_update_user_preferences(
        self,
        session: Session,
        user_id: str,
        **preferences
    ) -> Dict[str, Any]:
        """
        Handle request to update user preferences.

        Args:
            session: Database session
            user_id: ID of the user to update preferences for
            **preferences: Preference fields to update

        Returns:
            Response dictionary with updated user information
        """
        try:
            # Validate input parameters
            data = {"user_id": user_id, **preferences}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Update user preferences via service
            updated_user = self.user_service.update_user_preferences(session, user_id, **preferences)

            if not updated_user:
                app_logger.warning(
                    f"User preferences update failed for user: {user_id}",
                    extra_data={
                        "user_id": user_id,
                        "operation": "update_user_preferences",
                        "result": "user_not_found"
                    }
                )
                return create_error_response(
                    error="USER_NOT_FOUND",
                    message="User not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Log successful operation
            app_logger.info(
                f"User preferences updated successfully: {user_id}",
                extra_data={
                    "user_id": user_id,
                    "operation": "update_user_preferences",
                    "updated_preferences": list(preferences.keys())
                }
            )

            # Format response
            return create_success_response(
                data={
                    "user": {
                        "id": updated_user.id,
                        "email": updated_user.email,
                        "username": updated_user.username,
                        "timezone": updated_user.timezone,
                        "language": updated_user.language,
                        "theme_preference": updated_user.theme_preference,
                        "notifications_enabled": updated_user.notifications_enabled,
                        "email_notifications": updated_user.email_notifications,
                        "sms_notifications": updated_user.sms_notifications,
                        "two_factor_enabled": updated_user.two_factor_enabled,
                        "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
                    }
                },
                message="User preferences updated successfully"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in update_user_preferences: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error updating user preferences for user {user_id}: {str(e)}")
            return handle_error(e, context="update_user_preferences", user_id=user_id)

    def handle_get_user_statistics(self, session: Session, user_id: str) -> Dict[str, Any]:
        """
        Handle request to get user statistics.

        Args:
            session: Database session
            user_id: ID of the user to get statistics for

        Returns:
            Response dictionary with user statistics
        """
        try:
            # Validate input parameters
            data = {"user_id": user_id}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Get user statistics via service
            stats = self.user_service.get_user_statistics(session, user_id)

            # Format response
            return create_success_response(
                data={
                    "statistics": stats
                },
                message="User statistics retrieved successfully"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in get_user_statistics: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except NotFoundError as nfe:
            app_logger.error(f"User not found in get_user_statistics: {nfe}", extra_data={"user_id": user_id})
            return create_error_response(
                error="USER_NOT_FOUND",
                message=str(nfe),
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            app_logger.error(f"Error getting user statistics for user {user_id}: {str(e)}")
            return handle_error(e, context="get_user_statistics", user_id=user_id)

    def handle_search_users(
        self,
        session: Session,
        search_term: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Handle request to search users.

        Args:
            session: Database session
            search_term: Term to search for in user data
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            Response dictionary with search results
        """
        try:
            # Validate input parameters
            data = {"search_term": search_term, "limit": limit, "offset": offset}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Validate limit range
            if not (1 <= limit <= 100):
                return create_error_response(
                    error="INVALID_LIMIT",
                    message="Limit must be between 1 and 100",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Search users via service
            users = self.user_service.search_users(session, search_term, limit, offset)

            # Format response
            users_data = [
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]

            return create_success_response(
                data={
                    "users": users_data,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total": len(users_data)
                    },
                    "search_term": search_term
                },
                message=f"Found {len(users_data)} users matching '{search_term}'"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in search_users: {ve}")
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error searching users with term {search_term}: {str(e)}")
            return handle_error(e, context="search_users", request_details={"search_term": search_term})

    def handle_get_users_with_filters(
        self,
        session: Session,
        is_active: Optional[bool] = None,
        role: Optional[str] = None,
        created_after: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Handle request to get users with various filters.

        Args:
            session: Database session
            is_active: Filter by active status
            role: Filter by role
            created_after: Filter by creation date (ISO format string)
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            Response dictionary with filtered user list
        """
        try:
            # Convert created_after string to datetime if provided
            from datetime import datetime
            created_after_dt = None
            if created_after:
                try:
                    created_after_dt = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
                except ValueError:
                    return create_error_response(
                        error="INVALID_DATE_FORMAT",
                        message="created_after must be in ISO format",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

            # Validate input parameters
            data = {
                "is_active": is_active,
                "role": role,
                "created_after": created_after,
                "limit": limit,
                "offset": offset
            }
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Validate limit range
            if not (1 <= limit <= 100):
                return create_error_response(
                    error="INVALID_LIMIT",
                    message="Limit must be between 1 and 100",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Get users with filters via service
            users = self.user_service.get_users_with_filters(
                session, is_active, role, created_after_dt, limit, offset
            )

            # Format response
            users_data = [
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]

            filters_applied = {}
            if is_active is not None:
                filters_applied["is_active"] = is_active
            if role:
                filters_applied["role"] = role
            if created_after:
                filters_applied["created_after"] = created_after

            return create_success_response(
                data={
                    "users": users_data,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total": len(users_data)
                    },
                    "filters": filters_applied
                },
                message=f"Retrieved {len(users_data)} users with specified filters"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in get_users_with_filters: {ve}")
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error getting users with filters: {str(e)}")
            return handle_error(e, context="get_users_with_filters", request_details={
                "is_active": is_active,
                "role": role,
                "created_after": created_after
            })

    def handle_get_user_count(
        self,
        session: Session,
        is_active: Optional[bool] = None,
        role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle request to get user count with optional filters.

        Args:
            session: Database session
            is_active: Filter by active status
            role: Filter by role

        Returns:
            Response dictionary with user count
        """
        try:
            # Validate input parameters
            data = {"is_active": is_active, "role": role}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Get user count via service
            count = self.user_service.get_user_count(session, is_active, role)

            filters_applied = {}
            if is_active is not None:
                filters_applied["is_active"] = is_active
            if role:
                filters_applied["role"] = role

            return create_success_response(
                data={
                    "count": count,
                    "filters": filters_applied
                },
                message=f"Found {count} users matching specified filters"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in get_user_count: {ve}")
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error getting user count: {str(e)}")
            return handle_error(e, context="get_user_count", request_details={
                "is_active": is_active,
                "role": role
            })