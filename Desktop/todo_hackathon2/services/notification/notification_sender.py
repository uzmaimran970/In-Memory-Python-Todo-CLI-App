"""
Notification Sender (T043)

Handles sending notifications to users via various channels.
Currently supports:
- WebSocket push (real-time)
- In-app notification storage

Future channels:
- Email
- Push notifications (FCM/APNs)
"""
import os
import logging
from enum import Enum
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
WEBSOCKET_APP_ID = "websocket-svc"
BACKEND_APP_ID = "backend-svc"


class NotificationType(str, Enum):
    """Types of notifications."""
    REMINDER = "reminder"
    TASK_SHARED = "task_shared"
    TASK_COMPLETED = "task_completed"
    SYSTEM = "system"


async def send_notification(
    user_id: str,
    notification_type: NotificationType,
    title: str,
    body: str,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send a notification to a user.

    Attempts to:
    1. Push via WebSocket (real-time) to websocket-svc
    2. Store as in-app notification in backend-svc

    Args:
        user_id: Target user ID
        notification_type: Type of notification
        title: Notification title
        body: Notification body text
        metadata: Additional data (task_id, etc.)

    Returns:
        True if at least one channel succeeded
    """
    success = False

    # Channel 1: Real-time push via WebSocket service
    ws_success = await _push_websocket(user_id, title, body, notification_type, metadata)
    if ws_success:
        success = True

    # Channel 2: Store in-app notification
    store_success = await _store_notification(user_id, notification_type, title, body, metadata)
    if store_success:
        success = True

    if not success:
        logger.error(f"All notification channels failed for user {user_id}")

    return success


async def _push_websocket(
    user_id: str,
    title: str,
    body: str,
    notification_type: NotificationType,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Push notification via WebSocket service.

    Uses Dapr service invocation to call websocket-svc.
    """
    url = f"{DAPR_BASE_URL}/v1.0/invoke/{WEBSOCKET_APP_ID}/method/notify"

    payload = {
        "user_id": user_id,
        "type": notification_type.value,
        "title": title,
        "body": body,
        "metadata": metadata or {}
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                logger.info(f"WebSocket notification sent to {user_id}")
                return True
            else:
                logger.debug(f"WebSocket push failed: {response.status_code}")
                return False
    except Exception as e:
        logger.debug(f"WebSocket service unavailable: {e}")
        return False


async def _store_notification(
    user_id: str,
    notification_type: NotificationType,
    title: str,
    body: str,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Store notification in backend database.

    Uses Dapr service invocation to call backend-svc internal API.
    """
    url = f"{DAPR_BASE_URL}/v1.0/invoke/{BACKEND_APP_ID}/method/api/internal/notifications"

    payload = {
        "user_id": user_id,
        "type": notification_type.value,
        "title": title,
        "body": body,
        "metadata": metadata or {}
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code in (200, 201):
                logger.info(f"Notification stored for {user_id}")
                return True
            else:
                logger.warning(f"Failed to store notification: {response.status_code}")
                return False
    except Exception as e:
        logger.warning(f"Backend service unavailable for notification storage: {e}")
        return False
