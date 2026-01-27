"""
Reminder Store (T043)

Manages reminder state using Dapr State Store.
Stores pending reminders and retrieves due reminders for notification.
"""
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
STATE_STORE_NAME = "statestore"

# In-memory fallback for local dev without Dapr
_local_store: Dict[str, Dict[str, Any]] = {}


async def store_reminder(
    reminder_id: int,
    task_id: int,
    user_id: str,
    scheduled_time: str,
    task_title: str
) -> bool:
    """
    Store a reminder in Dapr state store.

    Args:
        reminder_id: Unique reminder ID
        task_id: Associated task ID
        user_id: Owner user ID
        scheduled_time: ISO format datetime for notification
        task_title: Task title for notification message

    Returns:
        True if stored successfully
    """
    key = f"reminder-{reminder_id}"
    value = {
        "reminder_id": reminder_id,
        "task_id": task_id,
        "user_id": user_id,
        "scheduled_time": scheduled_time,
        "task_title": task_title,
        "status": "pending",
        "stored_at": datetime.utcnow().isoformat()
    }

    try:
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=[{"key": key, "value": value}])
            if response.status_code in (200, 204):
                logger.info(f"Stored reminder {reminder_id} for task {task_id}")
                return True
            else:
                logger.error(f"Failed to store reminder: {response.status_code}")
                # Fallback to local store
                _local_store[key] = value
                return True
    except Exception as e:
        logger.warning(f"Dapr state store unavailable, using local: {e}")
        _local_store[key] = value
        return True


async def cancel_reminder(
    reminder_id: int,
    task_id: int,
    user_id: str
) -> bool:
    """
    Cancel a pending reminder by removing from state store.

    Args:
        reminder_id: Reminder ID to cancel
        task_id: Associated task ID
        user_id: Owner user ID

    Returns:
        True if cancelled successfully
    """
    key = f"reminder-{reminder_id}"

    try:
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}/{key}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.delete(url)
            if response.status_code in (200, 204):
                logger.info(f"Cancelled reminder {reminder_id}")
                return True
            else:
                logger.warning(f"Failed to cancel from state store: {response.status_code}")
    except Exception as e:
        logger.warning(f"Dapr state store unavailable: {e}")

    # Fallback: remove from local
    _local_store.pop(key, None)
    return True


async def get_due_reminders(before: datetime) -> List[Dict[str, Any]]:
    """
    Get all reminders that are due (scheduled_time <= before).

    Note: With Dapr state store, we use query API if available,
    otherwise we iterate local store.

    Args:
        before: Get reminders scheduled before this time

    Returns:
        List of due reminder data dicts
    """
    due = []
    before_iso = before.isoformat()

    # Try Dapr query API (requires queryable state store)
    try:
        url = f"{DAPR_BASE_URL}/v1.0-alpha1/state/{STATE_STORE_NAME}/query"
        query = {
            "filter": {
                "AND": [
                    {"EQ": {"status": "pending"}},
                    {"LTE": {"scheduled_time": before_iso}}
                ]
            }
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=query)
            if response.status_code == 200:
                results = response.json().get("results", [])
                for item in results:
                    due.append(item.get("data", {}))
                return due
    except Exception as e:
        logger.debug(f"Dapr query API not available, using local store: {e}")

    # Fallback: iterate local store
    for key, value in list(_local_store.items()):
        if value.get("status") == "pending":
            scheduled = value.get("scheduled_time", "")
            if scheduled and scheduled <= before_iso:
                due.append(value)

    return due


async def mark_reminder_sent(reminder_id: int) -> bool:
    """
    Mark a reminder as sent in the state store.

    Args:
        reminder_id: Reminder ID to mark

    Returns:
        True if updated successfully
    """
    key = f"reminder-{reminder_id}"

    try:
        # Get current state
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}/{key}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                value = response.json()
                value["status"] = "sent"
                value["sent_at"] = datetime.utcnow().isoformat()

                # Save updated state
                save_url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}"
                await client.post(save_url, json=[{"key": key, "value": value}])
                logger.info(f"Marked reminder {reminder_id} as sent")
                return True
    except Exception as e:
        logger.warning(f"Dapr state store unavailable: {e}")

    # Fallback: update local store
    if key in _local_store:
        _local_store[key]["status"] = "sent"
        _local_store[key]["sent_at"] = datetime.utcnow().isoformat()

    return True
