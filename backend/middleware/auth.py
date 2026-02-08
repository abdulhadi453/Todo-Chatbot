"""
Authentication middleware for the AI agent endpoints.
This module handles JWT token validation for agent-related API endpoints.
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class AuthMiddleware:
    """
    Authentication middleware class for agent endpoints.
    Handles JWT token validation and user identification.
    """

    def __init__(self):
        """
        Initialize the authentication middleware with the secret key.
        """
        self.secret_key = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-for-development")
        self.algorithm = "HS256"
        self.security = HTTPBearer()

    async def verify_token(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> dict:
        """
        Verify the JWT token and extract the payload.

        Args:
            credentials: HTTP authorization credentials containing the JWT token

        Returns:
            Token payload if valid

        Raises:
            HTTPException: If token is invalid, expired, or missing
        """
        token = credentials.credentials

        try:
            # Decode the JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_user_id_from_token(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> str:
        """
        Extract the user ID from the JWT token.

        Args:
            credentials: HTTP authorization credentials containing the JWT token

        Returns:
            User ID if token is valid

        Raises:
            HTTPException: If token is invalid, expired, missing, or user ID not found
        """
        token = credentials.credentials

        try:
            # Decode the JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            user_id = payload.get("user_id")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_user_owns_resource(self, user_id_from_token: str, resource_user_id: str) -> bool:
        """
        Verify that the authenticated user owns a specific resource.

        Args:
            user_id_from_token: User ID extracted from JWT token
            resource_user_id: User ID associated with the requested resource

        Returns:
            True if user IDs match, False otherwise
        """
        return user_id_from_token == resource_user_id

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """
        Create a new JWT access token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Default to 15 minutes expiration
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt


# Create a global instance of the AuthMiddleware
auth_middleware = AuthMiddleware()

# Export the dependency for use in routes
get_current_user_id = auth_middleware.get_user_id_from_token