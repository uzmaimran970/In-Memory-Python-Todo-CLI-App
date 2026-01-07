# Task CRUD Operations Specification - FastAPI Backend

**Feature**: Task Create, Read, Update, Delete Operations
**Created**: 2026-01-05
**Status**: Specification
**Dependencies**: [authentication.md](authentication.md), [schema.md](../database/schema.md), [rest-endpoints.md](../api/rest-endpoints.md)

## Overview

This specification defines the internal implementation of all Task CRUD operations in the FastAPI backend. Each operation includes user stories, detailed acceptance criteria, SQLModel query examples, validation logic, error handling, and security enforcement.

**Core Principles**:
- Every operation requires authenticated user from JWT
- User isolation enforced at database query level
- Ownership verified before read/update/delete operations
- Pydantic validates all inputs
- Proper error handling with appropriate HTTP status codes

---

## User Stories

### US-1: Create Task
**As a** registered user
**I want to** create a new task with a title and optional description
**So that** I can track my todo items

**Acceptance Criteria**:
- User must be authenticated (valid JWT token)
- Title is required (1-200 characters)
- Description is optional (max 1000 characters)
- Task is created with my user_id from JWT
- Task defaults to incomplete status
- Created task is returned with auto-generated ID
- Timestamps (created_at, updated_at) are set automatically

---

### US-2: List My Tasks
**As a** registered user
**I want to** view all my tasks with filtering and sorting options
**So that** I can see my pending work, completed tasks, or all tasks in my preferred order

**Acceptance Criteria**:
- User must be authenticated (valid JWT token)
- Only my tasks are returned (filtered by my user_id)
- I can filter by status: all (default), pending, completed
- I can sort by: created (default, newest first), title (alphabetical), updated (most recently updated first)
- Empty array returned when I have no tasks
- Total count of tasks is included in response

---

### US-3: View Single Task Details
**As a** registered user
**I want to** view the details of a specific task
**So that** I can see all information about that task

**Acceptance Criteria**:
- User must be authenticated (valid JWT token)
- Task must exist in database (404 if not)
- Task must belong to me (403 if owned by another user)
- Full task details returned including timestamps

---

### US-4: Update Task
**As a** registered user
**I want to** update the title and/or description of my task
**So that** I can correct mistakes or add more detail

**Acceptance Criteria**:
- User must be authenticated (valid JWT token)
- Task must exist in database (404 if not)
- Task must belong to me (403 if owned by another user)
- Title is required (1-200 characters)
- Description is optional (max 1000 characters)
- updated_at timestamp is refreshed
- created_at timestamp remains unchanged
- Completed status is NOT modified (use toggle endpoint)

---

### US-5: Delete Task
**As a** registered user
**I want to** delete a task I no longer need
**So that** my task list stays clean and relevant

**Acceptance Criteria**:
- User must be authenticated (valid JWT token)
- Task must exist in database (404 if not)
- Task must belong to me (403 if owned by another user)
- Task is permanently removed from database
- Success message returned with deleted task ID
- Subsequent attempts to access deleted task return 404

---

### US-6: Toggle Task Completion
**As a** registered user
**I want to** mark a task as complete or incomplete
**So that** I can track which tasks are done

**Acceptance Criteria**:
- User must be authenticated (valid JWT token)
- Task must exist in database (404 if not)
- Task must belong to me (403 if owned by another user)
- Completed status toggles: false → true or true → false
- updated_at timestamp is refreshed
- Title and description remain unchanged
- Operation is idempotent (can toggle multiple times)

---

## Implementation Details

### 1. Create Task Operation

#### Flow Diagram
```
1. Extract JWT token from Authorization header → get_current_user_id()
2. Validate request body with Pydantic (TaskCreate model)
3. Create Task instance with user_id from JWT
4. Insert into database (SQLModel session.add())
5. Commit transaction and refresh to get auto-generated ID
6. Return TaskResponse with 201 Created
```

#### SQLModel Implementation

