"""SQLModel database models."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    """
    User model for authentication.
    """
    __tablename__ = "users"

    # Primary key
    id: Optional[str] = Field(
        default=None,
        primary_key=True,
        description="Unique user ID"
    )

    # User credentials
    email: str = Field(
        unique=True,
        index=True,
        description="User email address"
    )

    password_hash: str = Field(
        description="Hashed password"
    )

    name: Optional[str] = Field(
        default=None,
        description="User's full name"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="User registration timestamp (UTC)"
    )


class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.

    Security: Every task MUST be associated with a user_id.
    All queries MUST filter by authenticated user's ID.
    """
    __tablename__ = "tasks"

    # Primary key
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-generated task ID"
    )

    # User ID from Better Auth (no foreign key since users table is managed by Better Auth)
    user_id: str = Field(
        index=True,
        nullable=False,
        description="Owner's user ID from Better Auth"
    )

    # Task content
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required, 1-200 characters)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional, max 1000 characters)"
    )

    # Status
    completed: bool = Field(
        default=False,
        index=True,
        description="Completion status (default: false)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task last update timestamp (UTC)"
    )
