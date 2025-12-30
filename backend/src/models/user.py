"""User model for authentication."""

from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel, Column, DateTime
from sqlalchemy.sql import func


class User(SQLModel, table=True):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique user identifier (UUID)",
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address (unique)",
    )
    hashed_password: str = Field(
        max_length=255,
        description="Bcrypt hashed password",
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User's full name",
    )
    is_active: bool = Field(
        default=True,
        description="Whether user account is active",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Account creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        ),
        description="Last update timestamp",
    )

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
            }
        }