```python
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from app.models import Task
from app.schemas import TaskCreate, TaskResponse
from app.auth import get_current_user_id
from app.database import get_session

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

    Validation:
    - Pydantic validates title (1-200 chars) and description (max 1000 chars)

    Returns:
    - 201 Created with new task object
    - 400 Bad Request for validation errors
    - 401 Unauthorized for invalid/missing JWT
    """
    # Create new task instance
    new_task = Task(
        user_id=current_user_id,  # Security: From JWT, not request
        title=task_data.title,
        description=task_data.description,
        completed=False,  # New tasks default to incomplete
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Insert into database
    session.add(new_task)
    session.commit()
    session.refresh(new_task)  # Get auto-generated ID and defaults

    return TaskResponse.model_validate(new_task)
```

#### Pydantic Validation Model

```python
from pydantic import BaseModel, Field
from typing import Optional

class TaskCreate(BaseModel):
    """
    Request schema for creating a new task.

    Validation Rules:
    - title: Required, 1-200 characters (whitespace-only strings rejected)
    - description: Optional, max 1000 characters
    """
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title",
        examples=["Complete backend API implementation"]
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional task description",
        examples=["Implement all CRUD endpoints with FastAPI and SQLModel"]
    )

    # Pydantic v2 config
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Write unit tests",
                    "description": "Test all CRUD operations with pytest"
                }
            ]
        }
    }
```

#### Error Cases

**400 Bad Request - Missing Title**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

**400 Bad Request - Title Too Long**
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "title"],
      "msg": "String should have at most 200 characters",
      "input": "very long title...",
      "ctx": {"max_length": 200}
    }
  ]
}
```

**401 Unauthorized - Invalid JWT**
```json
{
  "detail": "Invalid authentication credentials"
}
```

#### Example Request/Response

**Request**:
```http
POST /api/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Complete backend API",
  "description": "Implement all REST endpoints with FastAPI"
}
```

**Response (201 Created)**:
```json
{
  "id": 42,
  "user_id": "user_2mK8jX9pL3nQ5vR",
  "title": "Complete backend API",
  "description": "Implement all REST endpoints with FastAPI",
  "is_completed": false,
  "created_at": "2026-01-05T14:30:00.123456Z",
  "updated_at": "2026-01-05T14:30:00.123456Z"
}
```

---

### 2. List Tasks Operation

#### Flow Diagram
```
1. Extract JWT token → get_current_user_id()
2. Parse and validate query parameters (status, sort)
3. Build SQLModel query: SELECT * FROM tasks WHERE user_id = current_user_id
4. Apply status filter (if status != "all")
5. Apply sorting (order_by)
6. Execute query and fetch all results
7. Return TaskListResponse with tasks array and metadata
```

#### SQLModel Implementation

```python
from typing import Literal
from fastapi import Query

@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    status: Literal["all", "pending", "completed"] = Query(
        default="all",
        description="Filter by completion status"
    ),
    sort: Literal["created", "title", "updated"] = Query(
        default="created",
        description="Sort order"
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

    Query Parameters:
    - status: "all" (default) | "pending" | "completed"
    - sort: "created" (default, newest first) | "title" (A-Z) | "updated" (most recent)

    Returns:
    - 200 OK with tasks array, total count, and applied filters
    - 400 Bad Request for invalid query parameters
    - 401 Unauthorized for invalid/missing JWT
    """
    # Base query: SELECT * FROM tasks WHERE user_id = current_user_id
    query = select(Task).where(Task.user_id == current_user_id)

    # Apply status filter
    if status == "pending":
        # Uses idx_tasks_user_completed composite index
        query = query.where(Task.completed == False)
    elif status == "completed":
        # Uses idx_tasks_user_completed composite index
        query = query.where(Task.completed == True)
    # status == "all": no additional filter

    # Apply sorting
    if sort == "created":
        # Newest first - uses idx_tasks_created_at
        query = query.order_by(Task.created_at.desc())
    elif sort == "title":
        # Alphabetical A-Z
        query = query.order_by(Task.title.asc())
    elif sort == "updated":
        # Most recently updated first
        query = query.order_by(Task.updated_at.desc())

    # Execute query
    tasks = session.exec(query).all()

    # Build response
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
        status_filter=status,
        sort_by=sort
    )
```

#### Query Examples

**All tasks for user (newest first)**:
```sql
SELECT * FROM tasks
WHERE user_id = 'user_2mK8jX9pL3nQ5vR'
ORDER BY created_at DESC;

-- Uses indexes: idx_tasks_user_id, idx_tasks_created_at
```

**Pending tasks for user (newest first)**:
```sql
SELECT * FROM tasks
WHERE user_id = 'user_2mK8jX9pL3nQ5vR' AND completed = false
ORDER BY created_at DESC;

-- Uses index: idx_tasks_user_completed (composite)
```

**Completed tasks for user (alphabetical)**:
```sql
SELECT * FROM tasks
WHERE user_id = 'user_2mK8jX9pL3nQ5vR' AND completed = true
ORDER BY title ASC;

-- Uses index: idx_tasks_user_completed for WHERE, then sorts
```

#### Response Models

```python
from pydantic import BaseModel
from datetime import datetime

class TaskResponse(BaseModel):
    """Response schema for a single task."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    is_completed: bool = Field(alias="completed")
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,  # Enable ORM mode
        "populate_by_name": True  # Allow both 'completed' and 'is_completed'
    }

