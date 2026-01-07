# REST API Endpoints Specification - FastAPI Backend

**Feature**: REST API Endpoints for Task CRUD Operations
**Created**: 2026-01-05
**Status**: Specification
**Dependencies**: [authentication.md](../features/authentication.md), [schema.md](../database/schema.md)

## Overview

This specification defines all REST API endpoints for the FastAPI backend. All endpoints require JWT authentication and enforce user isolation through the authenticated user's ID.

**Base URL**: `/api/`
**Authentication**: All endpoints require valid JWT token in `Authorization: Bearer <token>` header
**Content-Type**: `application/json`
**Response Format**: JSON

## Authentication Requirements

All endpoints in this specification:
- MUST include `Authorization: Bearer <jwt_token>` header
- MUST validate JWT signature, expiration, audience, and issuer
- MUST extract `user_id` from JWT `sub` claim
- MUST filter all database queries by authenticated `user_id`
- MUST return 401 Unauthorized for missing/invalid/expired tokens
- MUST return 403 Forbidden when user attempts to access another user's tasks

See [authentication.md](../features/authentication.md) for JWT verification implementation.

## Endpoints

### 1. List User Tasks

**Endpoint**: `GET /api/tasks`
**Description**: Retrieve all tasks for the authenticated user with optional filtering and sorting
**Authentication**: Required

#### Query Parameters

| Parameter | Type | Default | Description | Validation |
|-----------|------|---------|-------------|------------|
| `status` | string | `all` | Filter by completion status | Enum: `all`, `pending`, `completed` |
| `sort` | string | `created` | Sort order | Enum: `created`, `title`, `updated` |

#### Request Example

```http
GET /api/tasks?status=pending&sort=created HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response (200 OK)

```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "user_2mK8jX9pL3nQ5vR",
      "title": "Complete backend API",
      "description": "Implement all REST endpoints with FastAPI",
      "is_completed": false,
      "created_at": "2026-01-05T10:30:00Z",
      "updated_at": "2026-01-05T10:30:00Z"
    },
    {
      "id": 2,
      "user_id": "user_2mK8jX9pL3nQ5vR",
      "title": "Write unit tests",
      "description": "Test all CRUD operations",
      "is_completed": false,
      "created_at": "2026-01-05T11:15:00Z",
      "updated_at": "2026-01-05T11:15:00Z"
    }
  ],
  "total": 2,
  "status_filter": "pending",
  "sort_by": "created"
}
```

#### Error Responses

**401 Unauthorized** - Missing or invalid JWT token
```json
{
  "detail": "Invalid authentication credentials"
}
```

**400 Bad Request** - Invalid query parameter
```json
{
  "detail": "Invalid status filter. Must be one of: all, pending, completed"
}
```

#### Implementation Notes

```python
from typing import Literal
from fastapi import APIRouter, Depends, Query, HTTPException

@router.get("/tasks")
async def list_tasks(
    status: Literal["all", "pending", "completed"] = Query(default="all"),
    sort: Literal["created", "title", "updated"] = Query(default="created"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session)
) -> TaskListResponse:
    """
    List all tasks for authenticated user with filtering and sorting.

    Security: Filters by current_user_id from JWT - user cannot see other users' tasks.
    """
    query = db.query(Task).filter(Task.user_id == current_user_id)

    # Apply status filter
    if status == "pending":
        query = query.filter(Task.completed == False)
    elif status == "completed":
        query = query.filter(Task.completed == True)

    # Apply sorting
    if sort == "created":
        query = query.order_by(Task.created_at.desc())
    elif sort == "title":
        query = query.order_by(Task.title.asc())
    elif sort == "updated":
        query = query.order_by(Task.updated_at.desc())

    tasks = query.all()

    return TaskListResponse(
        tasks=[TaskResponse.from_orm(task) for task in tasks],
        total=len(tasks),
        status_filter=status,
        sort_by=sort
    )
