# MCP Skill: update_task

> **Version**: 1.0.0
> **Phase**: 3 (AI-Powered Features)
> **Database**: Neon PostgreSQL

---

## Overview

| Property | Value |
|----------|-------|
| **Skill Name** | `update_task` |
| **Purpose** | Task ka title ya description edit karna |
| **Auth Required** | Yes (JWT Token via Better Auth) |
| **Endpoint** | `PUT /api/tasks/{id}` |

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Current logged-in user ka ID |
| `task_id` | integer | ✅ Yes | Task ka ID jo update karna hai |
| `title` | string | ❌ No | Naya title (agar nahi diya to purana rahega) |
| `description` | string | ❌ No | Nayi description (agar nahi di to purani rahegi) |

**Note**: `title` ya `description` mein se kam az kam ek dena zaroori hai.

---

## Returns

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | integer | Updated task ka ID |
| `status` | string | `"updated"` ya `"error"` |
| `title` | string | Updated title |
| `description` | string/null | Updated description |
| `message` | string | Success/error message (Roman Urdu) |

---

## Example User Messages

AI ko yeh natural language patterns samajhne chahiye:

```
"Task 1 ka title change karo 'Buy vegetables'"
"Grocery task mein bread bhi add karo description mein"
"Update task 3: Meeting 3pm pe hai"
"Pehle task ko rename karo"
"Task number 5 ki description update karo"
"Task 2 mein eggs add karo"
"Change task title to 'Important Meeting'"
```

---

## Example Tool Call

### Input JSON (Update Title Only):
```json
{
  "user_id": "user123",
  "task_id": 1,
  "title": "Buy groceries and fruits"
}
```

### Input JSON (Update Description Only):
```json
{
  "user_id": "user123",
  "task_id": 1,
  "description": "Milk, eggs, apples, bananas"
}
```

### Input JSON (Update Both):
```json
{
  "user_id": "user123",
  "task_id": 1,
  "title": "Weekly Shopping",
  "description": "Groceries for the week"
}
```

---

## Example Output JSON

### Success (Title Updated):
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs",
  "message": "Task title update ho gaya!"
}
```

### Success (Description Updated):
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries",
  "description": "Milk, eggs, apples, bananas",
  "message": "Task description update ho gayi!"
}
```

### Success (Both Updated):
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Weekly Shopping",
  "description": "Groceries for the week",
  "message": "Task title aur description dono update ho gaye!"
}
```

### Error - Task Not Found:
```json
{
  "task_id": 1,
  "status": "error",
  "title": "",
  "description": null,
  "message": "Task nahi mila. Shayad delete ho gaya hai."
}
```

### Error - Nothing to Update:
```json
{
  "task_id": 1,
  "status": "error",
  "title": "",
  "description": null,
  "message": "Kuch update karne ko nahi hai. Title ya description dein."
}
```

---

## Behavior

### Step by Step Process:

```
┌─────────────────────────────────────────────────────────────┐
│  1. INPUT VALIDATION                                        │
│     - user_id required hai                                  │
│     - task_id required hai (integer > 0)                    │
│     - title ya description mein se ek zaroori               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. CHECK KE KUCH UPDATE KARNA HAI                          │
│     - Agar title aur description dono None                  │
│     - Return error: "Kuch update karne ko nahi hai"         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. TASK FIND KARO                                          │
│     - session.get(Task, task_id)                            │
│     - Agar nahi mila → error return                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. OWNERSHIP VERIFY KARO                                   │
│     - task.user_id == input.user_id ?                       │
│     - Agar nahi → "Yeh task aapka nahi hai"                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. SIRF DI GAYI FIELDS UPDATE KARO                         │
│     - if title != None: task.title = title                  │
│     - if description != None: task.description = desc       │
│     - Purani values preserve rehti hain                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  6. UPDATED_AT UPDATE KARO                                  │
│     - task.updated_at = datetime.utcnow()                   │
│     - session.commit()                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  7. SUCCESS RESPONSE                                        │
│     - status: "updated"                                     │
│     - message based on what was changed                     │
└─────────────────────────────────────────────────────────────┘
```

### Security Rules:
- ✅ user_id JWT token se automatically milega
- ✅ Ownership check mandatory hai
- ✅ Sirf apna task update kar sakte hain
- ✅ completed status yahan se change nahi hota (use complete_task)

### Partial Update Logic:
| Input | Result |
|-------|--------|
| title only | Sirf title change, description same |
| description only | Sirf description change, title same |
| both | Dono change |
| neither | Error |

---

## MCP SDK Compatible Schema

```json
{
  "name": "update_task",
  "description": "Task ka title ya description edit karta hai. Sirf di gayi fields update hoti hain.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "Current logged-in user ka ID"
      },
      "task_id": {
        "type": "integer",
        "description": "Task ka ID jo update karna hai"
      },
      "title": {
        "type": "string",
        "description": "Naya title (optional)",
        "minLength": 1,
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "Nayi description (optional)",
        "maxLength": 1000
      }
    },
    "required": ["user_id", "task_id"],
    "additionalProperties": false
  }
}
```

---

## Code Snippets

### 1. Core Logic (`skills/update_task.py`)

```python
from sqlmodel import Session
from datetime import datetime
from app.models import Task

