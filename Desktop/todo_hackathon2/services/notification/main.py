"""
Notification Service Main Entry Point (T042)

Dapr subscription handler for reminders topic.
Processes scheduled reminders and sends notifications.
Also runs a cron job to check for due reminders.
"""
import os
import logging
from fastapi import FastAPI, Request
from datetime import datetime, timedelta
from typing import Dict, Any, List
from notification_sender import send_notification, NotificationType
from reminder_store import (
    store_reminder,
    cancel_reminder,
    get_due_reminders,
    mark_reminder_sent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Handles task reminders and notifications",
    version="1.0.0"
)


# Dapr subscription configuration
@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr subscription endpoint."""
    subscriptions = [
        {
            "pubsubname": "taskpubsub",
            "topic": "reminders",
            "route": "/events/reminders",
            "metadata": {
                "rawPayload": "true"
            }
        }
    ]
    return subscriptions


@app.post("/events/reminders")
async def handle_reminder_event(request: Request):
    """
    Handle reminder events from Dapr Pub/Sub.

    Processes:
    - reminder.scheduled: Store reminder for future notification
    - reminder.cancelled: Remove pending reminder

    Args:
        request: FastAPI request with CloudEvent body
    """
    try:
        body = await request.json()
        action = body.get("action")
        logger.info(f"Received reminder event: action={action}")

        if action == "scheduled":
            # Store reminder for later notification
            await store_reminder(
                reminder_id=body.get("reminder_id"),
                task_id=body.get("task_id"),
                user_id=body.get("user_id"),
                scheduled_time=body.get("scheduled_time"),
                task_title=body.get("task_title")
            )
            return {"status": "stored"}

        elif action == "cancelled":
            # Cancel pending reminder
            await cancel_reminder(
                reminder_id=body.get("reminder_id"),
                task_id=body.get("task_id"),
                user_id=body.get("user_id")
            )
            return {"status": "cancelled"}

        else:
            logger.debug(f"Unknown reminder action: {action}")
            return {"status": "ignored"}

    except Exception as e:
        logger.error(f"Error processing reminder event: {e}", exc_info=True)
        return {"status": "error", "reason": str(e)}


@app.post("/cron/check-reminders")
async def check_due_reminders():
    """
    Cron job handler: Check for due reminders.

    Called by Dapr cron binding every 60 seconds.
    Finds reminders due within the next 60s and sends notifications.
    """
    try:
        now = datetime.utcnow()
        due_reminders = await get_due_reminders(before=now)

        if not due_reminders:
            return {"status": "no_due_reminders"}

        logger.info(f"Found {len(due_reminders)} due reminders")

        sent_count = 0
        for reminder in due_reminders:
            success = await send_notification(
                user_id=reminder["user_id"],
                notification_type=NotificationType.REMINDER,
                title=f"Reminder: {reminder.get('task_title', 'Task')}",
                body=f"Your task '{reminder.get('task_title')}' needs attention!",
                metadata={
                    "task_id": reminder["task_id"],
                    "reminder_id": reminder["reminder_id"]
                }
            )
            if success:
                await mark_reminder_sent(reminder["reminder_id"])
                sent_count += 1

        return {"status": "processed", "sent": sent_count, "total": len(due_reminders)}

    except Exception as e:
        logger.error(f"Error checking due reminders: {e}", exc_info=True)
        return {"status": "error", "reason": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "notification-service"}


@app.get("/ready")
async def readiness_check():
    """Readiness check."""
    return {"status": "ready", "service": "notification-service"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)
