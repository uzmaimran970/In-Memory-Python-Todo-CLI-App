"""
Reminder API endpoints (T038-T040).

Allows users to set and manage reminders on tasks.
Publishes reminder events to Kafka via Dapr Pub/Sub.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime

from app.database import get_session
from app.auth import get_current_user_id
from app.models import Task, Reminder, ReminderStatus, Notification
from app.schemas import ReminderCreate, ReminderResponse
from app.services.event_publisher import schedule_reminder, cancel_reminder
from sqlalchemy import desc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["reminders"])


@router.post("/tasks/{task_id}/reminder", status_code=status.HTTP_201_CREATED, response_model=ReminderResponse)
async def create_reminder(
    task_id: int,
    reminder_data: ReminderCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ReminderResponse:
    """
    Create a reminder for a task (T038).

    Sets a reminder to notify the user at the specified time.
    Publishes a reminder.scheduled event to Kafka.

    Args:
        task_id: Task ID from path
        reminder_data: Reminder time (remind_at in UTC)
        current_user_id: Authenticated user from JWT
        session: Database session

    Returns:
        ReminderResponse: Created reminder

    Raises:
        404: Task not found
        403: Task belongs to another user
        400: Reminder time is in the past
        409: Task already has an active reminder
    """
    # Verify task exists and belongs to user
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to set reminder on this task"
        )

    # Validate reminder time is in the future
    if reminder_data.remind_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reminder time must be in the future"
        )

    # Check for existing active reminder on this task
    existing = session.exec(
        select(Reminder).where(
            Reminder.task_id == task_id,
            Reminder.user_id == current_user_id,
            Reminder.status == ReminderStatus.PENDING
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task already has an active reminder. Delete it first."
        )

    # Create reminder
    reminder = Reminder(
        task_id=task_id,
        user_id=current_user_id,
        remind_at=reminder_data.remind_at,
        status=ReminderStatus.PENDING,
        created_at=datetime.utcnow()
    )

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    # Publish reminder scheduled event (T040)
    try:
        await schedule_reminder(
            task_id=task_id,
            user_id=current_user_id,
            scheduled_time=reminder_data.remind_at,
            task_title=task.title,
            reminder_id=reminder.id
        )
    except Exception as e:
        logger.warning(f"Failed to publish reminder scheduled event: {e}")

    return ReminderResponse.model_validate(reminder)


@router.delete("/tasks/{task_id}/reminder", response_model=dict)
async def delete_reminder(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Delete/cancel a reminder for a task (T039).

    Cancels any active reminder on the specified task.
    Publishes a reminder.cancelled event to Kafka.

    Args:
        task_id: Task ID from path
        current_user_id: Authenticated user from JWT
        session: Database session

    Returns:
        Success message

    Raises:
        404: Task not found or no active reminder
        403: Task belongs to another user
    """
    # Verify task exists and belongs to user
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task's reminders"
        )

    # Find active reminder
    reminder = session.exec(
        select(Reminder).where(
            Reminder.task_id == task_id,
            Reminder.user_id == current_user_id,
            Reminder.status == ReminderStatus.PENDING
        )
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active reminder found for this task"
        )

    # Cancel the reminder
    reminder.status = ReminderStatus.CANCELLED
    session.add(reminder)
    session.commit()

    # Publish reminder cancelled event (T040)
    try:
        await cancel_reminder(
            task_id=task_id,
            user_id=current_user_id,
            reminder_id=reminder.id
        )
    except Exception as e:
        logger.warning(f"Failed to publish reminder cancelled event: {e}")

    return {"message": "Reminder cancelled successfully", "task_id": task_id}


@router.get("/tasks/{task_id}/reminder", response_model=ReminderResponse)
async def get_reminder(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ReminderResponse:
    """
    Get the active reminder for a task.

    Args:
        task_id: Task ID from path
        current_user_id: Authenticated user from JWT
        session: Database session

    Returns:
        ReminderResponse: Active reminder data

    Raises:
        404: No active reminder found
        403: Task belongs to another user
    """
    # Verify task exists and belongs to user
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this task's reminders"
        )

    # Find active reminder
    reminder = session.exec(
        select(Reminder).where(
            Reminder.task_id == task_id,
            Reminder.user_id == current_user_id,
            Reminder.status == ReminderStatus.PENDING
        )
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active reminder found for this task"
        )

    return ReminderResponse.model_validate(reminder)


# ============================================================================
# Notification Endpoints (Phase 5 - User-facing)
# ============================================================================

@router.get("/notifications")
async def get_notifications(
    limit: int = 50,
    unread_only: bool = False,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Get notifications for the authenticated user."""
    query = select(Notification).where(
        Notification.user_id == current_user_id
    )
    if unread_only:
        query = query.where(Notification.read == False)

    query = query.order_by(desc(Notification.created_at)).limit(limit)
    notifications = session.exec(query).all()

    # Get unread count
    unread_query = select(Notification).where(
        Notification.user_id == current_user_id,
        Notification.read == False
    )
    unread_count = len(session.exec(unread_query).all())

    return {
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "body": n.body,
                "type": n.type,
                "read": n.read,
                "created_at": n.created_at.isoformat()
            }
            for n in notifications
        ],
        "total": len(notifications),
        "unread_count": unread_count
    }


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Mark a notification as read."""
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    notification.read = True
    session.add(notification)
    session.commit()
    return {"message": "Notification marked as read", "id": notification_id}


@router.patch("/notifications/read-all")
async def mark_all_read(
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Mark all notifications as read for the user."""
    notifications = session.exec(
        select(Notification).where(
            Notification.user_id == current_user_id,
            Notification.read == False
        )
    ).all()

    for n in notifications:
        n.read = True
        session.add(n)

    session.commit()
    return {"message": "All notifications marked as read", "count": len(notifications)}