class TaskListResponse(BaseModel):
    """Response schema for task list with metadata."""
    tasks: list[TaskResponse]
    total: int
    status_filter: str
    sort_by: str
```

#### Example Request/Response

**Request - Get all pending tasks sorted by title**:
```http
GET /api/tasks?status=pending&sort=title HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "user_2mK8jX9pL3nQ5vR",
      "title": "Complete backend API",
      "description": "Implement all REST endpoints",
      "is_completed": false,
      "created_at": "2026-01-05T10:00:00Z",
      "updated_at": "2026-01-05T10:00:00Z"
    },
    {
      "id": 3,
      "user_id": "user_2mK8jX9pL3nQ5vR",
      "title": "Write unit tests",
      "description": null,
      "is_completed": false,
      "created_at": "2026-01-05T11:00:00Z",
      "updated_at": "2026-01-05T11:00:00Z"
    }
  ],
  "total": 2,
  "status_filter": "pending",
  "sort_by": "title"
}
```

**Response - Empty task list (200 OK)**:
```json
{
  "tasks": [],
  "total": 0,
  "status_filter": "all",
  "sort_by": "created"
}
```

---

### 3. Get Single Task Operation

#### Flow Diagram
```
1. Extract JWT token → get_current_user_id()
2. Parse task_id from path parameter
3. Query database: SELECT * FROM tasks WHERE id = task_id
4. Check if task exists (404 if not)
5. Verify ownership: task.user_id == current_user_id (403 if not)
6. Return TaskResponse with 200 OK
```

#### SQLModel Implementation

```python
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
    - Returns 403 if task owned by different user (not 404 to avoid info leakage)

    Returns:
    - 200 OK with task details
    - 404 Not Found if task doesn't exist
    - 403 Forbidden if task belongs to another user
    - 401 Unauthorized for invalid/missing JWT
    """
    # Query by ID - uses primary key index
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
```

#### Alternative Implementation (Single Query)

```python
# More efficient: Single query with WHERE clauses
@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_single_query(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Get single task with ownership filter in query.

    Note: This approach returns 404 for both "doesn't exist" and "owned by other user"
    which is more secure (doesn't leak task existence) but less clear for debugging.
    """
    query = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id
    )
    task = session.exec(query).first()

    if not task:
        # Could be: task doesn't exist OR user doesn't own it
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse.model_validate(task)
```

#### Error Cases

**404 Not Found - Task Doesn't Exist**:
```json
{
  "detail": "Task not found"
}
```

**403 Forbidden - Task Owned by Another User**:
```json
{
  "detail": "Not authorized to access this task"
}
```

#### Security Note: 403 vs 404

**Preferred Approach** (first implementation):
- Return 404 when task doesn't exist
- Return 403 when task exists but user doesn't own it
- **Advantage**: Clear error messages for debugging
- **Disadvantage**: Leaks task existence (user can enumerate IDs)

**Alternative Approach** (second implementation):
- Return 404 for both cases
- **Advantage**: Doesn't leak task existence
- **Disadvantage**: Less clear error messages

**Recommendation**: Use first approach (403 vs 404) since:
- User isolation already enforced at query level
- Better developer experience
- Auto-incrementing IDs are already guessable

---

### 4. Update Task Operation

#### Flow Diagram
```
1. Extract JWT token → get_current_user_id()
2. Parse task_id from path parameter
3. Validate request body with Pydantic (TaskUpdate model)
4. Query database: SELECT * FROM tasks WHERE id = task_id
5. Check if task exists (404 if not)
6. Verify ownership: task.user_id == current_user_id (403 if not)
7. Update fields: title, description, updated_at
8. Commit transaction and refresh
9. Return updated TaskResponse with 200 OK
```

#### SQLModel Implementation

```python
class TaskUpdate(BaseModel):
    """
    Request schema for updating a task.

    Validation Rules:
    - title: Required, 1-200 characters
    - description: Optional, max 1000 characters

    Note: completed status is NOT updated here (use PATCH /complete endpoint)
    """
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

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

    Returns:
    - 200 OK with updated task
    - 404 Not Found if task doesn't exist
    - 403 Forbidden if task belongs to another user
    - 400 Bad Request for validation errors
    - 401 Unauthorized for invalid/missing JWT
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

    # Update fields
    task.title = task_data.title
    task.description = task_data.description
    task.updated_at = datetime.utcnow()

    # Commit changes
    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)
