"""
WebSocket Connection Manager (T046)

Manages active WebSocket connections per user.
Handles connection lifecycle, broadcasting, and cleanup.
"""
import logging
import json
from typing import Dict, List, Any
from fastapi import WebSocket
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections grouped by user_id.

    Supports multiple connections per user (multiple tabs/devices).
    Thread-safe for concurrent access.
    """

    def __init__(self):
        # user_id -> list of WebSocket connections
        self._connections: Dict[str, List[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket instance
            user_id: User ID for routing messages
        """
        await websocket.accept()

        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = []
            self._connections[user_id].append(websocket)

        logger.info(f"WebSocket connected: user={user_id}, total_connections={self.get_connection_count(user_id)}")

    async def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket instance to remove
            user_id: User ID
        """
        async with self._lock:
            if user_id in self._connections:
                if websocket in self._connections[user_id]:
                    self._connections[user_id].remove(websocket)
                if not self._connections[user_id]:
                    del self._connections[user_id]

        logger.info(f"WebSocket disconnected: user={user_id}, remaining={self.get_connection_count(user_id)}")

    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> int:
        """
        Send a message to all connections for a specific user.

        Args:
            user_id: Target user ID
            message: Message dict to send as JSON

        Returns:
            Number of connections message was sent to
        """
        sent = 0
        dead_connections = []

        async with self._lock:
            connections = self._connections.get(user_id, []).copy()

        for ws in connections:
            try:
                await ws.send_json(message)
                sent += 1
            except Exception as e:
                logger.warning(f"Failed to send to user {user_id}: {e}")
                dead_connections.append(ws)

        # Clean up dead connections
        if dead_connections:
            async with self._lock:
                for ws in dead_connections:
                    if user_id in self._connections and ws in self._connections[user_id]:
                        self._connections[user_id].remove(ws)

        return sent

    async def broadcast(self, message: Dict[str, Any], exclude_user: str = None) -> int:
        """
        Broadcast a message to all connected users.

        Args:
            message: Message dict to send as JSON
            exclude_user: Optional user to exclude from broadcast

        Returns:
            Total number of connections message was sent to
        """
        total_sent = 0

        async with self._lock:
            user_ids = list(self._connections.keys())

        for user_id in user_ids:
            if user_id == exclude_user:
                continue
            sent = await self.send_to_user(user_id, message)
            total_sent += sent

        return total_sent

    def get_connection_count(self, user_id: str = None) -> int:
        """
        Get number of active connections.

        Args:
            user_id: If specified, count for this user only

        Returns:
            Connection count
        """
        if user_id:
            return len(self._connections.get(user_id, []))
        return sum(len(conns) for conns in self._connections.values())

    def get_connected_users(self) -> List[str]:
        """Get list of connected user IDs."""
        return list(self._connections.keys())

    def is_user_connected(self, user_id: str) -> bool:
        """Check if a user has any active connections."""
        return user_id in self._connections and len(self._connections[user_id]) > 0


# Singleton instance
manager = ConnectionManager()
