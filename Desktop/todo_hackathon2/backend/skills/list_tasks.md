# MCP Skill: list_tasks

> **Version**: 1.0.0
> **Phase**: 3 (AI-Powered Features)
> **Database**: Neon PostgreSQL

---

## Overview

| Property | Value |
|----------|-------|
| **Skill Name** | `list_tasks` |
| **Purpose** | User ke saare ya filtered tasks ki list return karna (all, pending, completed) |
| **Auth Required** | Yes (JWT Token via Better Auth) |
| **Endpoint** | `GET /api/tasks` ya `POST /api/mcp/skills/list_tasks` |

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `user_id` | string | ✅ Yes | - | Current logged-in user ka ID |
| `status` | string | ❌ No | `"all"` | Filter: `"all"`, `"pending"`, ya `"completed"` |

---

## Returns

| Field | Type | Description |
|-------|------|-------------|
| `tasks` | array | Task objects ki array |
| `total` | integer | Total tasks count |
| `status_filter` | string | Applied filter |
| `message` | string | Response message (Roman Urdu) |

### Task Object Structure:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Task ka unique ID |
| `title` | string | Task ka title |
| `description` | string/null | Task ki detail |
| `completed` | boolean | Complete status |
| `created_at` | datetime | Kab bana |
| `updated_at` | datetime | Kab update hua |

---

## Example User Messages

AI ko yeh natural language patterns samajhne chahiye:

```
"Mere saare tasks dikhao"
"Meri todo list"
"Kya kya karna hai?"
"Pending kaam batao"
"Completed tasks ki list do"
"Kitne tasks hain mere?"
"Aaj ke tasks"
```

---

## Example Tool Call

### Input JSON (All Tasks):
```json
{
  "user_id": "user123",
  "status": "all"
}
```

### Input JSON (Pending Only):
```json
{
  "user_id": "user123",
  "status": "pending"
}
```

### Input JSON (Completed Only):
```json
{
  "user_id": "user123",
  "status": "completed"
}
```

---

## Example Output JSON

### Success (Tasks Found):
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-01-14T10:00:00",
      "updated_at": "2026-01-14T10:00:00"
    },
    {
      "id": 2,
      "title": "Call mom",
      "description": null,
      "completed": false,
      "created_at": "2026-01-14T09:00:00",
      "updated_at": "2026-01-14T09:00:00"
    }
  ],
  "total": 2,
  "status_filter": "pending",
  "message": "2 pending tasks mile."
}
```

### Success (No Tasks):
```json
{
  "tasks": [],
  "total": 0,
  "status_filter": "pending",
  "message": "Koi pending task nahi hai. Sab kaam ho gaya! 🎉"
}
```

### Error:
```json
{
  "tasks": [],
  "total": 0,
  "status_filter": "all",
  "message": "User verify nahi ho saka. Pehle login karein."
}
```

---

## Behavior

### Step by Step Process:

```
┌─────────────────────────────────────────────────────────────┐
│  1. INPUT VALIDATION                                        │
│     - user_id required hai                                  │
│     - status optional hai (default: "all")                  │
│     - Valid status: "all", "pending", "completed"           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. USER VERIFICATION                                       │
│     - Check ke user exist karta hai                         │
│     - Agar nahi → empty array + error message               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. BUILD SQLMODEL QUERY                                    │
│     - Base: Task.user_id == current_user_id                 │
│     - if status == "pending": completed == False            │
│     - if status == "completed": completed == True           │
│     - Order by: created_at DESC (naya pehle)                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. EXECUTE QUERY                                           │
│     - session.exec(query).all()                             │
│     - Results ko TaskItem objects mein convert karo         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. FORMAT RESPONSE                                         │
│     - tasks array                                           │
│     - total count                                           │
│     - applied filter                                        │
│     - friendly message (Roman Urdu)                         │
└─────────────────────────────────────────────────────────────┘
```

### Security Rules:
- ✅ user_id JWT token se milega
- ✅ Sirf apne tasks dekh sakta hai (ownership)
- ✅ Doosre users ke tasks access nahi kar sakta
- ✅ user_id query mein ALWAYS filter hoga

### Empty Results Messages:
| Status | Message |
|--------|---------|
| all | "Koi task nahi mila. Naya task add karein!" |
| pending | "Koi pending task nahi hai. Sab kaam ho gaya! 🎉" |
| completed | "Koi completed task nahi hai abhi." |

---

## MCP SDK Compatible Schema

```json
{
  "name": "list_tasks",
  "description": "User ke saare ya filtered tasks ki list return karta hai.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "Current logged-in user ka ID"
      },
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "default": "all",
        "description": "Filter: 'all', 'pending', ya 'completed'"
      }
    },
    "required": ["user_id"],
    "additionalProperties": false
  }
}
```

---

## Code Snippets

### 1. SQLModel Query (`skills/list_tasks.py`)

```python
from sqlmodel import Session, select
from app.models import Task

