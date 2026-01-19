"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        MCP SKILL: list_tasks                                 ║
║══════════════════════════════════════════════════════════════════════════════║
║  Purpose:  User ke saare ya filtered tasks ki list return karna              ║
║            (all, pending, completed)                                         ║
║                                                                              ║
║  Author:   Todo App Phase 3                                                  ║
║  Version:  1.0.0                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

STEP BY STEP GUIDE (Roman Urdu):
================================

Step 1: User Message Samjho
---------------------------
Jab user kuch aisa bole:
- "Mere saare tasks dikhao"
- "Pending kaam kya kya hai?"
- "Completed tasks ki list do"
- "Meri todo list"

AI ko samajhna hai ke tasks list karna hai.

Step 2: Parameters Extract Karo
-------------------------------
User message se yeh cheezein nikalo:
- status: "all", "pending", ya "completed"
- user_id: JWT token se automatically milega

Step 3: Database Query Banao
----------------------------
SQLModel use karke:
- Base query: Task.user_id == current_user_id
- Agar status = "pending": completed == False
- Agar status = "completed": completed == True
- Order by created_at descending

Step 4: Response Return Karo
----------------------------
Tasks array return karo with count
Agar koi task nahi: empty array + friendly message

"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from sqlmodel import Session, select
import sys
import os

# App imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.models import Task, User
    from app.database import engine
except ImportError:
    Task = None
    User = None
    engine = None


# ============================================================================
# MCP SDK COMPATIBLE SCHEMA
# ============================================================================
LIST_TASKS_SCHEMA = {
    "name": "list_tasks",
    "description": (
        "User ke saare ya filtered tasks ki list return karta hai. "
        "Status filter: 'all' (default), 'pending', ya 'completed'. "
        "Sirf logged-in user apne tasks dekh sakta hai."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Current logged-in user ka ID (Better Auth se)"
            },
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "default": "all",
                "description": "Filter: 'all' (default), 'pending', ya 'completed'"
            }
        },
        "required": ["user_id"],
        "additionalProperties": False
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "completed": {"type": "boolean"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                },
                "description": "Tasks ki array"
            },
            "total": {
                "type": "integer",
                "description": "Total tasks count"
            },
            "status_filter": {
                "type": "string",
                "description": "Applied filter"
            },
            "message": {
                "type": "string",
                "description": "Response message (Roman Urdu)"
            }
        },
        "required": ["tasks", "total", "status_filter", "message"]
    }
}


# ============================================================================
# INPUT MODEL (Pydantic)
# ============================================================================
class ListTasksInput(BaseModel):
    """
    list_tasks skill ke input parameters.

    Attributes:
        user_id: Current logged-in user ka ID (required)
        status: Filter - "all", "pending", ya "completed" (default: "all")

    Example:
        ```python
        input_data = ListTasksInput(
            user_id="user_abc123",
            status="pending"
        )
        ```
    """
    user_id: str = Field(
        ...,
        min_length=1,
        description="Current logged-in user ka ID"
    )
    status: Literal["all", "pending", "completed"] = Field(
        default="all",
        description="Filter: 'all', 'pending', ya 'completed'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "status": "pending"
            }
        }


# ============================================================================
# TASK ITEM MODEL
# ============================================================================
class TaskItem(BaseModel):
    """Single task item in the list."""
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-01-14T10:00:00",
                "updated_at": "2026-01-14T10:00:00"
            }
        }


# ============================================================================
# OUTPUT MODEL (Pydantic)
# ============================================================================
class ListTasksOutput(BaseModel):
    """
    list_tasks skill ka output/response.

    Attributes:
        tasks: Tasks ki array
        total: Total tasks count
        status_filter: Applied filter
        message: Response message (Roman Urdu)

    Example:
        ```json
        {
            "tasks": [
                {"id": 1, "title": "Buy groceries", "completed": false, ...}
            ],
            "total": 1,
            "status_filter": "pending",
            "message": "1 pending task mila."
        }
        ```
    """
    tasks: List[TaskItem] = Field(
        default=[],
        description="Tasks ki array"
    )
    total: int = Field(
        default=0,
        description="Total tasks count"
    )
    status_filter: str = Field(
        default="all",
        description="Applied filter"
    )
    message: str = Field(
        description="Response message (Roman Urdu)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2026-01-14T10:00:00",
                        "updated_at": "2026-01-14T10:00:00"
                    }
                ],
                "total": 1,
                "status_filter": "pending",
                "message": "1 pending task mila."
            }
        }