```

#### Acceptance Criteria

- ✅ Returns only tasks belonging to authenticated user (filters by `user_id` from JWT)
- ✅ `status=all` returns both pending and completed tasks
- ✅ `status=pending` returns only tasks where `completed=false`
- ✅ `status=completed` returns only tasks where `completed=true`
- ✅ `sort=created` orders by `created_at` descending (newest first)
- ✅ `sort=title` orders alphabetically by title ascending
- ✅ `sort=updated` orders by `updated_at` descending (most recently updated first)
- ✅ Returns 401 for missing/invalid JWT token
- ✅ Returns 400 for invalid query parameters
- ✅ Response includes `total` count of returned tasks
- ✅ Empty array returned when user has no tasks

---

### 2. Create New Task

**Endpoint**: `POST /api/tasks`
**Description**: Create a new task for the authenticated user
**Authentication**: Required

#### Request Body

```typescript
{
  title: string;        // Required, 1-200 characters
  description?: string; // Optional, max 1000 characters
}
```

#### Request Example

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

#### Response (201 Created)

```json
{
  "id": 1,
  "user_id": "user_2mK8jX9pL3nQ5vR",
  "title": "Complete backend API",
  "description": "Implement all REST endpoints with FastAPI",
  "is_completed": false,
  "created_at": "2026-01-05T10:30:00Z",
  "updated_at": "2026-01-05T10:30:00Z"
}
```

#### Error Responses

**401 Unauthorized** - Missing or invalid JWT token
```json
{
  "detail": "Invalid authentication credentials"
}
```

**400 Bad Request** - Validation error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**400 Bad Request** - Title too long
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at most 200 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

#### Implementation Notes

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

@router.post("/tasks", status_code=201)
async def create_task(
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    Security: Sets user_id from JWT (current_user_id) - user cannot create tasks for others.
    """
    # Create new task with authenticated user_id
    new_task = Task(
        user_id=current_user_id,  # Security: Always use JWT user_id
        title=task_data.title,
        description=task_data.description,
        completed=False  # New tasks start as incomplete
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return TaskResponse.from_orm(new_task)
```

#### Acceptance Criteria

- ✅ Creates task with authenticated `user_id` from JWT (never from request body)
- ✅ `title` is required and validated (1-200 characters)
- ✅ `description` is optional and validated (max 1000 characters)
- ✅ New tasks default to `completed=false`
- ✅ `created_at` and `updated_at` set to current UTC timestamp
- ✅ Returns 201 Created with task object including auto-generated `id`
- ✅ Returns 401 for missing/invalid JWT token
- ✅ Returns 400 for missing title or validation errors
- ✅ Returns 400 if title is empty string or exceeds 200 characters
- ✅ Returns 400 if description exceeds 1000 characters

---

### 3. Get Single Task

**Endpoint**: `GET /api/tasks/{id}`
**Description**: Retrieve a single task by ID (with ownership verification)
**Authentication**: Required

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Task ID |

#### Request Example

```http
GET /api/tasks/1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response (200 OK)

```json
{
  "id": 1,
  "user_id": "user_2mK8jX9pL3nQ5vR",
  "title": "Complete backend API",
  "description": "Implement all REST endpoints with FastAPI",
  "is_completed": false,
  "created_at": "2026-01-05T10:30:00Z",
  "updated_at": "2026-01-05T10:30:00Z"
}
```

#### Error Responses

**401 Unauthorized** - Missing or invalid JWT token
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden** - Task belongs to another user
```json
{
  "detail": "Not authorized to access this task"
}
```

**404 Not Found** - Task does not exist
```json
{
  "detail": "Task not found"
}
```

#### Implementation Notes

```python
@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session)
) -> TaskResponse:
    """
    Get a single task by ID.

    Security: Verifies task belongs to authenticated user before returning.
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Security: Verify ownership
    if task.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")

    return TaskResponse.from_orm(task)
```

#### Acceptance Criteria

- ✅ Returns task details when task exists and belongs to authenticated user
- ✅ Returns 404 when task ID does not exist in database
- ✅ Returns 403 when task exists but belongs to different user
- ✅ Returns 401 for missing/invalid JWT token
- ✅ Ownership verification happens BEFORE returning task data
- ✅ User cannot enumerate other users' tasks by guessing IDs

---

### 4. Update Task (Full Update)

**Endpoint**: `PUT /api/tasks/{id}`
**Description**: Update task title and/or description (with ownership verification)
**Authentication**: Required

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Task ID |

#### Request Body

```typescript
{
  title: string;        // Required, 1-200 characters
  description?: string; // Optional, max 1000 characters
}
```

#### Request Example

```http
PUT /api/tasks/1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Complete backend API implementation",
  "description": "Implement all REST endpoints with FastAPI and SQLModel"
}
```

#### Response (200 OK)

```json
{
  "id": 1,
  "user_id": "user_2mK8jX9pL3nQ5vR",
  "title": "Complete backend API implementation",
  "description": "Implement all REST endpoints with FastAPI and SQLModel",
  "is_completed": false,
  "created_at": "2026-01-05T10:30:00Z",
  "updated_at": "2026-01-05T15:45:00Z"
}
```

#### Error Responses

**401 Unauthorized** - Missing or invalid JWT token
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden** - Task belongs to another user
```json
{
  "detail": "Not authorized to modify this task"
}
```

**404 Not Found** - Task does not exist
```json
{
  "detail": "Task not found"
}
```

**400 Bad Request** - Validation error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at most 200 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

#### Implementation Notes

```python
class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session)
) -> TaskResponse:
    """
    Update task title and description.

    Security: Verifies task belongs to authenticated user before updating.
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Security: Verify ownership before allowing update
    if task.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")

    # Update fields
    task.title = task_data.title
    task.description = task_data.description
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return TaskResponse.from_orm(task)
```

#### Acceptance Criteria

- ✅ Updates task title and description when task belongs to authenticated user
- ✅ `updated_at` timestamp is refreshed to current UTC time
- ✅ `created_at` timestamp remains unchanged
- ✅ `completed` status is NOT modified (use PATCH /complete endpoint)
- ✅ `user_id` cannot be changed (immutable)
- ✅ Returns 404 when task ID does not exist
- ✅ Returns 403 when task exists but belongs to different user
- ✅ Returns 401 for missing/invalid JWT token
- ✅ Returns 400 for validation errors (title too long, etc.)

---

### 5. Delete Task

**Endpoint**: `DELETE /api/tasks/{id}`
**Description**: Delete a task (with ownership verification)
**Authentication**: Required

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Task ID |

#### Request Example

```http
DELETE /api/tasks/1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response (200 OK)

