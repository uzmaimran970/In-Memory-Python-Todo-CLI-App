"""Task CRUD API endpoints."""
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from datetime import datetime
from typing import Literal
import httpx

from app.database import get_session
from app.auth import get_current_user_id
from app.models import Task, TaskPriority
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    DeleteResponse
)
from app.services.event_publisher import (
    publish_task_created,
    publish_task_updated,
    publish_task_deleted,
    publish_task_completed
)

logger = logging.getLogger(__name__)

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["tasks"])


@router.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    Security:
    - user_id is ALWAYS set from JWT (current_user_id)
    - Never accept user_id from request body

    Args:
        task_data: Task title and optional description
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        TaskResponse: Created task with auto-generated ID

    Raises:
        400: Validation error (title too long, etc.)
        401: Missing or invalid JWT token
    """
    # Validate priority
    priority = TaskPriority.MEDIUM
    if task_data.priority:
        try:
            priority = TaskPriority(task_data.priority)
        except ValueError:
            priority = TaskPriority.MEDIUM

    # Create new task with authenticated user_id
    new_task = Task(
        user_id=current_user_id,  # Security: From JWT, never from request
        title=task_data.title,
        description=task_data.description,
        completed=False,  # New tasks default to incomplete
        priority=priority,
        tags=task_data.tags or [],
        due_date=task_data.due_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Insert into database
    session.add(new_task)
    session.commit()
    session.refresh(new_task)  # Get auto-generated ID

    # Publish task created event (T026: Dapr Pub/Sub integration)
    try:
        await publish_task_created(
            task_id=new_task.id,
            user_id=current_user_id,
            task_data={
                "id": new_task.id,
                "title": new_task.title,
                "description": new_task.description,
                "completed": new_task.completed,
                "created_at": new_task.created_at.isoformat(),
                "updated_at": new_task.updated_at.isoformat()
            }
        )
    except Exception as e:
        logger.warning(f"Failed to publish task created event: {e}")

    return TaskResponse.model_validate(new_task)


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    status_filter: Literal["all", "pending", "completed"] = Query(
        default="all",
        alias="status",
        description="Filter by completion status"
    ),
    sort: Literal["created", "title", "updated", "priority", "due_date"] = Query(
        default="created",
        description="Sort order"
    ),
    priority: str = Query(
        default=None,
        description="Filter by priority (high, medium, low)"
    ),
    tag: str = Query(
        default=None,
        description="Filter by tag"
    ),
    search: str = Query(
        default=None,
        description="Search in title and description"
    ),
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskListResponse:
    """
    List all tasks for the authenticated user with filtering and sorting.

    Security:
    - Queries are ALWAYS filtered by current_user_id from JWT
    - User cannot see other users' tasks

    Performance:
    - Uses index on (user_id, completed) for filtered queries
    - Uses index on created_at for created sort

    Args:
        status_filter: "all" (default) | "pending" | "completed"
        sort: "created" (default, newest first) | "title" (A-Z) | "updated"
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        TaskListResponse: Tasks array, total count, applied filters

    Raises:
        400: Invalid query parameters
        401: Missing or invalid JWT token
    """
    # Base query: Filter by authenticated user
    query = select(Task).where(Task.user_id == current_user_id)

    # Apply status filter
    if status_filter == "pending":
        query = query.where(Task.completed == False)
    elif status_filter == "completed":
        query = query.where(Task.completed == True)
    # status_filter == "all": no additional filter

    # Apply priority filter (T068)
    if priority:
        try:
            priority_enum = TaskPriority(priority)
            query = query.where(Task.priority == priority_enum)
        except ValueError:
            pass  # Invalid priority, ignore filter

    # Apply tag filter (T068)
    if tag:
        query = query.where(Task.tags.contains([tag]))

    # Apply search filter (T068)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Task.title.ilike(search_pattern)) |
            (Task.description.ilike(search_pattern))
        )

    # Apply sorting
    if sort == "created":
        query = query.order_by(Task.created_at.desc())  # Newest first
    elif sort == "title":
        query = query.order_by(Task.title.asc())  # Alphabetical A-Z
    elif sort == "updated":
        query = query.order_by(Task.updated_at.desc())  # Most recently updated
    elif sort == "priority":
        query = query.order_by(Task.priority.asc())  # High first
    elif sort == "due_date":
        query = query.order_by(Task.due_date.asc())  # Soonest first

    # Execute query
    tasks = session.exec(query).all()

    # Build response
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
        status_filter=status_filter,
        sort_by=sort
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Get a single task by ID.

    Security:
    - Verifies task belongs to authenticated user
    - Returns 403 if task owned by different user

    Args:
        task_id: Task ID from path parameter
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        TaskResponse: Task details

    Raises:
        404: Task doesn't exist
        403: Task belongs to another user
        401: Missing or invalid JWT token
    """
    # Query by ID
    task = session.get(Task, task_id)

    # Check existence
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Security: Verify ownership BEFORE returning data
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    return TaskResponse.model_validate(task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Update task title and description.

    Security:
    - Verifies task belongs to authenticated user before updating
    - user_id cannot be changed (immutable)

    Updates:
    - title: Required, 1-200 chars
    - description: Optional, max 1000 chars
    - updated_at: Automatically set to current UTC time

    Does NOT Update:
    - completed: Use PATCH /tasks/{id}/complete endpoint
    - created_at: Immutable
    - user_id: Immutable

    Args:
        task_id: Task ID from path parameter
        task_data: Updated title and description
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        TaskResponse: Updated task

    Raises:
        404: Task doesn't exist
        403: Task belongs to another user
        400: Validation error (title too long, etc.)
        401: Missing or invalid JWT token
    """
    # Query by ID
    task = session.get(Task, task_id)

    # Check existence
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Security: Verify ownership before allowing update
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task"
        )

    # Capture before state for audit
    before_state = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }

    # Update fields
    task.title = task_data.title
    task.description = task_data.description
    if task_data.priority:
        try:
            task.priority = TaskPriority(task_data.priority)
        except ValueError:
            pass
    if task_data.tags is not None:
        task.tags = task_data.tags
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    task.updated_at = datetime.utcnow()

    # Commit changes
    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish task updated event (T026: Dapr Pub/Sub integration)
    try:
        await publish_task_updated(
            task_id=task.id,
            user_id=current_user_id,
            task_data={
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            },
            before_state=before_state
        )
    except Exception as e:
        logger.warning(f"Failed to publish task updated event: {e}")

    return TaskResponse.model_validate(task)


@router.delete("/tasks/{task_id}", response_model=DeleteResponse)
async def delete_task(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> DeleteResponse:
    """
    Delete a task permanently.

    Security:
    - Verifies task belongs to authenticated user before deletion
    - Cannot be undone

    Args:
        task_id: Task ID from path parameter
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        DeleteResponse: Success message with deleted task ID

    Raises:
        404: Task doesn't exist
        403: Task belongs to another user
        401: Missing or invalid JWT token
    """
    # Query by ID
    task = session.get(Task, task_id)

    # Check existence
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Security: Verify ownership before allowing deletion
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    # Capture task data before deletion for event
    task_data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }

    # Delete from database
    session.delete(task)
    session.commit()

    # Publish task deleted event (T026: Dapr Pub/Sub integration)
    try:
        await publish_task_deleted(
            task_id=task_id,
            user_id=current_user_id,
            task_data=task_data
        )
    except Exception as e:
        logger.warning(f"Failed to publish task deleted event: {e}")

    return DeleteResponse(
        message="Task deleted successfully",
        deleted_task_id=task_id
    )


@router.patch("/tasks/{id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Toggle task completion status (true ↔ false).

    Security:
    - Verifies task belongs to authenticated user before toggling

    Behavior:
    - false → true (mark as complete)
    - true → false (mark as incomplete)
    - Idempotent: Can be called multiple times to toggle back and forth

    Updates:
    - completed: Toggles boolean value
    - updated_at: Set to current UTC time

    Does NOT Update:
    - title, description: Unchanged
    - created_at: Immutable

    Args:
        id: Task ID from path parameter
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        TaskResponse: Updated task with new completed status

    Raises:
        404: Task doesn't exist
        403: Task belongs to another user
        401: Missing or invalid JWT token
    """
    # Query by ID
    task = session.get(Task, id)

    # Check existence
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Security: Verify ownership before allowing status change
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task"
        )

    # Capture before state for audit
    before_state = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }
    was_incomplete = not task.completed

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    # Commit changes
    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish event (T026: Dapr Pub/Sub integration)
    # Use task.completed event when marking complete (triggers recurring-service)
    # Use task.updated event when unmarking complete
    try:
        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "recurrence_id": task.recurrence_id,
            "updated_at": task.updated_at.isoformat()
        }
        if was_incomplete and task.completed:
            # Task marked as complete - triggers recurring service
            await publish_task_completed(
                task_id=task.id,
                user_id=current_user_id,
                task_data=task_data,
                before_state=before_state
            )
        else:
            # Task unmarked - just an update
            await publish_task_updated(
                task_id=task.id,
                user_id=current_user_id,
                task_data=task_data,
                before_state=before_state
            )
    except Exception as e:
        logger.warning(f"Failed to publish task completion event: {e}")

    return TaskResponse.model_validate(task)


@router.get("/tasks/{task_id}/history")
async def get_task_history(
    task_id: int,
    limit: int = Query(default=50, le=200),
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Get audit history for a task (T060).

    Retrieves the change history from the audit service
    via Dapr service invocation.

    Args:
        task_id: Task ID from path
        limit: Max entries to return (default 50, max 200)
        current_user_id: Authenticated user from JWT
        session: Database session

    Returns:
        Audit history entries for the task

    Raises:
        404: Task not found
        403: Task belongs to another user
    """
    # Verify task exists and belongs to user
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this task's history"
        )

    # Query audit service via Dapr service invocation
    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
    url = f"http://localhost:{dapr_port}/v1.0/invoke/audit-svc/method/api/audit/task/{task_id}?limit={limit}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Audit service returned {response.status_code}")
                return {"task_id": task_id, "entries": [], "total": 0}
    except Exception as e:
        logger.warning(f"Audit service unavailable: {e}")
        return {"task_id": task_id, "entries": [], "total": 0, "error": "Audit service unavailable"}