# ============================================================================
# MAIN SKILL FUNCTION
# ============================================================================
def list_tasks(input_data: ListTasksInput) -> ListTasksOutput:
    """
    MCP Skill: list_tasks

    User ke saare ya filtered tasks return karta hai.

    STEP BY STEP PROCESS:
    ---------------------
    1. Input validation (user_id required)
    2. User existence check
    3. Build SQLModel query with filters
    4. Execute query and fetch results
    5. Format and return response

    Args:
        input_data: ListTasksInput with user_id and optional status filter

    Returns:
        ListTasksOutput: tasks array, total count, filter applied, message

    Example:
        ```python
        # Input
        input_data = ListTasksInput(
            user_id="user_abc123",
            status="pending"
        )

        # Call skill
        result = list_tasks(input_data)

        # Output
        print(result.total)    # 5
        print(result.tasks)    # [TaskItem(...), ...]
        print(result.message)  # "5 pending tasks mile."
        ```
    """

    # -------------------------------------------------------------------------
    # Step 1: Database Connection
    # -------------------------------------------------------------------------
    try:
        if engine is None:
            return ListTasksOutput(
                tasks=[],
                total=0,
                status_filter=input_data.status,
                message="Database connection nahi hai. Server restart karein."
            )

        with Session(engine) as session:

            # -----------------------------------------------------------------
            # Step 2: User Verification
            # -----------------------------------------------------------------
            user = session.exec(
                select(User).where(User.id == input_data.user_id)
            ).first()

            if not user:
                return ListTasksOutput(
                    tasks=[],
                    total=0,
                    status_filter=input_data.status,
                    message="User verify nahi ho saka. Pehle login karein."
                )

            # -----------------------------------------------------------------
            # Step 3: Build Query with Filters
            # -----------------------------------------------------------------
            # Base query: Filter by user_id (OWNERSHIP)
            query = select(Task).where(Task.user_id == input_data.user_id)

            # Apply status filter
            if input_data.status == "pending":
                query = query.where(Task.completed == False)
            elif input_data.status == "completed":
                query = query.where(Task.completed == True)
            # "all" = no additional filter

            # Order by created_at descending (naya task pehle)
            query = query.order_by(Task.created_at.desc())

            # -----------------------------------------------------------------
            # Step 4: Execute Query
            # -----------------------------------------------------------------
            tasks_result = session.exec(query).all()

            # -----------------------------------------------------------------
            # Step 5: Format Response
            # -----------------------------------------------------------------
            task_items = [
                TaskItem(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    completed=task.completed,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )
                for task in tasks_result
            ]

            total = len(task_items)

            # Generate friendly message
            if total == 0:
                if input_data.status == "all":
                    message = "Koi task nahi mila. Naya task add karein!"
                elif input_data.status == "pending":
                    message = "Koi pending task nahi hai. Sab kaam ho gaya! 🎉"
                else:
                    message = "Koi completed task nahi hai abhi."
            else:
                status_text = {
                    "all": "",
                    "pending": "pending ",
                    "completed": "completed "
                }[input_data.status]

                if total == 1:
                    message = f"1 {status_text}task mila."
                else:
                    message = f"{total} {status_text}tasks mile."

            return ListTasksOutput(
                tasks=task_items,
                total=total,
                status_filter=input_data.status,
                message=message
            )

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------
    except Exception as e:
        return ListTasksOutput(
            tasks=[],
            total=0,
            status_filter=input_data.status,
            message=f"Tasks fetch nahi ho sake. Error: {str(e)[:50]}"
        )


