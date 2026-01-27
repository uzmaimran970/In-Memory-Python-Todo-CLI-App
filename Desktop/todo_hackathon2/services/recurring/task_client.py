"""
Task Client (T030)

Creates new task instances via Dapr service invocation.
Communicates with backend-svc to create recurring task occurrences.
"""
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx

logger = logging.getLogger(__name__)

# Dapr sidecar configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
BACKEND_APP_ID = "backend-svc"


async def create_next_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None,
    recurrence_id: Optional[int] = None,
    priority: str = "medium",
    tags: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a new task via Dapr service invocation.

    Uses Dapr sidecar to invoke backend-svc POST /api/tasks endpoint.
    This bypasses JWT auth since it's internal service-to-service call.

    Args:
        user_id: Owner user ID
        title: Task title
        description: Task description (optional)
        due_date: Due date for the new task (optional)
        recurrence_id: FK to recurrence rule (optional)
        priority: Task priority (high/medium/low)
        tags: Task tags (optional)

    Returns:
        Created task data dict, or None on failure
    """
    # Build task payload
    task_payload = {
        "title": title,
        "description": description,
        "priority": priority,
        "tags": tags or [],
        "due_date": due_date.isoformat() if due_date else None,
        "recurrence_id": recurrence_id
    }

    # Remove None values
    task_payload = {k: v for k, v in task_payload.items() if v is not None}

    # Dapr service invocation URL
    # Format: http://localhost:<dapr-port>/v1.0/invoke/<app-id>/method/<method>
    url = f"{DAPR_BASE_URL}/v1.0/invoke/{BACKEND_APP_ID}/method/api/internal/tasks"

    headers = {
        "Content-Type": "application/json",
        # Pass user_id as header for internal service auth
        "X-User-Id": user_id
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info(f"Creating task via Dapr service invocation: {title}")
            response = await client.post(url, json=task_payload, headers=headers)

            if response.status_code == 201:
                task_data = response.json()
                logger.info(f"Task created successfully: id={task_data.get('id')}")
                return task_data
            else:
                logger.error(
                    f"Failed to create task: status={response.status_code}, "
                    f"body={response.text}"
                )
                return None

    except httpx.TimeoutException:
        logger.error(f"Timeout creating task via Dapr: {title}")
        return None
    except httpx.HTTPError as e:
        logger.error(f"HTTP error creating task: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating task: {e}", exc_info=True)
        return None


async def get_recurrence_rule(recurrence_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch recurrence rule details from backend.

    Args:
        recurrence_id: Recurrence rule ID

    Returns:
        Recurrence rule data dict, or None on failure
    """
    url = f"{DAPR_BASE_URL}/v1.0/invoke/{BACKEND_APP_ID}/method/api/recurrence/{recurrence_id}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get recurrence rule {recurrence_id}: {response.status_code}")
                return None

    except Exception as e:
        logger.error(f"Error fetching recurrence rule: {e}")
        return None


async def get_task(task_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch task details from backend.

    Args:
        task_id: Task ID
        user_id: User ID for authorization

    Returns:
        Task data dict, or None on failure
    """
    url = f"{DAPR_BASE_URL}/v1.0/invoke/{BACKEND_APP_ID}/method/api/tasks/{task_id}"
    headers = {"X-User-Id": user_id}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get task {task_id}: {response.status_code}")
                return None

    except Exception as e:
        logger.error(f"Error fetching task: {e}")
        return None
