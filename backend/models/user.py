from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    email: str = Field(index=True, nullable=False, unique=True)
    password_hash: str
    salt: str

    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    role: str = Field(default="user")
    timezone: Optional[str] = None
    language: Optional[str] = None

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deactivated_at: Optional[datetime] = None