def list_tasks_query(session: Session, user_id: str, status: str = "all"):
    """
    Tasks fetch karne ka SQLModel query.

    Step 1: Base query with user_id filter (OWNERSHIP)
    Step 2: Apply status filter
    Step 3: Order by created_at descending
    """

    # Step 1: Base query - OWNERSHIP ensure karo
    query = select(Task).where(Task.user_id == user_id)

    # Step 2: Status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)
    # "all" = no additional filter

    # Step 3: Order by (naya task pehle)
    query = query.order_by(Task.created_at.desc())

    # Execute and return
    return session.exec(query).all()
```

### 2. FastAPI Endpoint (`app/routers/mcp.py`)

```python
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Literal

from app.database import get_session
from app.auth import get_current_user_id
from skills.list_tasks import list_tasks_async, ListTasksOutput

router = APIRouter(prefix="/api/mcp", tags=["mcp-skills"])

@router.get("/skills/list_tasks", response_model=ListTasksOutput)
async def mcp_list_tasks(
    status: Literal["all", "pending", "completed"] = Query(
        default="all",
        description="Filter: all, pending, completed"
    ),
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ListTasksOutput:
    """
    MCP Skill: list_tasks

    User ke tasks return karta hai with optional filter.
    user_id JWT token se automatically milta hai.
    """
    return await list_tasks_async(
        user_id=current_user_id,
        status=status,
        session=session
    )
```

### 3. Curl Test Commands

```bash
# Login karke token lo
TOKEN=$(curl -s -X POST "https://your-api.railway.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.token')

# All tasks
curl -X GET "https://your-api.railway.app/api/tasks" \
  -H "Authorization: Bearer $TOKEN"

# Pending tasks only
curl -X GET "https://your-api.railway.app/api/tasks?status=pending" \
  -H "Authorization: Bearer $TOKEN"

# Completed tasks only
curl -X GET "https://your-api.railway.app/api/tasks?status=completed" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Frontend Integration (TypeScript)

```typescript
// lib/mcp-skills.ts
import { getAuthToken } from './auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

interface TaskItem {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

interface ListTasksOutput {
  tasks: TaskItem[];
  total: number;
  status_filter: string;
  message: string;
}

type TaskStatus = 'all' | 'pending' | 'completed';

export async function listTasks(status: TaskStatus = 'all'): Promise<ListTasksOutput> {
  const token = getAuthToken();

  const response = await fetch(
    `${API_BASE}/api/tasks?status=${status}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );

  const data = await response.json();

  // Transform API response to match skill output
  return {
    tasks: data.tasks || [],
    total: data.total || 0,
    status_filter: status,
    message: data.tasks?.length
      ? `${data.tasks.length} tasks mile.`
      : 'Koi task nahi mila.'
  };
}

// Usage Examples
const allTasks = await listTasks('all');
const pendingTasks = await listTasks('pending');
const completedTasks = await listTasks('completed');

console.log(pendingTasks.message); // "5 pending tasks mile."
```

---

## AI Response Templates

Jab AI tasks list kare, yeh templates use kar sakta hai:

### Template 1: Tasks Found
```
Aapke {total} {status} tasks hain:

1. 📋 {title} - {description}
2. 📋 {title} - {description}
...

Koi task complete karna hai ya naya add karna hai?
```

### Template 2: No Tasks
```
Aapke koi {status} tasks nahi hain abhi.

{status == "pending" ? "Sab kaam ho gaya! 🎉" : "Naya task add karein?"}
```

### Template 3: Error
```
Tasks load nahi ho sake. {error_message}

Dobara try karein ya login check karein.
```

---

## Error Codes

| Error | HTTP Code | Message |
|-------|-----------|---------|
| No token | 401 | "Pehle login karein" |
| Token expired | 401 | "Session expire ho gaya" |
| User not found | 400 | "User verify nahi ho saka" |
| Invalid status | 422 | "Invalid status filter" |
| DB error | 500 | "Tasks fetch nahi ho sake" |

---

## File Location

```
backend/
├── skills/
│   ├── __init__.py
│   ├── add_task.py
│   ├── add_task.md
│   ├── list_tasks.py     ← Main implementation
│   └── list_tasks.md     ← This documentation
├── app/
│   ├── models.py
│   └── routers/
│       ├── tasks.py      ← Existing tasks endpoint
│       └── mcp.py        ← MCP skills endpoint
```

---

## Related Skills

- [`add_task`](./add_task.md) - Naya task create karna
- [`complete_task`](./complete_task.md) - Task complete karna
- [`delete_task`](./delete_task.md) - Task delete karna
- [`update_task`](./update_task.md) - Task update karna

---

> **Last Updated**: 2026-01-14
> **Maintainer**: Todo App Phase 3 Team
