"""
T025: Event Publisher Service for Dapr Pub/Sub

Publishes task events to Kafka topics via Dapr sidecar.
Topics:
- task-events: All CRUD operations (for recurring-service, audit-service)
- task-updates: All changes (for websocket-service)
- reminders: When due dates are set (for notification-service)
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Any
from uuid import uuid4

import httpx

logger = logging.getLogger(__name__)

# Dapr sidecar HTTP port (default: 3500)
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = "taskpubsub"

# Topics
TOPIC_TASK_EVENTS = "task-events"
TOPIC_TASK_UPDATES = "task-updates"
TOPIC_REMINDERS = "reminders"


class EventPublisher:
    """
    Publishes events to Kafka via Dapr Pub/Sub.
    All events are CloudEvents format.
    """

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.enabled = os.getenv("DAPR_ENABLED", "false").lower() == "true"

    async def _publish(self, topic: str, data: dict, event_type: str) -> bool:
        """
        Publish a CloudEvent to a Dapr topic.
        Returns True if successful, False otherwise.
        """
        if not self.enabled:
            logger.info(f"Dapr disabled, skipping publish to {topic}: {event_type}")
            return True

        url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"

        # CloudEvents metadata
        headers = {
            "Content-Type": "application/cloudevents+json",
            "ce-specversion": "1.0",
            "ce-type": f"com.todo.{event_type}",
            "ce-source": "backend-svc",
            "ce-id": str(uuid4()),
            "ce-time": datetime.utcnow().isoformat() + "Z",
        }

        try:
            response = await self.client.post(url, json=data, headers=headers)
            response.raise_for_status()
            logger.info(f"Published {event_type} to {topic}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            return False

    async def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        user_id: str,
        task_data: dict,
        before_state: Optional[dict] = None
    ) -> bool:
        """
        Publish a task CRUD event to task-events topic.
        Consumed by: recurring-service, audit-service
        """
        payload = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "task_id": task_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": task_data,
            "metadata": {
                "source": "backend-svc",
                "before_state": before_state
            }
        }

        # Publish to both task-events and task-updates
        result1 = await self._publish(TOPIC_TASK_EVENTS, payload, f"task.{event_type}")
        result2 = await self._publish(TOPIC_TASK_UPDATES, payload, f"task.{event_type}")

        return result1 and result2

    async def publish_reminder_event(
        self,
        action: str,  # "schedule", "cancel", "fire"
        task_id: int,
        user_id: str,
        scheduled_time: datetime,
        task_title: str,
        reminder_id: Optional[int] = None
    ) -> bool:
        """
        Publish a reminder event to reminders topic.
        Consumed by: notification-service
        """
        payload = {
            "reminder_id": reminder_id,
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_time": scheduled_time.isoformat(),
            "action": action,
            "task_title": task_title
        }

        return await self._publish(TOPIC_REMINDERS, payload, f"reminder.{action}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get or create the singleton EventPublisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = EventPublisher()
    return _publisher


async def publish_task_created(task_id: int, user_id: str, task_data: dict) -> bool:
    """Helper: Publish task created event."""
    publisher = get_event_publisher()
    return await publisher.publish_task_event("created", task_id, user_id, task_data)


async def publish_task_updated(
    task_id: int,
    user_id: str,
    task_data: dict,
    before_state: dict
) -> bool:
    """Helper: Publish task updated event."""
    publisher = get_event_publisher()
    return await publisher.publish_task_event(
        "updated", task_id, user_id, task_data, before_state
    )


async def publish_task_deleted(task_id: int, user_id: str, task_data: dict) -> bool:
    """Helper: Publish task deleted event."""
    publisher = get_event_publisher()
    return await publisher.publish_task_event("deleted", task_id, user_id, task_data)


async def publish_task_completed(
    task_id: int,
    user_id: str,
    task_data: dict,
    before_state: dict
) -> bool:
    """Helper: Publish task completed event."""
    publisher = get_event_publisher()
    return await publisher.publish_task_event(
        "completed", task_id, user_id, task_data, before_state
    )


async def schedule_reminder(
    task_id: int,
    user_id: str,
    scheduled_time: datetime,
    task_title: str,
    reminder_id: int
) -> bool:
    """Helper: Schedule a new reminder."""
    publisher = get_event_publisher()
    return await publisher.publish_reminder_event(
        "schedule", task_id, user_id, scheduled_time, task_title, reminder_id
    )


async def cancel_reminder(
    task_id: int,
    user_id: str,
    reminder_id: int
) -> bool:
    """Helper: Cancel an existing reminder."""
    publisher = get_event_publisher()
    return await publisher.publish_reminder_event(
        "cancel", task_id, user_id, datetime.utcnow(), "", reminder_id
    )
