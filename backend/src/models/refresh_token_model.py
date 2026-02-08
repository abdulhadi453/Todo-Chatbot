from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid


class RefreshTokenBase(SQLModel):
    """Base model for RefreshToken with common fields"""
    user_id: str = Field(nullable=False)
    token_hash: str = Field(nullable=False)
    expires_at: datetime = Field(nullable=False)


class RefreshToken(RefreshTokenBase, table=True):
    """SQLModel for RefreshToken entity"""
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    # Relationship to User (optional depending on implementation)
    # user: Optional["User"] = Relationship(back_populates="refresh_tokens")


class RefreshTokenCreate(RefreshTokenBase):
    """Schema for creating a new refresh token"""
    user_id: str
    token_hash: str
    expires_at: datetime


class RefreshTokenRead(RefreshTokenBase):
    """Schema for reading a refresh token"""
    id: str
    created_at: datetime