```

#### Fields That Cannot Be Updated

```python
# ❌ WRONG: Never allow user_id to be changed
task.user_id = task_data.user_id  # Security violation!

# ❌ WRONG: Don't change created_at (immutable timestamp)
task.created_at = datetime.utcnow()

# ❌ WRONG: Don't update completed here (use PATCH /complete)
task.completed = task_data.completed

# ✅ CORRECT: Only update title, description, and updated_at
task.title = task_data.title
task.description = task_data.description
task.updated_at = datetime.utcnow()
```

#### Example Request/Response

**Request**:
```http
PUT /api/tasks/42 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Complete backend API implementation",
  "description": "Implement all REST endpoints with FastAPI and SQLModel"
}
```

**Response (200 OK)**:
```json
{
  "id": 42,
  "user_id": "user_2mK8jX9pL3nQ5vR",
  "title": "Complete backend API implementation",
  "description": "Implement all REST endpoints with FastAPI and SQLModel",
  "is_completed": false,
  "created_at": "2026-01-05T10:00:00Z",
  "updated_at": "2026-01-05T15:30:00Z"
}
```

**Note**: `created_at` remains unchanged, `updated_at` is refreshed

---

### 5. Delete Task Operation

#### Flow Diagram
```
1. Extract JWT token → get_current_user_id()
2. Parse task_id from path parameter
3. Query database: SELECT * FROM tasks WHERE id = task_id
4. Check if task exists (404 if not)
5. Verify ownership: task.user_id == current_user_id (403 if not)
6. Delete task from database
7. Commit transaction
8. Return success message with 200 OK
```

#### SQLModel Implementation

```python
class DeleteResponse(BaseModel):
    """Response schema for delete operations."""
    message: str
    deleted_task_id: int

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

    Returns:
    - 200 OK with success message and deleted task ID
    - 404 Not Found if task doesn't exist
    - 403 Forbidden if task belongs to another user
    - 401 Unauthorized for invalid/missing JWT
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

    # Delete from database
    session.delete(task)
    session.commit()

    return DeleteResponse(
        message="Task deleted successfully",
        deleted_task_id=task_id
    )
```

#### Example Request/Response

**Request**:
```http
DELETE /api/tasks/42 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK)**:
```json
{
  "message": "Task deleted successfully",
  "deleted_task_id": 42
}
```

**Subsequent GET Returns 404**:
```http
GET /api/tasks/42 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

HTTP/1.1 404 Not Found
{
  "detail": "Task not found"
}
```

---

### 6. Toggle Task Completion Operation

#### Flow Diagram
```
1. Extract JWT token → get_current_user_id()
2. Parse task_id from path parameter
3. Query database: SELECT * FROM tasks WHERE id = task_id
4. Check if task exists (404 if not)
5. Verify ownership: task.user_id == current_user_id (403 if not)
6. Toggle completed: task.completed = NOT task.completed
7. Update updated_at timestamp
8. Commit transaction and refresh
9. Return updated TaskResponse with 200 OK
```

#### SQLModel Implementation

```python
@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: int,
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

    Returns:
    - 200 OK with updated task (new completed status)
    - 404 Not Found if task doesn't exist
    - 403 Forbidden if task belongs to another user
    - 401 Unauthorized for invalid/missing JWT
    """
    # Query by ID
    task = session.get(Task, task_id)

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

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    # Commit changes
    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)
```

