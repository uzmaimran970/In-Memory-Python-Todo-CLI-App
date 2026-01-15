# API Route Handlers

try:
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
except ImportError as e:
    # Fallback for environments where relative imports might not work as expected
    import importlib
    import os
    import sys

    # Add the current directory to the path if needed
    current_dir = os.path.dirname(__file__)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Import using importlib as a fallback
    tasks = importlib.import_module('.tasks', package=__name__)
    auth = importlib.import_module('.auth', package=__name__)
    mcp = importlib.import_module('.mcp', package=__name__)
    chat = importlib.import_module('.chat', package=__name__)

    # Get the routers from the imported modules
    tasks_router = tasks.router
    auth_router = auth.router
    mcp_router = mcp.router
    chat_router = chat.router

# Define what gets imported with "from . import *"
__all__ = ["tasks", "auth", "mcp", "chat", "tasks_router", "auth_router", "mcp_router", "chat_router"]
