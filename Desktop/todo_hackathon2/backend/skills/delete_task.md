# MCP Skill: delete_task

> **Version**: 1.0.0
> **Phase**: 3 (AI-Powered Features)
> **Database**: Neon PostgreSQL
>
> ⚠️ **WARNING**: Delete action is PERMANENT and cannot be undone!

---

## Overview

| Property | Value |
|----------|-------|
| **Skill Name** | `delete_task` |
| **Purpose** | Kisi task ko permanently delete karna |
| **Auth Required** | Yes (JWT Token via Better Auth) |
| **Endpoint** | `DELETE /api/tasks/{id}` |
| **Reversible** | ❌ NO - Permanent delete |

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Current logged-in user ka ID |
| `task_id` | integer | ✅ Yes | Task ka ID jo delete karna hai |

---

## Returns

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | integer | Deleted task ka ID |
| `status` | string | `"deleted"` ya `"error"` |
| `title` | string | Deleted task ka title |
| `message` | string | Success/error message (Roman Urdu) |

---

## Example User Messages

AI ko yeh natural language patterns samajhne chahiye:

```
"Task 2 delete kar do"
"Grocery wala task hata do"
"Remove task number 3"
"Yeh kaam cancel hai, delete karo"
"Task 5 ko remove karo"
"Delete my first task"
"Pehla task hata do"
```

---

## Example Tool Call

### Input JSON:
```json
{
  "user_id": "user123",
  "task_id": 2
}
```

---

## Example Output JSON

### Success:
```json
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task",
  "message": "Task 'Old task' delete ho gaya."
}
```

### Error - Task Not Found:
```json
{
  "task_id": 2,
  "status": "error",
  "title": "",
  "message": "Task nahi mila. Shayad pehle se delete hai."
}
```

### Error - Not Owner:
```json
{
  "task_id": 2,
  "status": "error",
  "title": "",
  "message": "Yeh task aapka nahi hai. Sirf apna task delete kar sakte hain."
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
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. TASK FIND KARO                                          │
│     - session.get(Task, task_id)                            │
│     - Agar nahi mila → error return                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. OWNERSHIP VERIFY KARO                                   │
│     - task.user_id == input.user_id ?                       │
│     - Agar nahi → "Yeh task aapka nahi hai"                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. STORE TITLE (before delete)                             │
│     - deleted_title = task.title                            │
│     - Response mein use karne ke liye                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. TASK DELETE KARO ⚠️ PERMANENT!                          │
│     - session.delete(task)                                  │
│     - session.commit()                                      │
│     - Database se permanently remove                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  6. SUCCESS RESPONSE                                        │
│     - status: "deleted"                                     │
│     - message: "Task 'X' delete ho gaya."                   │
└─────────────────────────────────────────────────────────────┘
```

### Security Rules:
- ✅ user_id JWT token se automatically milega
- ✅ Ownership check mandatory hai
- ✅ Sirf apna task delete kar sakte hain
- ✅ Doosre user ka task access nahi kar sakte

### ⚠️ Important Warnings:
| Warning | Description |
|---------|-------------|
| **PERMANENT** | Delete undo nahi ho sakta |
| **No Soft Delete** | Task database se completely remove hota hai |
| **No Recovery** | Deleted task recover nahi ho sakta |

---

## MCP SDK Compatible Schema

```json
{
  "name": "delete_task",
  "description": "Kisi task ko permanently delete karta hai. ⚠️ WARNING: Yeh action undo nahi ho sakta!",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "Current logged-in user ka ID"
      },
      "task_id": {
        "type": "integer",
        "description": "Task ka ID jo delete karna hai"
      }
    },
    "required": ["user_id", "task_id"],
    "additionalProperties": false
  }
}
```

---

## Code Snippets

### 1. Core Logic (`skills/delete_task.py`)

```python
from sqlmodel import Session
from app.models import Task

def delete_task_core(session: Session, user_id: str, task_id: int):
    """
    Task delete karne ka core logic.

    ⚠️ WARNING: PERMANENT delete!

    Step 1: Task find karo
    Step 2: Ownership verify karo
    Step 3: Title store karo (for response)
    Step 4: Delete karo
    """

    # Step 1: Task find karo
    task = session.get(Task, task_id)

    if not task:
        return {"status": "error", "message": "Task nahi mila"}

    # Step 2: Ownership check
    if task.user_id != user_id:
        return {"status": "error", "message": "Yeh task aapka nahi hai"}

    # Step 3: Store title before delete
    deleted_title = task.title

    # Step 4: Delete karo (PERMANENT!)
    session.delete(task)
    session.commit()

    return {
        "status": "deleted",
        "title": deleted_title,
        "message": f"Task '{deleted_title}' delete ho gaya."
    }
```

### 2. FastAPI Endpoint (`app/routers/tasks.py`)

