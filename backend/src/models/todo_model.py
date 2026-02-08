from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel
from passlib.context import CryptContext
from enum import Enum

# Password hashing context - use pbkdf2:sha256 as alternative to bcrypt
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


class UserBase(SQLModel):
    """Base model for User with common fields"""
    email: str = Field(unique=True, nullable=False)
    name: Optional[str] = None
    email_verified: bool = Field(default=False)
    disabled: bool = Field(default=False)


class User(UserBase, table=True):
    """SQLModel for User entity with authentication fields"""
    __table_args__ = {'extend_existing': True}

    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)  # Using string ID to match requirements
    password_hash: str = Field(nullable=False)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    @staticmethod
    def hash_password(password: str) -> str:
        # Truncate password to 72 characters to comply with bcrypt limit
        truncated_password = password[:72] if len(password) > 72 else password
        return pwd_context.hash(truncated_password)

    def verify_password(self, password: str) -> bool:
        # Truncate password to 72 characters to comply with bcrypt limit
        truncated_password = password[:72] if len(password) > 72 else password
        return pwd_context.verify(truncated_password, self.password_hash)


# Define separate base classes for different contexts
class TodoTaskCommonFields(SQLModel):
    """Common fields for TodoTask excluding user_id and ID fields"""
    title: str = Field(min_length=1)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    category: Optional[str] = None
    priority: Optional[str] = Field(default="medium")  # Can be 'low', 'medium', 'high'
    due_date: Optional[datetime] = Field(default=None)  # Database field should be datetime

class TodoTask(TodoTaskCommonFields, table=True):
    """SQLModel for TodoTask entity (database model)"""
    __table_args__ = {'extend_existing': True}

    id: Optional[str] = Field(default=None, primary_key=True)  # Changed to string to match frontend expectations
    user_id: str = Field(min_length=1)  # Required in the database model
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

class TodoTaskCreate(SQLModel):
    """Schema for creating a new todo task - accepts string dates from API"""
    title: str = Field(min_length=1)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    category: Optional[str] = None
    priority: Optional[str] = Field(default="medium")  # Can be 'low', 'medium', 'high'
    due_date: Optional[str] = None  # Accept string from API

class TodoTaskRead(SQLModel):
    """Schema for reading a todo task - returns string dates for API"""
    id: str
    title: str
    description: Optional[str] = None
    completed: bool
    category: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str]  # Return string for API
    user_id: str  # Include user_id when reading
    created_at: datetime
    updated_at: datetime

class TodoTaskUpdate(BaseModel):
    """Schema for updating a todo task"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None

class TodoTaskPatch(BaseModel):
    """Schema for patching a todo task (toggle completion)"""
    completed: bool



class UserCreate(UserBase):
    """Schema for creating a new user"""
    email: str
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    user_id: str
    email: str
    name: Optional[str] = None
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user response"""
    user_id: str
    email: str
    name: Optional[str] = None
    created_at: Optional[str] = None


class TokenRefresh(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Schema for token refresh response"""
    access_token: str
    token_type: str = "bearer"