def update_task_core(
    session: Session,
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None
):
    """
    Task update karne ka core logic.

    Step 1: Check ke kuch update karna hai
    Step 2: Task find karo
    Step 3: Ownership verify karo
    Step 4: Sirf di gayi fields update karo
    Step 5: updated_at update karo
    """

    # Step 1: Check
    if title is None and description is None:
        return {"status": "error", "message": "Kuch update karne ko nahi hai"}

    # Step 2: Task find karo
    task = session.get(Task, task_id)

    if not task:
        return {"status": "error", "message": "Task nahi mila"}

    # Step 3: Ownership check
    if task.user_id != user_id:
        return {"status": "error", "message": "Yeh task aapka nahi hai"}

    # Step 4: Update sirf di gayi fields
    changes = []
    if title is not None:
        task.title = title
        changes.append("title")

    if description is not None:
        task.description = description
        changes.append("description")

    # Step 5: updated_at
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Build message
    if len(changes) == 2:
        message = "Task title aur description dono update ho gaye!"
    elif "title" in changes:
        message = "Task title update ho gaya!"
    else:
        message = "Task description update ho gayi!"

    return {
        "status": "updated",
        "title": task.title,
        "description": task.description,
        "message": message
    }
```

### 2. FastAPI Endpoint (`app/routers/tasks.py`)

```python
# Yeh endpoint already exist karta hai
# PUT /api/tasks/{task_id}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from app.database import get_session
from app.auth import get_current_user_id
from app.models import Task
from app.schemas import TaskResponse, TaskUpdate

