"""
WebSocket Service Main Entry Point (T047)

Handles:
- WebSocket connections for real-time updates
- Dapr Pub/Sub subscription to task-updates topic
- Push notifications to specific users via /notify endpoint
"""
import os
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query
from typing import Optional
from connection_manager import manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="WebSocket Service",
    description="Real-time task updates via WebSocket",
    version="1.0.0"
)


# Dapr subscription configuration
@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr subscription endpoint."""
    subscriptions = [
        {
            "pubsubname": "taskpubsub",
            "topic": "task-updates",
            "route": "/events/task-updates",
            "metadata": {
                "rawPayload": "true"
            }
        }
    ]
    return subscriptions


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: Optional[str] = Query(default=None)
):
    """
    WebSocket endpoint for real-time task updates.

    Client connects with user_id in path and optional JWT token
    in query string for authentication.

    Messages sent to client:
    - task.created: New task created
    - task.updated: Task modified
    - task.deleted: Task removed
    - task.completed: Task marked complete
    - notification: Push notification
    - ping: Keep-alive

    Args:
        websocket: WebSocket connection
        user_id: User ID from path
        token: Optional JWT token for auth (query param)
    """
    # TODO: Validate JWT token for production
    # For now, accept all connections (behind cluster network)

    await manager.connect(websocket, user_id)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "message": "Real-time updates active"
        })

        # Keep connection alive and handle client messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/pong for keep-alive
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            elif data == "status":
                await websocket.send_json({
                    "type": "status",
                    "connections": manager.get_connection_count(user_id),
                    "total_users": len(manager.get_connected_users())
                })

    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
        logger.info(f"Client disconnected: user={user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        await manager.disconnect(websocket, user_id)


@app.post("/events/task-updates")
async def handle_task_update_event(request: Request):
    """
    Handle task update events from Dapr Pub/Sub.

    Broadcasts real-time updates to connected WebSocket clients
    for the affected user.

    CloudEvents format expected with:
    - user_id: Target user
    - event_type: Type of change
    - payload: Task data
    """
    try:
        body = await request.json()
        user_id = body.get("user_id")
        event_type = body.get("event_type")

        if not user_id:
            logger.warning("Task update event missing user_id")
            return {"status": "ignored", "reason": "no user_id"}

        # Check if user is connected
        if not manager.is_user_connected(user_id):
            logger.debug(f"User {user_id} not connected, skipping broadcast")
            return {"status": "skipped", "reason": "user not connected"}

        # Build WebSocket message
        ws_message = {
            "type": f"task.{event_type}" if event_type else "task.updated",
            "task_id": body.get("task_id"),
            "payload": body.get("payload", {}),
            "timestamp": body.get("timestamp")
        }

        # Send to user's connections
        sent = await manager.send_to_user(user_id, ws_message)
        logger.info(f"Broadcast task.{event_type} to user {user_id}: {sent} connections")

        return {"status": "broadcast", "sent_to": sent}

    except Exception as e:
        logger.error(f"Error handling task update event: {e}", exc_info=True)
        return {"status": "error", "reason": str(e)}


@app.post("/notify")
async def push_notification(request: Request):
    """
    Push notification to a specific user via WebSocket.

    Used by notification-service via Dapr service invocation.

    Expected body:
    - user_id: Target user
    - type: Notification type
    - title: Notification title
    - body: Notification body
    - metadata: Additional data
    """
    try:
        body = await request.json()
        user_id = body.get("user_id")

        if not user_id:
            return {"status": "error", "reason": "no user_id"}

        if not manager.is_user_connected(user_id):
            return {"status": "skipped", "reason": "user not connected"}

        ws_message = {
            "type": "notification",
            "notification_type": body.get("type"),
            "title": body.get("title"),
            "body": body.get("body"),
            "metadata": body.get("metadata", {})
        }

        sent = await manager.send_to_user(user_id, ws_message)
        return {"status": "sent", "connections": sent}

    except Exception as e:
        logger.error(f"Error pushing notification: {e}")
        return {"status": "error", "reason": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "websocket-service",
        "active_connections": manager.get_connection_count(),
        "connected_users": len(manager.get_connected_users())
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check."""
    return {"status": "ready", "service": "websocket-service"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)