#### Idempotency Examples

**First PATCH - Mark as Complete**:
```http
PATCH /api/tasks/42/complete HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "id": 42,
  "is_completed": true,  // Was false, now true
  "updated_at": "2026-01-05T16:00:00Z"
}
```

**Second PATCH - Mark as Incomplete**:
```http
PATCH /api/tasks/42/complete HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "id": 42,
  "is_completed": false,  // Was true, now false
  "updated_at": "2026-01-05T16:05:00Z"
}
```

**Third PATCH - Mark as Complete Again**:
```http
PATCH /api/tasks/42/complete HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "id": 42,
  "is_completed": true,  // Was false, now true
  "updated_at": "2026-01-05T16:10:00Z"
}
```

---

## Security Enforcement

### User Isolation Pattern

**Every operation MUST enforce user isolation:**

```python
# ✅ CORRECT: User ID from JWT
current_user_id = Depends(get_current_user_id)

# ✅ CORRECT: Filter by authenticated user
query = select(Task).where(Task.user_id == current_user_id)

# ✅ CORRECT: Verify ownership before operation
if task.user_id != current_user_id:
    raise HTTPException(status_code=403, detail="Not authorized")

# ❌ WRONG: Never trust user_id from request
user_id = request_data.get("user_id")  # NEVER DO THIS

# ❌ WRONG: Never allow user to query arbitrary user_id
query = select(Task).where(Task.user_id == user_id_from_request)
```

### Ownership Verification Checklist

All operations that access specific tasks MUST verify ownership:

- [X] **Create**: Set `user_id` from JWT (no verification needed, creating for self)
- [X] **List**: Filter by `user_id` from JWT (no per-task verification needed)
- [X] **Get**: Verify `task.user_id == current_user_id` before returning
- [X] **Update**: Verify `task.user_id == current_user_id` before updating
- [X] **Delete**: Verify `task.user_id == current_user_id` before deleting
- [X] **Toggle**: Verify `task.user_id == current_user_id` before toggling

### Error Response Security

**Never leak sensitive information:**

```python
# ✅ CORRECT: Generic error messages
raise HTTPException(status_code=404, detail="Task not found")
raise HTTPException(status_code=403, detail="Not authorized to access this task")

# ❌ WRONG: Leaks user information
raise HTTPException(
    status_code=403,
    detail=f"Task belongs to user {task.user_id}, not you"
)

# ❌ WRONG: Exposes internal details
raise HTTPException(
    status_code=500,
    detail=f"Database error: {str(exception)}"
)
```

---

## Performance Optimization

### Index Usage

```sql
-- Index: idx_tasks_user_id (single column)
-- Used by: All queries (WHERE user_id = ?)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Index: idx_tasks_completed (single column)
-- Used by: Status filtering (WHERE completed = true/false)
CREATE INDEX idx_tasks_completed ON tasks(completed);

-- Index: idx_tasks_user_completed (composite)
-- Used by: Filtered queries (WHERE user_id = ? AND completed = ?)
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);

-- Index: idx_tasks_created_at (single column)
-- Used by: Sorting (ORDER BY created_at DESC)
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

### Query Performance Examples

**List all pending tasks for user (sorted by created)**:
```sql
SELECT * FROM tasks
WHERE user_id = 'user_123' AND completed = false
ORDER BY created_at DESC;

-- Index usage: idx_tasks_user_completed (WHERE clause)
--              idx_tasks_created_at (ORDER BY clause)
-- Performance: O(log n) index lookup + O(k log k) sort where k = result count
```

**Create new task**:
```sql
INSERT INTO tasks (user_id, title, description, completed, created_at, updated_at)
VALUES ('user_123', 'New task', 'Description', false, NOW(), NOW());

-- Index updates: All indexes updated automatically
-- Performance: O(log n) per index (4 indexes total)
```

### Connection Pooling

```python
# Database configuration (db.py)
from sqlmodel import create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL")  # Neon PostgreSQL with pooler

# Engine with connection pool
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging in development
    pool_size=5,  # Max 5 connections in pool
    max_overflow=10,  # Max 10 additional connections if pool exhausted
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600  # Recycle connections after 1 hour
)

def get_session():
    """Dependency for database sessions."""
    with Session(engine) as session:
        yield session
