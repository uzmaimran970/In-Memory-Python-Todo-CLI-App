"""
WebSocket Service (T045)

Microservice that manages WebSocket connections for real-time
task updates. Subscribes to task-updates topic and broadcasts
changes to connected clients.

Topics subscribed:
- task-updates: Broadcasts to connected user clients

Endpoints:
- WS /ws/{user_id}: WebSocket connection
- POST /notify: Push notification to specific user
"""
