# API Route Handlers
from . import tasks, auth, mcp, chat

# Export the routers
from .tasks import router as tasks_router
from .auth import router as auth_router
from .mcp import router as mcp_router
from .chat import router as chat_router

__all__ = ["tasks", "auth", "mcp", "chat", "tasks_router", "auth_router", "mcp_router", "chat_router"]