```

---

## Error Handling Summary

### HTTP Status Code Matrix

| Operation | Success | Not Found | Wrong User | Validation Error | Auth Error |
|-----------|---------|-----------|------------|------------------|------------|
| Create    | 201     | -         | -          | 400              | 401        |
| List      | 200     | -         | -          | 400 (bad params) | 401        |
| Get       | 200     | 404       | 403        | -                | 401        |
| Update    | 200     | 404       | 403        | 400              | 401        |
| Delete    | 200     | 404       | 403        | -                | 401        |
| Toggle    | 200     | 404       | 403        | -                | 401        |

### Error Response Examples

**400 Bad Request - Pydantic Validation**:
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "title"],
      "msg": "String should have at most 200 characters",
      "input": "very long title...",
      "ctx": {"max_length": 200}
    }
  ]
}
```

**401 Unauthorized - Invalid JWT**:
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden - Ownership Violation**:
```json
{
  "detail": "Not authorized to access this task"
}
```

**404 Not Found - Task Doesn't Exist**:
```json
{
  "detail": "Task not found"
}
```

---

## Testing Strategy

### Unit Tests for Each Operation

```python
import pytest
from fastapi.testclient import TestClient

def test_create_task_success(client: TestClient, auth_headers: dict):
    """Test creating a task with valid data."""
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Test task", "description": "Test description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["is_completed"] is False
    assert "id" in data

def test_create_task_missing_title(client: TestClient, auth_headers: dict):
    """Test creating a task without title fails with 400."""
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"description": "No title"}
    )
    assert response.status_code == 400

def test_list_tasks_filters_by_user(
    client: TestClient,
    auth_headers_user1: dict,
    auth_headers_user2: dict
):
    """Test that users only see their own tasks."""
    # User 1 creates task
    client.post(
        "/api/tasks",
        headers=auth_headers_user1,
        json={"title": "User 1 task"}
    )

    # User 2 creates task
    client.post(
        "/api/tasks",
        headers=auth_headers_user2,
        json={"title": "User 2 task"}
    )

    # User 1 lists tasks - should only see their own
    response = client.get("/api/tasks", headers=auth_headers_user1)
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "User 1 task"

def test_get_task_ownership_violation(
    client: TestClient,
    auth_headers_user1: dict,
    auth_headers_user2: dict
):
    """Test that users cannot access other users' tasks."""
    # User 1 creates task
    response = client.post(
        "/api/tasks",
        headers=auth_headers_user1,
        json={"title": "User 1 task"}
    )
    task_id = response.json()["id"]

    # User 2 tries to access User 1's task
    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers_user2)
    assert response.status_code == 403

def test_update_task_success(client: TestClient, auth_headers: dict):
    """Test updating a task with valid data."""
    # Create task
    create_response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Original title"}
    )
    task_id = create_response.json()["id"]

    # Update task
    update_response = client.put(
        f"/api/tasks/{task_id}",
        headers=auth_headers,
        json={"title": "Updated title", "description": "New description"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated title"
    assert data["description"] == "New description"

def test_delete_task_success(client: TestClient, auth_headers: dict):
    """Test deleting a task."""
    # Create task
    create_response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "To be deleted"}
    )
    task_id = create_response.json()["id"]

    # Delete task
    delete_response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted_task_id"] == task_id

    # Verify task is gone
    get_response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_toggle_completion_idempotent(client: TestClient, auth_headers: dict):
    """Test toggling completion status multiple times."""
    # Create task
    create_response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Toggle test"}
    )
    task_id = create_response.json()["id"]

    # First toggle: false → true
    response1 = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert response1.json()["is_completed"] is True

    # Second toggle: true → false
    response2 = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert response2.json()["is_completed"] is False

    # Third toggle: false → true
    response3 = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert response3.json()["is_completed"] is True
```

---

## Acceptance Criteria

### Create Task
- ✅ Creates task with user_id from JWT (never from request body)
- ✅ Title is required and validated (1-200 characters)
- ✅ Description is optional and validated (max 1000 characters)
- ✅ New tasks default to completed=false
- ✅ Timestamps created_at and updated_at set to current UTC time
- ✅ Returns 201 Created with task object including auto-generated ID
- ✅ Returns 401 for missing/invalid JWT
- ✅ Returns 400 for validation errors

