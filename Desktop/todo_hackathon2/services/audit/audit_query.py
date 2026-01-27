"""
Audit Query (T059)

Retrieves audit history from Dapr state store.
Supports querying by task ID or user ID.
"""
import os
import logging
from typing import List, Dict, Any
import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
STATE_STORE_NAME = "statestore"

# Reference to local fallback store
from audit_handler import _local_store


async def get_task_history(task_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get audit history for a specific task.

    Args:
        task_id: Task ID to query
        limit: Maximum entries to return

    Returns:
        List of audit entries, newest first
    """
    entries = []

    try:
        # Get task's audit index
        index_key = f"audit-index-task-{task_id}"
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}/{index_key}"

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                index_data = response.json()
                entry_ids = index_data.get("entries", []) if isinstance(index_data, dict) else []

                # Get entries in reverse order (newest first)
                entry_ids = entry_ids[-limit:][::-1]

                for entry_id in entry_ids:
                    entry_key = f"audit-task-{task_id}-{entry_id}"
                    entry_response = await client.get(
                        f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}/{entry_key}"
                    )
                    if entry_response.status_code == 200:
                        entries.append(entry_response.json())

                return entries

    except Exception as e:
        logger.warning(f"Dapr query failed, using local store: {e}")

    # Fallback: search local store
    prefix = f"audit-task-{task_id}-"
    local_entries = [
        v for k, v in _local_store.items()
        if k.startswith(prefix)
    ]
    # Sort by timestamp descending
    local_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return local_entries[:limit]


async def get_user_audit_log(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get audit log for a specific user.

    Args:
        user_id: User ID to query
        limit: Maximum entries to return

    Returns:
        List of audit entries, newest first
    """
    entries = []

    try:
        # Get user's audit index
        index_key = f"audit-index-user-{user_id}"
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}/{index_key}"

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                index_data = response.json()
                entry_ids = index_data.get("entries", []) if isinstance(index_data, dict) else []

                # Get entries in reverse order (newest first)
                entry_ids = entry_ids[-limit:][::-1]

                for entry_id in entry_ids:
                    entry_key = f"audit-user-{user_id}-{entry_id}"
                    entry_response = await client.get(
                        f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}/{entry_key}"
                    )
                    if entry_response.status_code == 200:
                        entries.append(entry_response.json())

                return entries

    except Exception as e:
        logger.warning(f"Dapr query failed, using local store: {e}")

    # Fallback: search local store
    prefix = f"audit-user-{user_id}-"
    local_entries = [
        v for k, v in _local_store.items()
        if k.startswith(prefix)
    ]
    local_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return local_entries[:limit]