# ============================================================================
# ASYNC VERSION (FastAPI ke liye)
# ============================================================================
async def list_tasks_async(
    user_id: str,
    status: str = "all",
    session: Session = None
) -> ListTasksOutput:
    """
    Async version of list_tasks skill for FastAPI endpoints.

    Args:
        user_id: Current logged-in user ka ID
        status: "all", "pending", ya "completed"
        session: SQLModel Session (injected via Depends)

    Returns:
        ListTasksOutput: Tasks array with count and message
    """
    try:
        # User verification
        user = session.exec(
            select(User).where(User.id == user_id)
        ).first()

        if not user:
            return ListTasksOutput(
                tasks=[],
                total=0,
                status_filter=status,
                message="User verify nahi ho saka. Pehle login karein."
            )

        # Build query
        query = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        query = query.order_by(Task.created_at.desc())

        # Execute
        tasks_result = session.exec(query).all()

        # Format
        task_items = [
            TaskItem(
                id=task.id,
                title=task.title,
                description=task.description,
                completed=task.completed,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in tasks_result
        ]

        total = len(task_items)

        # Message
        if total == 0:
            if status == "pending":
                message = "Koi pending task nahi hai. Sab kaam ho gaya! 🎉"
            elif status == "completed":
                message = "Koi completed task nahi hai abhi."
            else:
                message = "Koi task nahi mila. Naya task add karein!"
        else:
            status_text = {"all": "", "pending": "pending ", "completed": "completed "}[status]
            message = f"{total} {status_text}task{'s' if total > 1 else ''} mil{'e' if total > 1 else 'a'}."

        return ListTasksOutput(
            tasks=task_items,
            total=total,
            status_filter=status,
            message=message
        )

    except Exception as e:
        return ListTasksOutput(
            tasks=[],
            total=0,
            status_filter=status,
            message=f"Tasks fetch nahi ho sake. Error: {str(e)[:50]}"
        )


# ============================================================================
# MCP TOOL HANDLER (for MCP Server)
# ============================================================================
def handle_list_tasks_tool(arguments: dict) -> dict:
    """
    MCP Server ke liye tool handler.

    Args:
        arguments: Dict with user_id and optional status

    Returns:
        Dict with tasks array, total, status_filter, message
    """
    try:
        input_data = ListTasksInput(
            user_id=arguments.get("user_id", ""),
            status=arguments.get("status", "all")
        )

        result = list_tasks(input_data)

        return {
            "tasks": [task.model_dump() for task in result.tasks],
            "total": result.total,
            "status_filter": result.status_filter,
            "message": result.message
        }

    except Exception as e:
        return {
            "tasks": [],
            "total": 0,
            "status_filter": arguments.get("status", "all"),
            "message": f"Skill execution failed: {str(e)}"
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_skill_schema() -> dict:
    """Return MCP compatible schema for this skill."""
    return LIST_TASKS_SCHEMA


def get_skill_info() -> dict:
    """Return skill metadata."""
    return {
        "name": "list_tasks",
        "version": "1.0.0",
        "description": "User ke tasks list karta hai with optional filter",
        "author": "Todo App Phase 3",
        "parameters": ["user_id (required)", "status (optional: all/pending/completed)"],
        "returns": ["tasks (array)", "total", "status_filter", "message"]
    }


# ============================================================================
# TESTING / STANDALONE EXECUTION
# ============================================================================
if __name__ == "__main__":
    import json

    print("=" * 60)
    print("MCP SKILL: list_tasks - Test Mode")
    print("=" * 60)

    print("\n📋 MCP Schema:")
    print(json.dumps(LIST_TASKS_SCHEMA, indent=2))

    print("\n📌 Skill Info:")
    print(json.dumps(get_skill_info(), indent=2))

    print("\n🧪 Test Input Examples:")
    examples = [
        {"user_id": "user123", "status": "all"},
        {"user_id": "user123", "status": "pending"},
        {"user_id": "user123", "status": "completed"}
    ]
    for ex in examples:
        print(f"  - {json.dumps(ex)}")

    print("\n" + "=" * 60)