```json
{
  "message": "Task deleted successfully",
  "deleted_task_id": 1
}
```

#### Error Responses

**401 Unauthorized** - Missing or invalid JWT token
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden** - Task belongs to another user
```json
{
  "detail": "Not authorized to delete this task"
}
```

**404 Not Found** - Task does not exist
```json
{
  "detail": "Task not found"
}
```

#### Implementation Notes

```python
class DeleteResponse(BaseModel):
    message: str
    deleted_task_id: int

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session)
) -> DeleteResponse:
    """
    Delete a task.

    Security: Verifies task belongs to authenticated user before deleting.
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Security: Verify ownership before allowing deletion
    if task.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    db.delete(task)
    db.commit()

    return DeleteResponse(
        message="Task deleted successfully",
        deleted_task_id=task_id
    )
```

#### Acceptance Criteria

- ✅ Deletes task when task belongs to authenticated user
- ✅ Returns success message with deleted task ID
- ✅ Returns 404 when task ID does not exist
- ✅ Returns 403 when task exists but belongs to different user
- ✅ Returns 401 for missing/invalid JWT token
- ✅ Task is permanently removed from database
- ✅ Subsequent GET requests for deleted task return 404

---

### 6. Toggle Task Completion Status

**Endpoint**: `PATCH /api/tasks/{id}/complete`
**Description**: Toggle task completed status (true ↔ false)
**Authentication**: Required

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Task ID |

#### Request Example

```http
PATCH /api/tasks/1/complete HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response (200 OK)

```json
{
  "id": 1,
  "user_id": "user_2mK8jX9pL3nQ5vR",
  "title": "Complete backend API",
  "description": "Implement all REST endpoints with FastAPI",
  "is_completed": true,
  "created_at": "2026-01-05T10:30:00Z",
  "updated_at": "2026-01-05T16:20:00Z"
}
```

#### Error Responses

**401 Unauthorized** - Missing or invalid JWT token
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden** - Task belongs to another user
```json
{
  "detail": "Not authorized to modify this task"
}
```

**404 Not Found** - Task does not exist
```json
{
  "detail": "Task not found"
}
```

#### Implementation Notes

```python
@router.patch("/tasks/{task_id}/complete")
async def toggle_task_completion(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session)
) -> TaskResponse:
    """
    Toggle task completion status (true ↔ false).

    Security: Verifies task belongs to authenticated user before toggling.
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Security: Verify ownership before allowing status change
    if task.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return TaskResponse.from_orm(task)
```

#### Acceptance Criteria

- ✅ Toggles `completed` from `false` to `true` when currently incomplete
- ✅ Toggles `completed` from `true` to `false` when currently complete
- ✅ `updated_at` timestamp is refreshed to current UTC time
- ✅ Title and description remain unchanged
- ✅ Returns 404 when task ID does not exist
- ✅ Returns 403 when task exists but belongs to different user
- ✅ Returns 401 for missing/invalid JWT token
- ✅ Idempotent: Multiple PATCH requests toggle status back and forth

---

## Pydantic Models

### Request Models

```python
from pydantic import BaseModel, Field
from typing import Optional

class TaskCreate(BaseModel):
    """Request model for creating a new task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