### List Tasks
- ✅ Returns only authenticated user's tasks (filtered by user_id from JWT)
- ✅ status=all returns both pending and completed tasks
- ✅ status=pending returns only tasks where completed=false
- ✅ status=completed returns only tasks where completed=true
- ✅ sort=created orders by created_at descending (newest first)
- ✅ sort=title orders alphabetically by title ascending
- ✅ sort=updated orders by updated_at descending
- ✅ Returns empty array when user has no tasks
- ✅ Response includes total count of returned tasks
- ✅ Returns 401 for missing/invalid JWT
- ✅ Returns 400 for invalid query parameters

### Get Single Task
- ✅ Returns task when owned by authenticated user
- ✅ Returns 404 when task doesn't exist
- ✅ Returns 403 when task exists but owned by different user
- ✅ Returns 401 for missing/invalid JWT
- ✅ Ownership verified before returning task data

### Update Task
- ✅ Updates task when owned by authenticated user
- ✅ Title and description validated (same rules as create)
- ✅ updated_at timestamp refreshed to current UTC time
- ✅ created_at timestamp remains unchanged
- ✅ completed status NOT modified (use toggle endpoint)
- ✅ user_id cannot be changed (immutable)
- ✅ Returns 404 when task doesn't exist
- ✅ Returns 403 when task exists but owned by different user
- ✅ Returns 401 for missing/invalid JWT
- ✅ Returns 400 for validation errors

### Delete Task
- ✅ Deletes task when owned by authenticated user
- ✅ Task permanently removed from database
- ✅ Returns success message with deleted task ID
- ✅ Subsequent GET requests return 404
- ✅ Returns 404 when task doesn't exist
- ✅ Returns 403 when task exists but owned by different user
- ✅ Returns 401 for missing/invalid JWT

### Toggle Completion
- ✅ Toggles completed: false → true when currently incomplete
- ✅ Toggles completed: true → false when currently complete
- ✅ updated_at timestamp refreshed to current UTC time
- ✅ Title and description remain unchanged
- ✅ Idempotent: Can toggle multiple times back and forth
- ✅ Returns 404 when task doesn't exist
- ✅ Returns 403 when task exists but owned by different user
- ✅ Returns 401 for missing/invalid JWT

### Security
- ✅ All operations require valid JWT authentication
- ✅ All operations enforce user isolation (users can only access their own tasks)
- ✅ Ownership verified before read/update/delete operations
- ✅ user_id always extracted from JWT, never from request body/params
- ✅ No sensitive information in error responses
- ✅ Proper HTTP status codes: 200/201 (success), 400 (validation), 401 (auth), 403 (forbidden), 404 (not found)

### Performance
- ✅ Indexes used for WHERE clauses (user_id, completed)
- ✅ Indexes used for ORDER BY clauses (created_at)
- ✅ Connection pooling configured for Neon PostgreSQL
- ✅ Queries are efficient (no N+1 problems, no full table scans)

---

## Implementation Checklist

- [ ] Create SQLModel Task model in `app/models.py`
- [ ] Create Pydantic schemas in `app/schemas.py` (TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, DeleteResponse)
- [ ] Create database session dependency in `app/database.py`
- [ ] Create authentication dependencies in `app/auth.py` (get_current_user_id)
- [ ] Create task router in `app/routers/tasks.py`
- [ ] Implement POST /api/tasks (create)
- [ ] Implement GET /api/tasks (list with filters)
- [ ] Implement GET /api/tasks/{id} (get single)
- [ ] Implement PUT /api/tasks/{id} (update)
- [ ] Implement DELETE /api/tasks/{id} (delete)
- [ ] Implement PATCH /api/tasks/{id}/complete (toggle)
- [ ] Add ownership verification to all single-task operations
- [ ] Configure database connection pooling
- [ ] Write unit tests for each endpoint (success cases)
- [ ] Write unit tests for error cases (400, 401, 403, 404)
- [ ] Write integration tests for complete workflows
- [ ] Test user isolation with multiple test users
- [ ] Verify index usage with EXPLAIN ANALYZE
- [ ] Test validation rules for title/description
- [ ] Test idempotency of toggle endpoint
- [ ] Load test with realistic user scenarios

---

**Status**: Specification Complete
**Next Steps**: Run `/sp.plan` to generate implementation plan for backend
