from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema for creating a new user
    """
    email: str
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    """
    Schema for user login
    """
    email: str
    password: str


class TokenResponse(BaseModel):
    """
    Schema for token response
    """
    user_id: str
    email: str
    name: Optional[str] = None
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """
    Schema for user information response
    """
    user_id: str
    email: str
    name: Optional[str] = None
    created_at: Optional[str] = None


class TokenRefresh(BaseModel):
    """
    Schema for token refresh request
    """
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """
    Schema for token refresh response
    """
    access_token: str
    token_type: str = "bearer"