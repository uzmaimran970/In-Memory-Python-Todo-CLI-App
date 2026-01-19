# MCP Skill: complete_task

> **Version**: 1.0.0
> **Phase**: 3 (AI-Powered Features)
> **Database**: Neon PostgreSQL

---

## Overview

| Property | Value |
|----------|-------|
| **Skill Name** | `complete_task` |
| **Purpose** | Kisi task ko complete mark karna (completed = True) |
| **Auth Required** | Yes (JWT Token via Better Auth) |
| **Endpoint** | `PATCH /api/tasks/{id}/complete` |

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Current logged-in user ka ID |
| `task_id` | integer | ✅ Yes | Task ka ID jo complete karna hai |

---

## Returns

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | integer | Task ka ID |
| `status` | string | `"completed"` ya `"error"` |
| `title` | string | Task ka title |
| `message` | string | Success/error message (Roman Urdu) |

---

## Example User Messages

AI ko yeh natural language patterns samajhne chahiye:

```
"Task 3 complete ho gaya"
"Grocery wala kaam done hai"
"Mark task 5 as complete"
"Pehla task finish ho gaya"
"Task number 2 done"
"Meeting wala kaam ho gaya"
"✓ Task 7"
```

---

## Example Tool Call

### Input JSON:
```json
{
  "user_id": "user123",
  "task_id": 3
}
```

---

## Example Output JSON

### Success:
```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom",
  "message": "Task 'Call mom' complete ho gaya! 🎉 Shabash!"
}
```

### Already Complete:
```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom",
  "message": "Task 'Call mom' pehle se complete hai! ✓"
}
```

### Error - Task Not Found:
```json
{
  "task_id": 3,
  "status": "error",
  "title": "",
  "message": "Task nahi mila. Shayad delete ho gaya hai."
}
```

### Error - Not Owner:
```json
{
  "task_id": 3,
  "status": "error",
  "title": "",
  "message": "Yeh task aapka nahi hai. Sirf apna task complete kar sakte hain."
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
│  4. ALREADY COMPLETE CHECK                                  │
│     - Agar task.completed == True                           │
│     - Return: "pehle se complete hai"                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. TASK UPDATE KARO                                        │
│     - task.completed = True                                 │
│     - task.updated_at = datetime.utcnow()                   │
│     - session.commit()                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  6. SUCCESS RESPONSE                                        │
│     - status: "completed"                                   │
│     - message: "Task 'X' complete ho gaya! 🎉"              │
└─────────────────────────────────────────────────────────────┘
```

### Security Rules:
- ✅ user_id JWT token se automatically milega
- ✅ Ownership check mandatory hai
- ✅ Sirf apna task complete kar sakte hain
- ✅ Doosre user ka task access nahi kar sakte

### Edge Cases:
| Case | Response |
|------|----------|
| Task not found | error: "Task nahi mila" |
| Not owner | error: "Yeh task aapka nahi hai" |
| Already complete | success: "pehle se complete hai" |
| DB error | error: "Task complete nahi ho saka" |

---

## MCP SDK Compatible Schema

```json
{
  "name": "complete_task",
  "description": "Kisi task ko complete mark karta hai (completed = True). Sirf logged-in user apna task complete kar sakta hai.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "Current logged-in user ka ID"
      },
      "task_id": {
        "type": "integer",
        "description": "Task ka ID jo complete karna hai"
      }
    },
    "required": ["user_id", "task_id"],
    "additionalProperties": false
  }
}
```

---

## Code Snippets

### 1. Core Logic (`skills/complete_task.py`)

```python
from sqlmodel import Session
from datetime import datetime
from app.models import Task

def complete_task_core(session: Session, user_id: str, task_id: int):
    """
    Task complete karne ka core logic.

    Step 1: Task find karo
    Step 2: Ownership verify karo
    Step 3: Complete = True set karo
    Step 4: updated_at update karo
    """

    # Step 1: Task find karo
    task = session.get(Task, task_id)

    if not task:
        return {"status": "error", "message": "Task nahi mila"}

    # Step 2: Ownership check
    if task.user_id != user_id:
        return {"status": "error", "message": "Yeh task aapka nahi hai"}

    # Step 3 & 4: Update karo
    task.completed = True
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return {
        "status": "completed",
        "title": task.title,
        "message": f"Task '{task.title}' complete ho gaya! 🎉"
    }
```

