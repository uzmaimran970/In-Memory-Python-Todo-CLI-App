"""Pydantic request and response schemas for API validation."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# Request Schemas

class TaskCreate(BaseModel):
    """
    Request schema for creating a new task.

    Validation:
    - title: Required, 1-200 characters
    - description: Optional, max 1000 characters
    - priority: Optional (high/medium/low), defaults to medium
    - tags: Optional list of strings
    - due_date: Optional datetime

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
    priority: Optional[str] = Field(
        default="medium",
        description="Task priority: high, medium, or low"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Task tags for categorization"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Task due date (UTC)"
    )


class TaskUpdate(BaseModel):
    """
    Request schema for updating an existing task.

    Validation:
    - title: Required, 1-200 characters
    - description: Optional, max 1000 characters
    - priority: Optional (high/medium/low)
    - tags: Optional list of strings
    - due_date: Optional datetime

    Note: completed status is NOT updated here (use PATCH /complete endpoint)
    """
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Optional[str] = Field(default=None, description="Task priority: high, medium, or low")
    tags: Optional[List[str]] = Field(default=None, description="Task tags")
    due_date: Optional[datetime] = Field(default=None, description="Task due date (UTC)")


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
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
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


# Reminder Schemas (Phase 5 - T038)

class ReminderCreate(BaseModel):
    """Request schema for creating a reminder on a task."""
    remind_at: datetime = Field(description="When to send the reminder (UTC)")

    model_config = ConfigDict(json_schema_extra={
        "examples": [{"remind_at": "2026-01-24T09:00:00Z"}]
    })


class ReminderResponse(BaseModel):
    """Response schema for reminder data."""
    id: int
    task_id: int
    user_id: str
    remind_at: datetime
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Recurrence Schemas (Phase 5)

class RecurrenceRuleCreate(BaseModel):
    """Request schema for creating a recurrence rule."""
    frequency: str = Field(description="daily, weekly, or monthly")
    interval: int = Field(default=1, ge=1, le=365, description="Every N units")
    end_date: Optional[datetime] = Field(default=None, description="Stop recurring after this date")
    days_of_week: Optional[list[int]] = Field(default=None, description="For weekly: days 0=Mon..6=Sun")


class RecurrenceRuleResponse(BaseModel):
    """Response schema for recurrence rule data."""
    id: int
    frequency: str
    interval: int
    end_date: Optional[datetime]
    days_of_week: Optional[list[int]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
