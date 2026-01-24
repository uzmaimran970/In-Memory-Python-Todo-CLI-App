"""SQLModel database models."""
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from datetime import datetime
from typing import Optional
from uuid import uuid4
from enum import Enum


class MessageRole(str, Enum):
    """Role of a message in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"


# Phase 5: Task enums for priority and recurrence
class TaskPriority(str, Enum):
    """Priority level for tasks."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurrenceFrequency(str, Enum):
    """Frequency for recurring tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReminderStatus(str, Enum):
    """Status of a reminder."""
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    """Type of notification."""
    REMINDER = "reminder"
    SYSTEM = "system"


class TaskEventType(str, Enum):
    """Type of task event for audit logging."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    COMPLETED = "completed"


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

    # Phase 5: Extended fields (T022, T024)
    priority: Optional[TaskPriority] = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority (high/medium/low)"
    )

    tags: Optional[list] = Field(
        default=None,
        sa_column=Column(JSON),
        description="User-defined tags (max 10)"
    )

    due_date: Optional[datetime] = Field(
        default=None,
        description="Task due date/time"
    )

    recurrence_id: Optional[int] = Field(
        default=None,
        foreign_key="recurrence_rules.id",
        description="FK to recurrence rule"
    )


# T021, T023: Recurrence Rule model for recurring tasks
class RecurrenceRule(SQLModel, table=True):
    """
    Recurrence pattern for recurring tasks.
    When a recurring task is completed, a new task is generated
    based on this rule.
    """
    __tablename__ = "recurrence_rules"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-generated recurrence rule ID"
    )

    frequency: RecurrenceFrequency = Field(
        nullable=False,
        description="Recurrence frequency (daily/weekly/monthly)"
    )

    interval: int = Field(
        default=1,
        ge=1,
        description="Every N units (default: 1)"
    )

    end_date: Optional[datetime] = Field(
        default=None,
        description="Stop recurring after this date"
    )

    days_of_week: Optional[list] = Field(
        default=None,
        sa_column=Column(JSON),
        description="For weekly: 0=Mon..6=Sun"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Rule creation timestamp"
    )


# T033: Reminder model for due date notifications
class Reminder(SQLModel, table=True):
    """
    Scheduled reminder for a task.
    Fires at scheduled_time to notify the user.
    """
    __tablename__ = "reminders"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-generated reminder ID"
    )

    task_id: int = Field(
        nullable=False,
        foreign_key="tasks.id",
        index=True,
        description="Associated task ID"
    )

    user_id: str = Field(
        nullable=False,
        index=True,
        description="User to notify"
    )

    remind_at: datetime = Field(
        nullable=False,
        description="When to fire the reminder"
    )

    status: ReminderStatus = Field(
        default=ReminderStatus.PENDING,
        description="Reminder status"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Reminder creation timestamp"
    )


# T055: Audit Entry model for operation logging
class AuditEntry(SQLModel, table=True):
    """
    Immutable audit log entry for task operations.
    Records all CRUD operations for accountability.
    """
    __tablename__ = "audit_entries"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-generated audit entry ID"
    )

    event_type: TaskEventType = Field(
        nullable=False,
        description="Type of operation"
    )

    task_id: int = Field(
        nullable=False,
        index=True,
        description="Affected task ID"
    )

    user_id: str = Field(
        nullable=False,
        index=True,
        description="User who performed the action"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="When the action occurred"
    )

    before_state: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Task state before change"
    )

    after_state: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Task state after change"
    )


# T034: Notification model for user inbox
class Notification(SQLModel, table=True):
    """
    User notification for reminders and system messages.
    """
    __tablename__ = "notifications"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-generated notification ID"
    )

    user_id: str = Field(
        nullable=False,
        index=True,
        description="Recipient user ID"
    )

    title: str = Field(
        nullable=False,
        max_length=200,
        description="Notification title"
    )

    body: str = Field(
        nullable=False,
        max_length=1000,
        description="Notification content"
    )

    type: NotificationType = Field(
        default=NotificationType.SYSTEM,
        description="Notification type"
    )

    read: bool = Field(
        default=False,
        description="Whether user has seen it"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Notification creation timestamp"
    )


class Conversation(SQLModel, table=True):
    """
    Conversation model for chat sessions.
    Each user has one active conversation at a time.
    """
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Unique conversation ID"
    )
    user_id: str = Field(
        unique=True,
        nullable=False,
        index=True,
        description="Owner user ID (one conversation per user)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Conversation start timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last activity timestamp"
    )


class Message(SQLModel, table=True):
    """
    Message model for chat messages.
    Stores both user and assistant messages in a conversation.
    """
    __tablename__ = "messages"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Unique message ID"
    )
    conversation_id: str = Field(
        nullable=False,
        index=True,
        description="Parent conversation ID"
    )
    role: MessageRole = Field(
        nullable=False,
        description="Message sender role (user/assistant)"
    )
    content: str = Field(
        nullable=False,
        description="Message text content"
    )
    tool_calls: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Tool calls made by assistant (JSON)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Message timestamp"
    )
