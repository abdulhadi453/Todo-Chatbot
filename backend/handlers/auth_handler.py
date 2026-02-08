"""
AuthHandler class - Handles authentication-related HTTP requests.
This handler delegates to the AuthService for business logic while handling HTTP concerns.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlmodel import Session
from backend.services.auth_service import AuthService
from backend.validation.auth_validator import AuthValidator
from backend.utils.response_utils import create_success_response, create_error_response
from backend.utils.error_utils import handle_error, ValidationError, AuthenticationError
from backend.logging.app_logger import app_logger
from backend.core.dependency_injection import get_service


class AuthHandler:
    """
    Handler class for processing authentication-related HTTP requests.
    Delegates business logic to AuthService while handling HTTP concerns like
    request parsing, response formatting, and error handling.
    """

    def __init__(self):
        """
        Initialize the AuthHandler with required services.
        """
        self.auth_service = get_service(AuthService)
        self.validator = AuthValidator()

    def handle_register_user(
        self,
        session: Session,
        email: str,
        password: str,
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle request to register a new user.

        Args:
            session: Database session
            email: User's email address
            password: User's password
            username: Optional username

        Returns:
            Response dictionary with registration result
        """
        try:
            # Validate input parameters
            data = {"email": email, "password": password}
            if username:
                data["username"] = username

            validation_result, errors = self.validator.validate_registration_data(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Register user via service
            user = self.auth_service.register_user(session, email, password, username)

            # Log successful operation
            app_logger.info(
                f"User registered successfully: {user.id}",
                extra_data={
                    "user_id": user.id,
                    "email": user.email,
                    "operation": "register_user"
                }
            )

            # Format response
            return create_success_response(
                data={
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "created_at": user.created_at.isoformat() if user.created_at else None
                    }
                },
                message="User registered successfully",
                status_code=status.HTTP_201_CREATED
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in register_user: {ve}", extra_data={"email": email})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error registering user with email {email}: {str(e)}")
            return handle_error(e, context="register_user", request_details={"email": email})

    def handle_login_user(
        self,
        session: Session,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Handle request for user login.

        Args:
            session: Database session
            email: User's email address
            password: User's password

        Returns:
            Response dictionary with login result and authentication token
        """
        try:
            # Validate input parameters
            data = {"email": email, "password": password}
            validation_result, errors = self.validator.validate_login_data(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Authenticate user via service
            user = self.auth_service.authenticate_user(session, email, password)

            if not user:
                app_logger.warning(
                    f"Login failed for email: {email}",
                    extra_data={
                        "email": email,
                        "operation": "login",
                        "result": "authentication_failed"
                    }
                )
                return create_error_response(
                    error="AUTHENTICATION_FAILED",
                    message="Invalid email or password",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            # In a real implementation, we would generate JWT tokens here
            # For now, we'll just return user info (in a real app, you'd return tokens)
            auth_token = self._generate_auth_token(user.id)
            refresh_token = self._generate_refresh_token(user.id)

            # Update last login time
            user.last_login = session.exec(
                # Update user's last login in database
                # This is a simplified approach - in a real implementation, you'd update the last_login field
            )

            # Log successful operation
            app_logger.info(
                f"User logged in successfully: {user.id}",
                extra_data={
                    "user_id": user.id,
                    "email": user.email,
                    "operation": "login"
                }
            )

            # Format response
            return create_success_response(
                data={
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "created_at": user.created_at.isoformat() if user.created_at else None
                    },
                    "auth_token": auth_token,
                    "refresh_token": refresh_token,
                    "expires_in": 3600  # Token expiry in seconds (1 hour)
                },
                message="Login successful"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in login_user: {ve}", extra_data={"email": email})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error during login for email {email}: {str(e)}")
            return handle_error(e, context="login_user", request_details={"email": email})

    def handle_logout_user(self, session: Session, user_id: str) -> Dict[str, Any]:
        """
        Handle request for user logout.

        Args:
            session: Database session
            user_id: ID of the user logging out

        Returns:
            Response dictionary confirming logout
        """
        try:
            # In a real implementation, we would invalidate the token
            # For now, we'll just return a success response
            app_logger.info(
                f"User logged out: {user_id}",
                extra_data={
                    "user_id": user_id,
                    "operation": "logout"
                }
            )

            return create_success_response(
                message="Logout successful",
                status_code=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:
            app_logger.error(f"Error during logout for user {user_id}: {str(e)}")
            return handle_error(e, context="logout_user", user_id=user_id)

    def handle_change_password(
        self,
        session: Session,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        """
        Handle request to change user's password.

        Args:
            session: Database session
            user_id: ID of the user changing password
            old_password: Current password
            new_password: New password

        Returns:
            Response dictionary confirming password change
        """
        try:
            # Validate input parameters
            data = {"old_password": old_password, "new_password": new_password}
            validation_result, errors = self.validator.validate_password_change(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Change password via service
            success = self.auth_service.change_password(session, user_id, old_password, new_password)

            if not success:
                app_logger.warning(
                    f"Password change failed for user: {user_id}",
                    extra_data={
                        "user_id": user_id,
                        "operation": "change_password",
                        "result": "failure"
                    }
                )
                return create_error_response(
                    error="PASSWORD_CHANGE_FAILED",
                    message="Password change failed. Please check your old password and try again.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Log successful operation
            app_logger.info(
                f"Password changed successfully for user: {user_id}",
                extra_data={
                    "user_id": user_id,
                    "operation": "change_password"
                }
            )

            return create_success_response(
                message="Password changed successfully"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in change_password: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error changing password for user {user_id}: {str(e)}")
            return handle_error(e, context="change_password", user_id=user_id)

    def handle_reset_password_request(
        self,
        session: Session,
        email: str
    ) -> Dict[str, Any]:
        """
        Handle request to initiate password reset.

        Args:
            session: Database session
            email: Email address of the user requesting password reset

        Returns:
            Response dictionary confirming password reset initiation
        """
        try:
            # Validate input parameters
            data = {"email": email}
            validation_result, errors = self.validator.validate_password_reset_request(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Initiate password reset via service
            success = self.auth_service.initiate_password_reset(session, email)

            if not success:
                app_logger.warning(
                    f"Password reset initiation failed for email: {email}",
                    extra_data={
                        "email": email,
                        "operation": "password_reset_request",
                        "result": "user_not_found"
                    }
                )
                return create_error_response(
                    error="USER_NOT_FOUND",
                    message="No user found with this email address",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Log successful operation
            app_logger.info(
                f"Password reset initiated for email: {email}",
                extra_data={
                    "email": email,
                    "operation": "password_reset_request"
                }
            )

            return create_success_response(
                message="Password reset instructions sent to your email"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in reset_password_request: {ve}", extra_data={"email": email})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error initiating password reset for email {email}: {str(e)}")
            return handle_error(e, context="reset_password_request", request_details={"email": email})

    def handle_reset_password(
        self,
        session: Session,
        email: str,
        new_password: str,
        confirm_new_password: str,
        reset_token: str
    ) -> Dict[str, Any]:
        """
        Handle request to reset user's password.

        Args:
            session: Database session
            email: Email of the user resetting password
            new_password: New password
            confirm_new_password: Confirmation of new password
            reset_token: Password reset token

        Returns:
            Response dictionary confirming password reset
        """
        try:
            # Validate input parameters
            data = {
                "email": email,
                "new_password": new_password,
                "confirm_new_password": confirm_new_password,
                "reset_token": reset_token
            }
            validation_result, errors = self.validator.validate_password_reset(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Validate reset token (in a real implementation)
            is_valid_token = self._validate_reset_token(reset_token, email)
            if not is_valid_token:
                app_logger.warning(
                    f"Invalid reset token used for email: {email}",
                    extra_data={
                        "email": email,
                        "operation": "reset_password",
                        "result": "invalid_token"
                    }
                )
                return create_error_response(
                    error="INVALID_RESET_TOKEN",
                    message="Invalid or expired reset token",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Reset password via service
            success = self.auth_service.reset_password(session, email, new_password)

            if not success:
                app_logger.warning(
                    f"Password reset failed for email: {email}",
                    extra_data={
                        "email": email,
                        "operation": "reset_password",
                        "result": "user_not_found"
                    }
                )
                return create_error_response(
                    error="USER_NOT_FOUND",
                    message="User with this email was not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Log successful operation
            app_logger.info(
                f"Password reset successfully for email: {email}",
                extra_data={
                    "email": email,
                    "operation": "reset_password"
                }
            )

            return create_success_response(
                message="Password reset successfully"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in reset_password: {ve}", extra_data={"email": email})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error resetting password for email {email}: {str(e)}")
            return handle_error(e, context="reset_password", request_details={"email": email})

    def handle_activate_user(self, session: Session, user_id: str) -> Dict[str, Any]:
        """
        Handle request to activate a user account.

        Args:
            session: Database session
            user_id: ID of the user to activate

        Returns:
            Response dictionary confirming account activation
        """
        try:
            # Activate user via service
            success = self.auth_service.activate_user(session, user_id)

            if not success:
                app_logger.warning(
                    f"Account activation failed for user: {user_id}",
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
                message="Account activated successfully"
            )

        except Exception as e:
            app_logger.error(f"Error activating user {user_id}: {str(e)}")
            return handle_error(e, context="activate_user", user_id=user_id)

    def handle_deactivate_user(self, session: Session, user_id: str) -> Dict[str, Any]:
        """
        Handle request to deactivate a user account.

        Args:
            session: Database session
            user_id: ID of the user to deactivate

        Returns:
            Response dictionary confirming account deactivation
        """
        try:
            # Deactivate user via service
            success = self.auth_service.deactivate_user(session, user_id)

            if not success:
                app_logger.warning(
                    f"Account deactivation failed for user: {user_id}",
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
                    "operation": "deactivate_user"
                }
            )

            return create_success_response(
                message="Account deactivated successfully"
            )

        except Exception as e:
            app_logger.error(f"Error deactivating user {user_id}: {str(e)}")
            return handle_error(e, context="deactivate_user", user_id=user_id)

    def handle_update_user_profile(
        self,
        session: Session,
        user_id: str,
        **updates
    ) -> Dict[str, Any]:
        """
        Handle request to update user profile information.

        Args:
            session: Database session
            user_id: ID of the user to update
            **updates: Profile fields to update

        Returns:
            Response dictionary with updated profile information
        """
        try:
            # Validate input parameters
            data = {"user_id": user_id, **updates}
            validation_result, errors = self.validator.validate_user_profile_update(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Update profile via service
            updated_user = self.auth_service.update_profile(session, user_id, **updates)

            if not updated_user:
                app_logger.warning(
                    f"Profile update failed for user: {user_id}",
                    extra_data={
                        "user_id": user_id,
                        "operation": "update_profile",
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
                f"Profile updated successfully for user: {user_id}",
                extra_data={
                    "user_id": user_id,
                    "operation": "update_profile",
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
                        "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
                    }
                },
                message="Profile updated successfully"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in update_profile: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error updating profile for user {user_id}: {str(e)}")
            return handle_error(e, context="update_profile", user_id=user_id)

    def handle_get_user_profile(self, session: Session, user_id: str) -> Dict[str, Any]:
        """
        Handle request to get user profile information.

        Args:
            session: Database session
            user_id: ID of the user whose profile to retrieve

        Returns:
            Response dictionary with user profile information
        """
        try:
            # Get user via service
            user = self.auth_service.get_user_by_id(session, user_id)

            if not user:
                app_logger.warning(
                    f"Profile retrieval failed for user: {user_id}",
                    extra_data={
                        "user_id": user_id,
                        "operation": "get_user_profile",
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
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                        "is_active": user.is_active
                    }
                },
                message="Profile retrieved successfully"
            )

        except Exception as e:
            app_logger.error(f"Error retrieving profile for user {user_id}: {str(e)}")
            return handle_error(e, context="get_user_profile", user_id=user_id)

    def _generate_auth_token(self, user_id: str) -> str:
        """
        Generate an authentication token for the user.

        Args:
            user_id: ID of the user

        Returns:
            Authentication token string
        """
        # In a real implementation, this would generate a JWT token
        # For this example, we'll return a placeholder
        import secrets
        return secrets.token_urlsafe(32)

    def _generate_refresh_token(self, user_id: str) -> str:
        """
        Generate a refresh token for the user.

        Args:
            user_id: ID of the user

        Returns:
            Refresh token string
        """
        # In a real implementation, this would generate a refresh JWT token
        # For this example, we'll return a placeholder
        import secrets
        return secrets.token_urlsafe(32)

    def _validate_reset_token(self, token: str, email: str) -> bool:
        """
        Validate a password reset token.

        Args:
            token: Reset token to validate
            email: Email associated with the reset token

        Returns:
            True if token is valid, False otherwise
        """
        # In a real implementation, this would check the token against a database
        # For this example, we'll return True (but in a real app, you'd validate properly)
        # This is just a placeholder implementation
        return len(token) > 0