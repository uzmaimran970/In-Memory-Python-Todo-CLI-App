# MCP Skills Documentation - Todo App

> Phase 3: AI-Powered Todo Management Skills
>
> Yeh file frontend ChatKit aur AI agents ke liye hai. Har skill ka detail neeche diya gaya hai.

---

## Table of Contents

1. [add_task](#1-add_task)
2. [list_tasks](#2-list_tasks)
3. [complete_task](#3-complete_task)
4. [delete_task](#4-delete_task)
5. [update_task](#5-update_task)

---

## 1. add_task

- **Skill Name**: `add_task`

- **Purpose**: User ke natural language se naya task create karna aur Neon DB mein save karna.

- **Parameters**:
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `user_id` | string | Yes | Current user ka ID (Better Auth se milega) |
  | `title` | string | Yes | Task ka title (1-200 characters) |
  | `description` | string | No | Task ki detail (max 1000 characters) |

- **Returns**:
  | Field | Type | Description |
  |-------|------|-------------|
  | `task_id` | integer | Naye task ka auto-generated ID |
  | `status` | string | "created" ya "error" |
  | `title` | string | Jo title diya tha |
  | `message` | string | Success ya error message |

- **Example User Message**:
  ```
  "Mujhe kal grocery leni hai, yaad dila dena"
  "Add task: Complete project report by Friday"
  "Naya kaam: Meeting schedule karna hai boss ke saath"
  ```

- **Example Tool Call**:
  ```json
  {
    "tool": "add_task",
    "arguments": {
      "user_id": "user_abc123",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread, butter"
    }
  }
  ```

- **Example Output**:
  ```json
  {
    "task_id": 5,
    "status": "created",
    "title": "Buy groceries",
    "message": "Task 'Buy groceries' successfully add ho gaya!"
  }
  ```

- **Behavior**:
  - AI pehle user message se title extract karega
  - Agar description bhi hai to wo bhi include karega
  - user_id automatically JWT token se milega
  - Success pe confirmation message dikhao
  - Error pe friendly message dikhao (e.g., "Task add nahi ho saka")

---

## 2. list_tasks

- **Skill Name**: `list_tasks`

- **Purpose**: User ke saare tasks ya filtered tasks Neon DB se fetch karke dikhana.

- **Parameters**:
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `user_id` | string | Yes | Current user ka ID |
  | `status_filter` | string | No | "all" (default), "pending", ya "completed" |
  | `sort_by` | string | No | "created" (default), "title", ya "updated" |
  | `limit` | integer | No | Kitne tasks dikhane hain (default: 50) |

- **Returns**:
  | Field | Type | Description |
  |-------|------|-------------|
  | `tasks` | array | Task objects ki list |
  | `total` | integer | Total tasks count |
  | `status_filter` | string | Applied filter |
  | `sort_by` | string | Applied sorting |

- **Example User Message**:
  ```
  "Mere saare tasks dikhao"
  "Pending kaam kya kya hai?"
  "Completed tasks ki list do"
  "Meri todo list dikhao"
  ```

- **Example Tool Call**:
  ```json
  {
    "tool": "list_tasks",
    "arguments": {
      "user_id": "user_abc123",
      "status_filter": "pending",
      "sort_by": "created"
    }
  }
  ```

- **Example Output**:
  ```json
  {
    "tasks": [
      {
        "id": 5,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "is_completed": false,
        "created_at": "2026-01-14T10:00:00Z"
      },
      {
        "id": 6,
        "title": "Call mom",
        "description": null,
        "is_completed": false,
        "created_at": "2026-01-14T11:00:00Z"
      }
    ],
    "total": 2,
    "status_filter": "pending",
    "sort_by": "created"
  }
  ```

- **Behavior**:
  - Default mein saare tasks dikhao (status_filter: "all")
  - User "pending" bole to sirf incomplete tasks
  - User "completed" bole to sirf complete tasks
  - Newest tasks pehle dikhao (default sorting)
  - Agar koi task nahi hai to friendly message: "Koi task nahi mila"

---

## 3. complete_task

- **Skill Name**: `complete_task`

- **Purpose**: Task ko complete ya incomplete mark karna (toggle).

- **Parameters**:
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `user_id` | string | Yes | Current user ka ID |
  | `task_id` | integer | Yes | Task ka ID jo complete karna hai |

- **Returns**:
  | Field | Type | Description |
  |-------|------|-------------|
  | `task_id` | integer | Task ka ID |
  | `title` | string | Task ka title |
  | `is_completed` | boolean | New completion status |
  | `status` | string | "updated" ya "error" |
  | `message` | string | Confirmation message |

- **Example User Message**:
  ```
  "Task 5 complete ho gaya"
  "Grocery wala kaam done hai"
  "Mark task 3 as complete"
  "Pehla task finish ho gaya"
  ```

- **Example Tool Call**:
  ```json
  {
    "tool": "complete_task",
    "arguments": {
      "user_id": "user_abc123",
      "task_id": 5
    }
  }
  ```

- **Example Output**:
  ```json
  {
    "task_id": 5,
    "title": "Buy groceries",
    "is_completed": true,
    "status": "updated",
    "message": "Task 'Buy groceries' complete mark ho gaya! Shabash!"
  }
  ```

- **Behavior**:
  - Yeh toggle hai: complete → incomplete, incomplete → complete
  - Pehle verify karo ke task user ka hai (ownership check)
  - Task nahi mila to error: "Task nahi mila"
  - Doosre user ka task to error: "Yeh task aapka nahi hai"
  - Success pe motivational message do

---

## 4. delete_task

- **Skill Name**: `delete_task`

- **Purpose**: Task ko permanently delete karna database se.

- **Parameters**:
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `user_id` | string | Yes | Current user ka ID |
  | `task_id` | integer | Yes | Task ka ID jo delete karna hai |

- **Returns**:
  | Field | Type | Description |
  |-------|------|-------------|
  | `task_id` | integer | Deleted task ka ID |
  | `status` | string | "deleted" ya "error" |
  | `message` | string | Confirmation message |

- **Example User Message**:
  ```
  "Task 5 delete kar do"
  "Grocery wala task hata do"
  "Remove task number 3"
  "Yeh kaam cancel hai, delete karo"
  ```

- **Example Tool Call**:
  ```json
  {
    "tool": "delete_task",
    "arguments": {
      "user_id": "user_abc123",
      "task_id": 5
    }
  }
  ```

- **Example Output**:
  ```json
  {
    "task_id": 5,
    "status": "deleted",
    "message": "Task 'Buy groceries' delete ho gaya!"
  }
  ```

- **Behavior**:
  - DELETE permanent hai, undo nahi ho sakta
  - Pehle ownership verify karo
  - Task nahi mila to: "Task nahi mila, shayad pehle se delete hai"
  - Doosre user ka task to: "Yeh task aapka nahi hai"
  - Success pe confirmation do

---

## 5. update_task

- **Skill Name**: `update_task`

- **Purpose**: Task ka title ya description update karna.

- **Parameters**:
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `user_id` | string | Yes | Current user ka ID |
  | `task_id` | integer | Yes | Task ka ID jo update karna hai |
  | `title` | string | No | Naya title (agar change karna hai) |
  | `description` | string | No | Nayi description (agar change karni hai) |

- **Returns**:
  | Field | Type | Description |
  |-------|------|-------------|
  | `task_id` | integer | Updated task ka ID |
  | `title` | string | Updated title |
  | `description` | string | Updated description |
  | `status` | string | "updated" ya "error" |
  | `message` | string | Confirmation message |

- **Example User Message**:
  ```
  "Task 5 ka title change karo 'Buy vegetables'"
  "Grocery task mein bread bhi add karo description mein"
  "Update task 3: Meeting 3pm pe hai"
  "Pehle task ko rename karo"
  ```

- **Example Tool Call**:
  ```json
  {
    "tool": "update_task",
    "arguments": {
      "user_id": "user_abc123",
      "task_id": 5,
      "title": "Buy vegetables and groceries",
      "description": "Milk, eggs, bread, tomatoes, onions"
    }
  }
  ```

- **Example Output**:
  ```json
  {
    "task_id": 5,
    "title": "Buy vegetables and groceries",
    "description": "Milk, eggs, bread, tomatoes, onions",
    "status": "updated",
    "message": "Task update ho gaya!"
  }
  ```

- **Behavior**:
  - Sirf wo fields update karo jo user ne diye
  - Title nahi diya to purana title rahega
  - Description nahi di to purani rahegi
  - Ownership verify karo pehle
  - updated_at timestamp automatically update hoga

---

## API Endpoints Summary

| Skill | HTTP Method | Endpoint | Auth Required |
|-------|-------------|----------|---------------|
| add_task | POST | `/api/mcp/tools/add_task` | Yes (JWT) |
| list_tasks | GET | `/api/tasks` | Yes (JWT) |
| complete_task | PATCH | `/api/tasks/{id}/complete` | Yes (JWT) |
| delete_task | DELETE | `/api/tasks/{id}` | Yes (JWT) |
| update_task | PUT | `/api/tasks/{id}` | Yes (JWT) |

---

## Error Handling

Har skill ke liye common errors:

| Error | Status Code | Message |
|-------|-------------|---------|
| Token missing | 401 | "Pehle login karein" |
| Token expired | 401 | "Session expire ho gaya, dobara login karein" |
| Task not found | 404 | "Task nahi mila" |
| Not authorized | 403 | "Yeh task aapka nahi hai" |
| Validation error | 400 | "Title dena zaroori hai" |
| Server error | 500 | "Kuch gadbad ho gayi, thodi der baad try karein" |

---

## Natural Language Patterns

AI ko yeh patterns samajhne chahiye:

### Adding Tasks
- "Add task: [title]"
- "Naya kaam: [title]"
- "Mujhe [task] karna hai"
- "[task] yaad dila dena"
- "Todo add karo: [title]"

### Listing Tasks
- "Mere tasks dikhao"
- "Kya kya karna hai?"
- "Todo list"
- "Pending kaam"
- "Completed tasks"

### Completing Tasks
- "Task [id/title] done"
- "[task] complete ho gaya"
- "Mark [id] complete"
- "[task] finish"

### Deleting Tasks
- "Delete task [id]"
- "[task] hata do"
- "Remove [id]"
- "Cancel karo [task]"

### Updating Tasks
- "Update task [id]: [new info]"
- "[task] ka title change karo"
- "[id] mein [changes] add karo"

---

## Usage with ChatKit

```typescript
// Frontend mein skill call karne ka example
import { api } from '@/lib/api';

// Add Task
const result = await api.createTask({
  title: "Buy groceries",
  description: "Milk, eggs, bread"
});

// List Tasks
const tasks = await api.getTasks();

// Complete Task
const updated = await api.toggleTask(taskId);

// Delete Task
await api.deleteTask(taskId);

// Update Task
const updatedTask = await api.updateTask(taskId, {
  title: "New title",
  description: "New description"
});
```

---

## Version Info

- **Document Version**: 1.0.0
- **Last Updated**: 2026-01-14
- **Phase**: 3 (AI-Powered Features)
- **Compatible With**: FastAPI Backend v1.0.0, Next.js Frontend v16+

---

> **Note**: Saare skills JWT authentication require karte hain. User ko pehle login hona zaroori hai.