class TaskUpdate(BaseModel):
    """Request model for updating an existing task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
```

### Response Models

```python
from datetime import datetime
from pydantic import BaseModel, Field

class TaskResponse(BaseModel):
    """Response model for task data."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    is_completed: bool = Field(alias="completed")  # Alias for frontend compatibility
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (use orm_mode=True for v1)
        populate_by_name = True  # Allow both 'completed' and 'is_completed'

class TaskListResponse(BaseModel):
    """Response model for task list with metadata."""
    tasks: list[TaskResponse]
    total: int
    status_filter: str
    sort_by: str

class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    message: str
    deleted_task_id: int
```

---

## HTTP Status Codes

| Code | Status | When Used |
|------|--------|-----------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE requests |
| 201 | Created | Successful POST request creating new task |
| 400 | Bad Request | Invalid request body, validation errors, invalid query params |
| 401 | Unauthorized | Missing JWT, invalid JWT signature, expired JWT |
| 403 | Forbidden | Valid JWT but user attempting to access another user's task |
| 404 | Not Found | Task ID does not exist in database |
| 500 | Internal Server Error | Unexpected server errors (should be rare) |

---

## Error Response Format

All error responses follow FastAPI's standard error format:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors (400 Bad Request), Pydantic provides detailed field-level errors:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at most 200 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

**Error Handling Principles**:
- Never expose stack traces or internal implementation details
- Use generic messages for authentication failures (don't reveal "user exists" vs "wrong password")
- Provide helpful validation messages for 400 errors
- Log errors server-side with request IDs for debugging

---

## Security Notes

### User Isolation (Critical)

**All endpoints MUST enforce user isolation:**

```python
# ✅ CORRECT: Filter by authenticated user_id from JWT
current_user_id = Depends(get_current_user_id)
task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user_id).first()

# ❌ WRONG: Never trust user_id from request body or query params
user_id = request_data.get("user_id")  # NEVER DO THIS
task = db.query(Task).filter(Task.id == task_id).first()
```

### Ownership Verification

**Before modifying or deleting tasks, verify ownership:**

```python
# Check task exists
if not task:
    raise HTTPException(status_code=404, detail="Task not found")

# Verify ownership BEFORE allowing operation
if task.user_id != current_user_id:
    raise HTTPException(status_code=403, detail="Not authorized to access this task")
```

### JWT Dependency Chain

All endpoints use FastAPI's dependency injection:

```python
from app.auth import get_current_user_id

@router.get("/tasks")
async def list_tasks(
    current_user_id: str = Depends(get_current_user_id),  # Extracts user_id from JWT
    db: Session = Depends(get_session)
):
    # current_user_id is guaranteed to be from verified JWT
    tasks = db.query(Task).filter(Task.user_id == current_user_id).all()
```

See [authentication.md](../features/authentication.md) for `get_current_user_id()` implementation.

### HTTPS in Production

- Development: HTTP on localhost is acceptable
- Production: HTTPS ONLY (TLS/SSL required)
- JWT tokens transmitted in Authorization header are sensitive credentials

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Integration with Frontend

### API Client Configuration

Frontend TypeScript API client from `frontend/src/lib/api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// All requests include JWT token
headers: {
  'Authorization': `Bearer ${getAuthToken()}`,
  'Content-Type': 'application/json'
}
```

### Response Field Mapping

Backend uses `completed` (database field), frontend expects `is_completed`:

```python
class TaskResponse(BaseModel):
    is_completed: bool = Field(alias="completed")

    class Config:
        populate_by_name = True  # Accept both names
```

This allows frontend to use `task.is_completed` while database stores `task.completed`.

---

## Testing Strategy

### Unit Tests

Test each endpoint with pytest:

```python
def test_create_task_success(client, auth_headers):
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Test task", "description": "Test description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["is_completed"] is False

