"""Pydantic request and response schemas for API validation."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


# Request Schemas

class TaskCreate(BaseModel):
    """
    Request schema for creating a new task.

    Validation:
    - title: Required, 1-200 characters
    - description: Optional, max 1000 characters

    Note: user_id is NOT accepted from request (set from JWT)
    """
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title",
        examples=["Complete backend API implementation"]
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional task description",
        examples=["Implement all REST endpoints with FastAPI and SQLModel"]
    )


class TaskUpdate(BaseModel):
    """
    Request schema for updating an existing task.

    Validation:
    - title: Required, 1-200 characters
    - description: Optional, max 1000 characters

    Note: completed status is NOT updated here (use PATCH /complete endpoint)
    """
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


# Response Schemas

class TaskResponse(BaseModel):
    """
    Response schema for task data.

    Frontend Compatibility:
    - Uses 'is_completed' for frontend (database stores 'completed')
    - Input accepts both 'completed' and 'is_completed'
    - Output always serializes as 'is_completed'
    """
    id: int
    user_id: str
    title: str
    description: Optional[str]
    is_completed: bool = Field(
        alias="completed",           # Accept 'completed' as input
        serialization_alias="is_completed"  # Always output as 'is_completed'
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode (SQLModel -> Pydantic)
        populate_by_name=True  # Allow both 'completed' and 'is_completed' for input
    )


class TaskListResponse(BaseModel):
    """Response schema for task list with metadata."""
    tasks: list[TaskResponse]
    total: int
    status_filter: str
    sort_by: str


class DeleteResponse(BaseModel):
    """Response schema for delete operations."""
    message: str
    deleted_task_id: int


# Authentication Schemas

class SignupRequest(BaseModel):
    """Request schema for user signup."""
    email: str = Field(description="User email address")
    password: str = Field(min_length=6, description="User password (min 6 characters)")
    name: Optional[str] = Field(default=None, description="User's full name")


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: str = Field(description="User email address")
    password: str = Field(description="User password")


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: str
    email: str
    name: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    """Response schema for authentication (signup/login)."""
    token: str = Field(description="JWT authentication token")
    user: UserResponse
