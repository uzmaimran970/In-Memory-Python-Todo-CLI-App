"""
Audit Service Main Entry Point (T057)

Subscribes to task-events and records all changes
in the audit trail for compliance and history.
"""
import os
import logging
from fastapi import FastAPI, Request
from audit_handler import record_audit_entry
from audit_query import get_task_history, get_user_audit_log

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Audit Service",
    description="Records task change history for audit trail",
    version="1.0.0"
)


# Dapr subscription configuration
@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr subscription endpoint."""
    subscriptions = [
        {
            "pubsubname": "taskpubsub",
            "topic": "task-events",
            "route": "/events/audit",
            "metadata": {
                "rawPayload": "true"
            }
        }
    ]
    return subscriptions


@app.post("/events/audit")
async def handle_audit_event(request: Request):
    """
    Handle all task events for audit logging.

    Records every task CRUD operation with before/after state.
    Stores in Dapr state store for persistence.

    CloudEvents format expected.
    """
    try:
        body = await request.json()
        event_type = body.get("event_type")
        task_id = body.get("task_id")
        user_id = body.get("user_id")

        logger.info(f"Audit event: type={event_type}, task_id={task_id}, user_id={user_id}")

        # Record the audit entry
        entry_id = await record_audit_entry(
            event_type=event_type,
            task_id=task_id,
            user_id=user_id,
            payload=body.get("payload", {}),
            before_state=body.get("before_state"),
            timestamp=body.get("timestamp")
        )

        return {"status": "recorded", "entry_id": entry_id}

    except Exception as e:
        logger.error(f"Error recording audit event: {e}", exc_info=True)
        return {"status": "error", "reason": str(e)}


@app.get("/api/audit/task/{task_id}")
async def get_task_audit_history(task_id: int, limit: int = 50):
    """
    Get audit history for a specific task.

    Used by backend via Dapr service invocation.

    Args:
        task_id: Task ID
        limit: Max entries to return (default 50)

    Returns:
        List of audit entries for the task
    """
    history = await get_task_history(task_id, limit=limit)
    return {"task_id": task_id, "entries": history, "total": len(history)}


@app.get("/api/audit/user/{user_id}")
async def get_user_history(user_id: str, limit: int = 100):
    """
    Get audit log for a specific user.

    Args:
        user_id: User ID
        limit: Max entries to return (default 100)

    Returns:
        List of audit entries for the user
    """
    log = await get_user_audit_log(user_id, limit=limit)
    return {"user_id": user_id, "entries": log, "total": len(log)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "audit-service"}


@app.get("/ready")
async def readiness_check():
    """Readiness check."""
    return {"status": "ready", "service": "audit-service"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", "8004"))
    uvicorn.run(app, host="0.0.0.0", port=port)
