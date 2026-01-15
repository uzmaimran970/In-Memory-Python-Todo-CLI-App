# API Route Handlers

# Import individual routers
from .tasks import router as tasks_router
from .auth import router as auth_router
from .mcp import router as mcp_router
from .chat import router as chat_router

# Also import the modules themselves to make them accessible
from . import tasks, auth, mcp, chat

# Make the routers available at package level
tasks = tasks
auth = auth
mcp = mcp
chat = chat

# Define what gets imported with "from . import *"
__all__ = ["tasks", "auth", "mcp", "chat", "tasks_router", "auth_router", "mcp_router", "chat_router"]
