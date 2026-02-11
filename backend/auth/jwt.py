"""
JWT authentication utilities for the chatbot feature.
This module handles JWT token validation and user identification.
"""

from datetime import datetime, timedelta
from typing import Optional
import os
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from config.database import get_session
from models.user_context import User  # Assuming User model exists from Phase II

# Initialize security scheme for API documentation
security = HTTPBearer()

# Get secret key from environment variable
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify a JWT token and return the payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Get the current authenticated user based on the JWT token.

    Args:
        credentials: HTTP authorization credentials from the request
        session: Database session for querying user

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: If token is invalid or user doesn't exist
    """
    token = credentials.credentials
    payload = verify_token(token)
    user_id: str = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Query the user from the database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def verify_user_owns_resource(user: User, resource_user_id: str) -> bool:
    """
    Verify that the authenticated user owns a specific resource.

    Args:
        user: The authenticated user
        resource_user_id: The user ID associated with the resource

    Returns:
        bool: True if user owns the resource, False otherwise
    """
    return str(user.id) == str(resource_user_id)


def get_user_id_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract user ID directly from the JWT token without database lookup.

    Args:
        credentials: HTTP authorization credentials from the request

    Returns:
        str: The user ID from the token
    """
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id