def test_create_task_without_auth(client):
    response = client.post(
        "/api/tasks",
        json={"title": "Test task"}
    )
    assert response.status_code == 401

def test_get_task_ownership_violation(client, auth_headers_user1, auth_headers_user2):
    # User1 creates task
    response = client.post("/api/tasks", headers=auth_headers_user1, json={"title": "User1 task"})
    task_id = response.json()["id"]

    # User2 tries to access User1's task
    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers_user2)
    assert response.status_code == 403
```

### Integration Tests

Test complete workflows:

```python
def test_task_lifecycle(client, auth_headers):
    # Create task
    create_response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Integration test task"}
    )
    task_id = create_response.json()["id"]

    # Get task
    get_response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 200

    # Update task
    update_response = client.put(
        f"/api/tasks/{task_id}",
        headers=auth_headers,
        json={"title": "Updated title", "description": "Updated description"}
    )
    assert update_response.json()["title"] == "Updated title"

    # Toggle completion
    complete_response = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert complete_response.json()["is_completed"] is True

    # Delete task
    delete_response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    # Verify deletion
    get_deleted = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_deleted.status_code == 404
```

---

## Acceptance Criteria

### Overall API Requirements

- ✅ All endpoints require valid JWT authentication
- ✅ All endpoints enforce user isolation (user can only access their own tasks)
- ✅ All responses return proper HTTP status codes
- ✅ All error responses use consistent JSON format
- ✅ Pydantic validates all request bodies
- ✅ Database queries are parameterized (no SQL injection)
- ✅ CORS configured for frontend origin

### Endpoint-Specific Criteria

**GET /api/tasks**:
- ✅ Returns only authenticated user's tasks
- ✅ Supports filtering by status (all/pending/completed)
- ✅ Supports sorting (created/title/updated)
- ✅ Returns empty array when user has no tasks

**POST /api/tasks**:
- ✅ Creates task with user_id from JWT
- ✅ Validates title length (1-200 chars)
- ✅ Validates description length (max 1000 chars)
- ✅ Returns 201 Created with new task

**GET /api/tasks/{id}**:
- ✅ Returns task when owned by user
- ✅ Returns 403 when owned by different user
- ✅ Returns 404 when task doesn't exist

**PUT /api/tasks/{id}**:
- ✅ Updates task when owned by user
- ✅ Returns 403 when owned by different user
- ✅ Validates title and description
- ✅ Updates `updated_at` timestamp

**DELETE /api/tasks/{id}**:
- ✅ Deletes task when owned by user
- ✅ Returns 403 when owned by different user
- ✅ Returns success message with deleted ID

**PATCH /api/tasks/{id}/complete**:
- ✅ Toggles completion status when owned by user
- ✅ Returns 403 when owned by different user
- ✅ Updates `updated_at` timestamp

### Security Requirements

- ✅ No endpoint accepts `user_id` from request body/params
- ✅ All `user_id` values extracted from verified JWT
- ✅ Ownership verified before read/update/delete operations
- ✅ No stack traces or sensitive info in error responses
- ✅ HTTPS required in production

---

## Dependencies

This specification depends on:

- [authentication.md](../features/authentication.md) - JWT verification and `get_current_user_id()` dependency
- [schema.md](../database/schema.md) - Task SQLModel class and database structure

Required by:

- Frontend API client (`frontend/src/lib/api.ts`)
- Integration tests

---

## Implementation Checklist

- [ ] Create FastAPI router at `app/routers/tasks.py`
- [ ] Implement all 6 endpoints with proper signatures
- [ ] Add Pydantic request/response models
- [ ] Configure dependency injection for JWT authentication
- [ ] Add database session management
- [ ] Implement ownership verification for all endpoints
- [ ] Add query parameter validation for GET /api/tasks
- [ ] Configure CORS middleware for frontend origin
- [ ] Write unit tests for each endpoint
- [ ] Write integration tests for complete workflows
- [ ] Test error scenarios (401, 403, 404, 400)
- [ ] Verify user isolation with multiple test users
- [ ] Test all validation rules (title/description lengths)
- [ ] Document API with OpenAPI/Swagger
- [ ] Load test with realistic user scenarios

---

**Status**: Specification Complete
**Next Steps**: Run `/sp.plan` to generate implementation plan