router = APIRouter(prefix="/api", tags=["tasks"])

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Update task title and description.
    Only provided fields are updated.
    """
    # Find task
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Ownership check
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task"
        )

    # Update fields
    task.title = task_data.title
    task.description = task_data.description
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)
```

### 3. MCP Skill Endpoint (`app/routers/mcp.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.database import get_session
from app.auth import get_current_user_id
from skills.update_task import update_task_async, UpdateTaskOutput

router = APIRouter(prefix="/api/mcp", tags=["mcp-skills"])

class UpdateTaskRequest(BaseModel):
    task_id: int = Field(..., gt=0, description="Task ID")
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

@router.post("/skills/update_task", response_model=UpdateTaskOutput)
async def mcp_update_task(
    request: UpdateTaskRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> UpdateTaskOutput:
    """
    MCP Skill: update_task

    Task ka title ya description update karta hai.
    """
    result = await update_task_async(
        user_id=current_user_id,
        task_id=request.task_id,
        title=request.title,
        description=request.description,
        session=session
    )

    if result.status == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )

    return result
```

### 4. Curl Test Commands

```bash
# Login karke token lo
TOKEN=$(curl -s -X POST "https://your-api.railway.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.token')

# Task update karo (existing endpoint)
curl -X PUT "https://your-api.railway.app/api/tasks/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries and fruits", "description": "Updated list"}'

# Ya MCP skill use karo
curl -X POST "https://your-api.railway.app/api/mcp/skills/update_task" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1, "title": "New Title"}'
```

### 5. Frontend Integration (TypeScript)

```typescript
// lib/mcp-skills.ts
import { getAuthToken } from './auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

interface UpdateTaskInput {
  task_id: number;
  title?: string;
  description?: string;
}

interface UpdateTaskOutput {
  task_id: number;
  status: 'updated' | 'error';
  title: string;
  description: string | null;
  message: string;
}

export async function updateTask(input: UpdateTaskInput): Promise<UpdateTaskOutput> {
  const token = getAuthToken();

  // Build update payload (only include provided fields)
  const payload: Record<string, any> = {};
  if (input.title !== undefined) payload.title = input.title;
  if (input.description !== undefined) payload.description = input.description;

  const response = await fetch(
    `${API_BASE}/api/tasks/${input.task_id}`,
    {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    }
  );

  if (!response.ok) {
    const error = await response.json();
    return {
      task_id: input.task_id,
      status: 'error',
      title: '',
      description: null,
      message: error.detail || 'Task update nahi ho saka'
    };
  }

  const task = await response.json();

  return {
    task_id: task.id,
    status: 'updated',
    title: task.title,
    description: task.description,
    message: 'Task update ho gaya!'
  };
}

// Usage
const result = await updateTask({
  task_id: 1,
  title: "Buy groceries and fruits"
});
console.log(result.message); // "Task update ho gaya!"
```

---

## AI Response Templates

### Template 1: Success - Title Updated
```
✓ Task ka title update ho gaya!

Pehle: "{old_title}"
Ab: "{new_title}"

Kuch aur change karna hai?
```

### Template 2: Success - Description Updated
```
✓ Task ki description update ho gayi!

Task: {title}
Nayi description: {description}
```

### Template 3: Success - Both Updated
```
✓ Task title aur description dono update ho gaye!

Title: {title}
Description: {description}
```

### Template 4: Error - Nothing to Update
```
Kya update karna hai? 🤔

Title ya description mein se kuch to batao.

Example: "Task 1 ka title change karo 'New Title'"
```

---

## Error Codes

| Error | HTTP Code | Message |
|-------|-----------|---------|
| No token | 401 | "Pehle login karein" |
| Token expired | 401 | "Session expire ho gaya" |
| Task not found | 404 | "Task nahi mila" |
| Not owner | 403 | "Yeh task aapka nahi hai" |
| Nothing to update | 400 | "Kuch update karne ko nahi hai" |
| Invalid title | 422 | "Title 1-200 characters hona chahiye" |
| DB error | 500 | "Task update nahi ho saka" |

---

## File Location

```
backend/
├── skills/
│   ├── __init__.py
│   ├── add_task.py
│   ├── add_task.md
│   ├── list_tasks.py
│   ├── list_tasks.md
│   ├── complete_task.py
│   ├── complete_task.md
│   ├── delete_task.py
│   ├── delete_task.md
│   ├── update_task.py     ← Main implementation
│   └── update_task.md     ← This documentation
├── app/
│   └── routers/
│       └── tasks.py       ← Existing PUT endpoint
```

---

## Related Skills

- [`add_task`](./add_task.md) - Naya task create karna
- [`list_tasks`](./list_tasks.md) - Tasks fetch karna
- [`complete_task`](./complete_task.md) - Task complete karna
- [`delete_task`](./delete_task.md) - Task delete karna

---

> **Last Updated**: 2026-01-14
> **Maintainer**: Todo App Phase 3 Team
