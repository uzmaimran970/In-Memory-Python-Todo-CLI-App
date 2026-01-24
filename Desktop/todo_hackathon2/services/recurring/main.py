"""
Recurring Service Main Entry Point (T028)

Dapr subscription handler for task-events topic.
Processes "completed" events for recurring tasks and
generates next occurrences.
"""
import os
import logging
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from recurrence_calculator import calculate_next_occurrence
from task_client import create_next_task

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Recurring Tasks Service",
    description="Generates next task occurrences when recurring tasks complete",
    version="1.0.0"
)


class TaskEventPayload(BaseModel):
    """Payload schema for task events."""
    event_id: str
    event_type: str
    task_id: int
    user_id: str
    timestamp: str
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


# Dapr subscription configuration
@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.
    Tells Dapr which topics this service subscribes to.
    """
    subscriptions = [
        {
            "pubsubname": "taskpubsub",
            "topic": "task-events",
            "route": "/events/tasks",
            "metadata": {
                "rawPayload": "true"
            }
        }
    ]
    logger.info(f"Returning subscriptions: {subscriptions}")
    return subscriptions


@app.post("/events/tasks")
async def handle_task_event(request: Request):
    """
    Handle task events from Dapr Pub/Sub.

    Only processes "completed" events for tasks with recurrence rules.
    Creates next occurrence via Dapr service invocation to backend-svc.

    CloudEvents format expected.
    """
    try:
        # Parse CloudEvent
        body = await request.json()
        logger.info(f"Received task event: {body.get('event_type', 'unknown')}")

        # Validate event structure
        event_type = body.get("event_type")
        if event_type != "completed":
            logger.debug(f"Ignoring non-completion event: {event_type}")
            return {"status": "ignored", "reason": "not a completion event"}

        # Extract task data
        payload = body.get("payload", {})
        task_id = body.get("task_id")
        user_id = body.get("user_id")
        recurrence_id = payload.get("recurrence_id")

        if not recurrence_id:
            logger.debug(f"Task {task_id} has no recurrence rule, skipping")
            return {"status": "ignored", "reason": "no recurrence rule"}

        logger.info(f"Processing recurring task completion: task_id={task_id}, recurrence_id={recurrence_id}")

        # Fetch recurrence rule from backend via Dapr service invocation
        from task_client import get_recurrence_rule
        rule = await get_recurrence_rule(recurrence_id)

        # Use rule data or defaults
        frequency = "daily"
        interval = 1
        end_date = None
        days_of_week = None

        if rule:
            frequency = rule.get("frequency", "daily")
            interval = rule.get("interval", 1)
            end_date_str = rule.get("end_date")
            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            days_of_week = rule.get("days_of_week")

        # Calculate next occurrence date
        current_due = payload.get("due_date")
        if current_due:
            current_due = datetime.fromisoformat(current_due.replace("Z", "+00:00"))
        else:
            current_due = datetime.utcnow()

        next_due = calculate_next_occurrence(
            current_due=current_due,
            frequency=frequency,
            interval=interval,
            end_date=end_date,
            days_of_week=days_of_week
        )

        if not next_due:
            logger.info(f"No next occurrence for task {task_id} (end date reached)")
            return {"status": "completed", "reason": "recurrence ended"}

        # Create next task occurrence
        new_task = await create_next_task(
            user_id=user_id,
            title=payload.get("title", "Recurring Task"),
            description=payload.get("description"),
            due_date=next_due,
            recurrence_id=recurrence_id,
            priority=payload.get("priority", "medium"),
            tags=payload.get("tags")
        )

        if new_task:
            logger.info(f"Created next occurrence: task_id={new_task.get('id')}, due={next_due}")
            return {
                "status": "success",
                "new_task_id": new_task.get("id"),
                "next_due": next_due.isoformat()
            }
        else:
            logger.error(f"Failed to create next occurrence for task {task_id}")
            return {"status": "error", "reason": "failed to create task"}

    except Exception as e:
        logger.error(f"Error processing task event: {e}", exc_info=True)
        # Return 200 to prevent Dapr retry on processing errors
        # Log for monitoring/alerting
        return {"status": "error", "reason": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "recurring-service"}


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes probes."""
    return {"status": "ready", "service": "recurring-service"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
