# MCP Skill: add_task

> **Version**: 1.0.0
> **Phase**: 3 (AI-Powered Features)
> **Database**: Neon PostgreSQL

---

## Overview

| Property | Value |
|----------|-------|
| **Skill Name** | `add_task` |
| **Purpose** | User ke natural language message se naya task create karna aur Neon PostgreSQL DB mein save karna |
| **Auth Required** | Yes (JWT Token via Better Auth) |
| **Endpoint** | `POST /api/mcp/skills/add_task` |

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Better Auth se current logged-in user ka ID |
| `title` | string | ✅ Yes | Task ka main title (1-200 characters) |
| `description` | string | ❌ No | Task ki detail ya note (max 1000 characters) |

---

## Returns

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | integer | Naya task ka auto-generated ID (-1 agar error) |
| `status` | string | `"created"` ya `"error"` |
| `title` | string | Jo title diya tha |
| `message` | string | Success/error message (friendly Roman Urdu mein) |

---

## Example User Messages

AI ko yeh natural language patterns samajhne chahiye:

```
"Mujhe kal grocery leni hai"
"Add task: Meeting at 3pm"
"Naya kaam: Report submit karna hai"
"Todo add karo: Call client"
"Reminder set karo: Doctor appointment"
"Task bana do: Project deadline Friday"
```

---

## Example Tool Call

### Input JSON:
```json
{
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

### Output JSON (Success):
```json
{
  "task_id": 5,
  "status": "created",
  "title": "Buy groceries",
  "message": "Task 'Buy groceries' successfully add ho gaya! ✓"
}
```

### Output JSON (Error):
```json
{
  "task_id": -1,
  "status": "error",
  "title": "Buy groceries",
  "message": "User verify nahi ho saka. Pehle login karein."
}
```

---

## Behavior

### Step by Step Process:

```
┌─────────────────────────────────────────────────────────────┐
│  1. INPUT VALIDATION                                        │
│     - Pydantic se user_id, title validate karo              │
│     - title required hai (1-200 chars)                      │
│     - description optional hai (max 1000 chars)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. USER VERIFICATION                                       │
│     - Better Auth se user exist karta hai ya nahi check     │
│     - Agar user nahi mila → error return karo               │
│     - Ownership ensure karo                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. TASK OBJECT CREATE (SQLModel)                           │
│     - user_id = current user (ownership)                    │
│     - title = user input                                    │
│     - description = user input (optional)                   │
│     - completed = False (new task)                          │
│     - created_at = datetime.utcnow()                        │
│     - updated_at = datetime.utcnow()                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. DATABASE SAVE                                           │
│     - session.add(new_task)                                 │
│     - session.commit()                                      │
│     - session.refresh(new_task) → auto ID                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. RESPONSE RETURN                                         │
│     - Success: task_id, status="created", message           │
│     - Error: task_id=-1, status="error", message            │
└─────────────────────────────────────────────────────────────┘
```

### Security Rules:
- ✅ user_id JWT token se automatically milega
- ✅ Manual user_id accept nahi hota (security reason)
- ✅ Sirf logged-in user apna task add kar sakta hai
- ✅ Ownership enforce hoti hai

### Error Handling:
- ❌ User nahi mila → "User verify nahi ho saka. Pehle login karein."
- ❌ Database error → "Database se connection nahi ho saka."
- ❌ Validation error → "Title dena zaroori hai."
- ❌ Unknown error → "Task add nahi ho saka. Dobara try karein."

---

## MCP SDK Compatible Schema

```json
{
  "name": "add_task",
  "description": "User ke natural language message se naya task create karta hai aur Neon PostgreSQL DB mein save karta hai.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "Better Auth se current logged-in user ka ID"
      },
      "title": {
        "type": "string",
        "description": "Task ka main title (1-200 characters)",
        "minLength": 1,
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "Task ki detail ya note (optional, max 1000 chars)",
        "maxLength": 1000
      }
    },
    "required": ["user_id", "title"],
    "additionalProperties": false
  }
}
```

---

## Code Snippets

### 1. SQLModel Task Model (`app/models.py`)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model for Neon PostgreSQL."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. FastAPI Endpoint (`app/routers/mcp.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.database import get_session
from app.auth import get_current_user_id
from app.models import Task, User

router = APIRouter(prefix="/api/mcp", tags=["mcp-skills"])

# Request Model
class AddTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

# Response Model
class AddTaskResponse(BaseModel):
    task_id: int
    status: str
    title: str
    message: str

@router.post("/skills/add_task", response_model=AddTaskResponse)
async def add_task_skill(
    request: AddTaskRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> AddTaskResponse:
    """
    MCP Skill: add_task

    Naya task create karta hai authenticated user ke liye.
    user_id JWT token se automatically milta hai.
    """
    try:
        # User verification
        user = session.exec(
            select(User).where(User.id == current_user_id)
        ).first()

        if not user:
            return AddTaskResponse(
                task_id=-1,
                status="error",
                title=request.title,
                message="User verify nahi ho saka. Pehle login karein."
            )

        # Task create karo
        new_task = Task(
            user_id=current_user_id,
            title=request.title,
            description=request.description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Database mein save karo
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        # Success response
        return AddTaskResponse(
            task_id=new_task.id,
            status="created",
            title=new_task.title,
            message=f"Task '{new_task.title}' successfully add ho gaya! ✓"
        )

    except Exception as e:
        return AddTaskResponse(
            task_id=-1,
            status="error",
            title=request.title,
            message=f"Task add nahi ho saka. Error: {str(e)[:50]}"
        )
```

### 3. Curl Test Command

```bash
# Login karke token lo
TOKEN=$(curl -s -X POST "https://your-api.railway.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.token')

# Task add karo
curl -X POST "https://your-api.railway.app/api/mcp/skills/add_task" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

### 4. Frontend Integration (TypeScript)

```typescript
// lib/mcp-skills.ts
import { getAuthToken } from './auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

interface AddTaskInput {
  title: string;
  description?: string;
}

interface AddTaskOutput {
  task_id: number;
  status: 'created' | 'error';
  title: string;
  message: string;
}

export async function addTask(input: AddTaskInput): Promise<AddTaskOutput> {
  const token = getAuthToken();

  const response = await fetch(`${API_BASE}/api/mcp/skills/add_task`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(input)
  });

  return response.json();
}

// Usage
const result = await addTask({
  title: "Buy groceries",
  description: "Milk, eggs, bread"
});

console.log(result.message); // "Task 'Buy groceries' successfully add ho gaya! ✓"
```

---

## Error Codes

| Error | HTTP Code | Message |
|-------|-----------|---------|
| No token | 401 | "Pehle login karein" |
| Token expired | 401 | "Session expire ho gaya" |
| User not found | 400 | "User verify nahi ho saka" |
| Validation error | 422 | "Title dena zaroori hai" |
| DB connection | 500 | "Database se connection nahi ho saka" |
| Unknown | 500 | "Task add nahi ho saka" |

---

## File Location

```
backend/
├── skills/
│   ├── add_task.py      ← Main implementation
│   └── add_task.md      ← This documentation
├── app/
│   ├── models.py        ← Task SQLModel
│   ├── routers/
│   │   └── mcp.py       ← FastAPI endpoint
│   └── ...
```

---

## Related Skills

- [`list_tasks`](./list_tasks.md) - Tasks fetch karna
- [`complete_task`](./complete_task.md) - Task complete karna
- [`delete_task`](./delete_task.md) - Task delete karna
- [`update_task`](./update_task.md) - Task update karna

---

> **Last Updated**: 2026-01-14
> **Maintainer**: Todo App Phase 3 Team
