"""
Audit Handler (T058)

Processes task events and stores audit entries in Dapr state store.
Each entry captures the event type, before/after state, and metadata.
"""
import os
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
STATE_STORE_NAME = "statestore"

# In-memory fallback for local dev
_local_store: Dict[str, Dict[str, Any]] = {}


async def record_audit_entry(
    event_type: str,
    task_id: int,
    user_id: str,
    payload: Dict[str, Any],
    before_state: Optional[Dict[str, Any]] = None,
    timestamp: Optional[str] = None
) -> str:
    """
    Record an audit entry in the state store.

    Args:
        event_type: Type of event (created, updated, deleted, completed)
        task_id: Affected task ID
        user_id: User who performed the action
        payload: Current state / event data
        before_state: State before the change (for updates)
        timestamp: Event timestamp (ISO format)

    Returns:
        Audit entry ID
    """
    entry_id = str(uuid.uuid4())[:8]
    now = timestamp or datetime.utcnow().isoformat()

    entry = {
        "id": entry_id,
        "event_type": event_type,
        "task_id": task_id,
        "user_id": user_id,
        "payload": payload,
        "before_state": before_state,
        "timestamp": now,
        "recorded_at": datetime.utcnow().isoformat()
    }

    # Store using composite keys for querying
    # Key pattern: audit-{task_id}-{entry_id} for task-level queries
    task_key = f"audit-task-{task_id}-{entry_id}"
    user_key = f"audit-user-{user_id}-{entry_id}"

    try:
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}"
        state_items = [
            {"key": task_key, "value": entry},
            {"key": user_key, "value": entry}
        ]

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=state_items)
            if response.status_code in (200, 204):
                logger.info(f"Audit entry recorded: id={entry_id}, type={event_type}, task={task_id}")

                # Also update the task's audit index
                await _update_audit_index("task", task_id, entry_id)
                await _update_audit_index("user", user_id, entry_id)

                return entry_id
            else:
                logger.error(f"Failed to store audit entry: {response.status_code}")
    except Exception as e:
        logger.warning(f"Dapr state store unavailable, using local: {e}")

    # Fallback to local store
    _local_store[task_key] = entry
    _local_store[user_key] = entry
    return entry_id


async def _update_audit_index(index_type: str, entity_id: Any, entry_id: str):
    """
    Maintain an index of entry IDs for efficient querying.

    Args:
        index_type: "task" or "user"
        entity_id: Task ID or User ID
        entry_id: New audit entry ID to add
    """
    index_key = f"audit-index-{index_type}-{entity_id}"

    try:
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}/{index_key}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Get current index
            response = await client.get(url)
            if response.status_code == 200:
                index_data = response.json()
                if isinstance(index_data, dict):
                    entries = index_data.get("entries", [])
                else:
                    entries = []
            else:
                entries = []

            # Add new entry ID
            entries.append(entry_id)

            # Keep only last 1000 entries
            if len(entries) > 1000:
                entries = entries[-1000:]

            # Save updated index
            save_url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}"
            await client.post(save_url, json=[{
                "key": index_key,
                "value": {"entries": entries, "updated_at": datetime.utcnow().isoformat()}
            }])

    except Exception as e:
        logger.debug(f"Failed to update audit index: {e}")
