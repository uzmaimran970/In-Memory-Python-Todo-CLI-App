"""
Internal API endpoints for service-to-service communication.

These endpoints are intended for Dapr service invocation from
microservices (recurring-service, notification-service, etc.)

Security:
- No JWT validation (service-to-service trust)
- User ID passed via X-User-Id header
- Should only be accessible within the cluster
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlmodel import Session
from datetime import datetime
from typing import Optional, List

from app.database import get_session
from app.models import Task, TaskPriority, RecurrenceRule, Notification, NotificationType
from app.schemas import TaskResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Create router with /api/internal prefix
router = APIRouter(prefix="/api/internal", tags=["internal"])


class InternalTaskCreate:
    """Schema for internal task creation."""
    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None,
        recurrence_id: Optional[int] = None
    ):
        self.title = title
        self.description = description
        self.priority = priority
        self.tags = tags
        self.due_date = due_date
        self.recurrence_id = recurrence_id


@router.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task_internal(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    recurrence_id: Optional[int] = None,
    x_user_id: str = Header(..., alias="X-User-Id"),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task (internal service-to-service endpoint).

    Used by microservices like recurring-service to create tasks
    via Dapr service invocation.

    Security:
    - No JWT validation (trusted internal call)
    - User ID from X-User-Id header (required)

    Args:
        title: Task title
        description: Task description (optional)
        priority: Task priority (high/medium/low)
        tags: Task tags (optional)
        due_date: Due date ISO string (optional)
        recurrence_id: Recurrence rule FK (optional)
        x_user_id: User ID from header
        session: Database session

    Returns:
        TaskResponse: Created task
    """
    logger.info(f"Internal task creation: user_id={x_user_id}, title={title}")

    # Validate priority
    try:
        task_priority = TaskPriority(priority)
    except ValueError:
        task_priority = TaskPriority.MEDIUM

    # Parse due date
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            logger.warning(f"Invalid due_date format: {due_date}")

    # Validate recurrence_id exists if provided
    if recurrence_id:
        rule = session.get(RecurrenceRule, recurrence_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Recurrence rule {recurrence_id} not found"
            )

    # Create task
    new_task = Task(
        user_id=x_user_id,
        title=title,
        description=description,
        completed=False,
        priority=task_priority,
        tags=tags or [],
        due_date=parsed_due_date,
        recurrence_id=recurrence_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    logger.info(f"Internal task created: id={new_task.id}")
    return TaskResponse.model_validate(new_task)


@router.get("/recurrence/{recurrence_id}")
async def get_recurrence_rule(
    recurrence_id: int,
    session: Session = Depends(get_session)
):
    """
    Get recurrence rule details (internal endpoint).

    Used by recurring-service to fetch rule configuration.

    Args:
        recurrence_id: Recurrence rule ID
        session: Database session

    Returns:
        Recurrence rule data
    """
    rule = session.get(RecurrenceRule, recurrence_id)

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurrence rule not found"
        )

    return {
        "id": rule.id,
        "frequency": rule.frequency,
        "interval": rule.interval,
        "end_date": rule.end_date.isoformat() if rule.end_date else None,
        "days_of_week": rule.days_of_week,
        "created_at": rule.created_at.isoformat()
    }


class NotificationCreate(BaseModel):
    """Schema for internal notification creation."""
    user_id: str
    type: str = "system"
    title: str
    body: str
    metadata: Optional[dict] = None


@router.post("/notifications", status_code=status.HTTP_201_CREATED)
async def create_notification_internal(
    data: NotificationCreate,
    session: Session = Depends(get_session)
):
    """
    Store a notification (internal service-to-service endpoint).

    Used by notification-service to persist notifications.
    """
    try:
        notif_type = NotificationType(data.type)
    except ValueError:
        notif_type = NotificationType.SYSTEM

    notification = Notification(
        user_id=data.user_id,
        title=data.title,
        body=data.body,
        type=notif_type,
        read=False,
        created_at=datetime.utcnow()
    )

    session.add(notification)
    session.commit()
    session.refresh(notification)

    logger.info(f"Notification stored: id={notification.id}, user={data.user_id}")
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "title": notification.title,
        "type": notification.type,
        "created_at": notification.created_at.isoformat()
    }
