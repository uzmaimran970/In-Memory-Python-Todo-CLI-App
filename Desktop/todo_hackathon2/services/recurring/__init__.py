"""
Recurring Tasks Service (T027)

Microservice that handles recurring task generation.
Subscribes to task-events topic and creates next occurrences
when recurring tasks are completed.

Topics subscribed:
- task-events: Listens for "completed" events

Dapr service invocation:
- backend-svc: Creates new task instances
"""
from fastapi import FastAPI
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Recurring Tasks Service",
    description="Generates next task occurrences when recurring tasks complete",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "recurring-service"}


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes probes."""
    return {"status": "ready", "service": "recurring-service"}