### 2. FastAPI Endpoint (`app/routers/mcp.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, Field

from app.database import get_session
from app.auth import get_current_user_id
from skills.complete_task import complete_task_async, CompleteTaskOutput

router = APIRouter(prefix="/api/mcp", tags=["mcp-skills"])

class CompleteTaskRequest(BaseModel):
    task_id: int = Field(..., gt=0, description="Task ID")

@router.post("/skills/complete_task", response_model=CompleteTaskOutput)
async def mcp_complete_task(
    request: CompleteTaskRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> CompleteTaskOutput:
    """
    MCP Skill: complete_task

    Task ko complete mark karta hai.
    user_id JWT token se automatically milta hai.
    """
    result = await complete_task_async(
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

### 3. Existing Toggle Endpoint (`app/routers/tasks.py`)

```python
# Yeh endpoint already exist karta hai
# PATCH /api/tasks/{id}/complete

@router.patch("/tasks/{id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """Toggle task completion (complete ↔ incomplete)."""

    task = session.get(Task, id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Toggle
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)
```

### 4. Curl Test Commands

```bash
# Login karke token lo
TOKEN=$(curl -s -X POST "https://your-api.railway.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.token')

# Task complete karo (Toggle)
curl -X PATCH "https://your-api.railway.app/api/tasks/3/complete" \
  -H "Authorization: Bearer $TOKEN"

# Ya MCP skill use karo
curl -X POST "https://your-api.railway.app/api/mcp/skills/complete_task" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id": 3}'
```

### 5. Frontend Integration (TypeScript)

```typescript
// lib/mcp-skills.ts
import { getAuthToken } from './auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

interface CompleteTaskOutput {
  task_id: number;
  status: 'completed' | 'error';
  title: string;
  message: string;
}

export async function completeTask(taskId: number): Promise<CompleteTaskOutput> {
  const token = getAuthToken();

  // Use existing toggle endpoint
  const response = await fetch(
    `${API_BASE}/api/tasks/${taskId}/complete`,
    {
      method: 'PATCH',
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
      message: error.detail || 'Task complete nahi ho saka'
    };
  }

  const task = await response.json();

  return {
    task_id: task.id,
    status: task.completed ? 'completed' : 'incomplete',
    title: task.title,
    message: task.completed
      ? `Task '${task.title}' complete ho gaya! 🎉`
      : `Task '${task.title}' incomplete mark ho gaya.`
  };
}

// Usage
const result = await completeTask(3);
console.log(result.message); // "Task 'Call mom' complete ho gaya! 🎉"
```

---

## AI Response Templates

### Template 1: Success
```
✅ {title} complete ho gaya!

Aur koi task complete karna hai ya naye task add karne hain?
```

### Template 2: Already Complete
```
Yeh task pehle se done hai! ✓

Aapke {pending_count} pending tasks hain abhi.
```

### Template 3: Error - Not Found
```
Hmm, yeh task nahi mila. 🤔

Shayad delete ho gaya hai. Apne tasks dekhne ke liye "meri tasks dikhao" bolein.
```

### Template 4: Error - Not Owner
```
Yeh task kisi aur ka hai.

Sirf apne tasks complete kar sakte hain. Apni task list dekhein?
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
| DB error | 500 | "Task complete nahi ho saka" |

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
│   ├── complete_task.py   ← Main implementation
│   └── complete_task.md   ← This documentation
├── app/
│   └── routers/
│       └── tasks.py       ← Existing PATCH endpoint
```

---

## Related Skills

- [`add_task`](./add_task.md) - Naya task create karna
- [`list_tasks`](./list_tasks.md) - Tasks fetch karna
- [`delete_task`](./delete_task.md) - Task delete karna
- [`update_task`](./update_task.md) - Task update karna

---

> **Last Updated**: 2026-01-14
> **Maintainer**: Todo App Phase 3 Team