```python
# Yeh endpoint already exist karta hai
# DELETE /api/tasks/{task_id}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.auth import get_current_user_id
from app.models import Task
from app.schemas import DeleteResponse

router = APIRouter(prefix="/api", tags=["tasks"])

@router.delete("/tasks/{task_id}", response_model=DeleteResponse)
async def delete_task(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> DeleteResponse:
    """
    Delete a task permanently.

    ⚠️ WARNING: Cannot be undone!
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
            detail="Not authorized to delete this task"
        )

    # Delete
    session.delete(task)
    session.commit()

    return DeleteResponse(
        message="Task deleted successfully",
        deleted_task_id=task_id
    )
```

### 3. MCP Skill Endpoint (`app/routers/mcp.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, Field

from app.database import get_session
from app.auth import get_current_user_id
from skills.delete_task import delete_task_async, DeleteTaskOutput

router = APIRouter(prefix="/api/mcp", tags=["mcp-skills"])

class DeleteTaskRequest(BaseModel):
    task_id: int = Field(..., gt=0, description="Task ID to delete")

@router.post("/skills/delete_task", response_model=DeleteTaskOutput)
async def mcp_delete_task(
    request: DeleteTaskRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> DeleteTaskOutput:
    """
    MCP Skill: delete_task

    ⚠️ WARNING: Delete is PERMANENT!
    """
    result = await delete_task_async(
        user_id=current_user_id,
        task_id=request.task_id,
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

# Task delete karo (existing endpoint)
curl -X DELETE "https://your-api.railway.app/api/tasks/2" \
  -H "Authorization: Bearer $TOKEN"

# Ya MCP skill use karo
curl -X POST "https://your-api.railway.app/api/mcp/skills/delete_task" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id": 2}'
```

### 5. Frontend Integration (TypeScript)

```typescript
// lib/mcp-skills.ts
import { getAuthToken } from './auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

interface DeleteTaskOutput {
  task_id: number;
  status: 'deleted' | 'error';
  title: string;
  message: string;
}

export async function deleteTask(taskId: number): Promise<DeleteTaskOutput> {
  const token = getAuthToken();

  const response = await fetch(
    `${API_BASE}/api/tasks/${taskId}`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );

  if (!response.ok) {
    const error = await response.json();
    return {
      task_id: taskId,
      status: 'error',
      title: '',
      message: error.detail || 'Task delete nahi ho saka'
    };
  }

  const data = await response.json();

  return {
    task_id: taskId,
    status: 'deleted',
    title: '',  // API doesn't return title on delete
    message: data.message || 'Task delete ho gaya.'
  };
}

// Usage with confirmation
async function handleDeleteTask(taskId: number, taskTitle: string) {
  // Show confirmation dialog first!
  const confirmed = window.confirm(
    `⚠️ Kya aap sure hain? "${taskTitle}" permanently delete ho jayega!`
  );

  if (!confirmed) {
    return { status: 'cancelled', message: 'Delete cancel kar diya.' };
  }

  return await deleteTask(taskId);
}
```

---

## AI Response Templates

### Template 1: Before Delete (Confirmation)
```
⚠️ Kya aap sure hain ke "{title}" delete karna hai?

Yeh action UNDO nahi ho sakta. Task permanently remove ho jayega.

Confirm karne ke liye "haan delete karo" bolein.
```

### Template 2: Success
```
✓ Task "{title}" delete ho gaya.

Aapke {remaining_count} tasks baaki hain.
```

### Template 3: Error - Not Found
```
Hmm, yeh task nahi mila. 🤔

Shayad pehle se delete hai. Apni task list refresh karein?
```

### Template 4: Error - Not Owner
```
Yeh task kisi aur ka hai.

Sirf apne tasks delete kar sakte hain.
```

---

## Error Codes

| Error | HTTP Code | Message |
|-------|-----------|---------|
| No token | 401 | "Pehle login karein" |
| Token expired | 401 | "Session expire ho gaya" |
| Task not found | 404 | "Task nahi mila" |
| Not owner | 403 | "Yeh task aapka nahi hai" |
| Invalid task_id | 422 | "Task ID valid nahi hai" |
| DB error | 500 | "Task delete nahi ho saka" |

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
│   ├── delete_task.py     ← Main implementation
│   └── delete_task.md     ← This documentation
├── app/
│   └── routers/
│       └── tasks.py       ← Existing DELETE endpoint
```

---

## Related Skills

- [`add_task`](./add_task.md) - Naya task create karna
- [`list_tasks`](./list_tasks.md) - Tasks fetch karna
- [`complete_task`](./complete_task.md) - Task complete karna
- [`update_task`](./update_task.md) - Task update karna

---

> **Last Updated**: 2026-01-14
> **Maintainer**: Todo App Phase 3 Team
