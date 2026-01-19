"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        MCP SKILL: delete_task                                ║
║══════════════════════════════════════════════════════════════════════════════║
║  Purpose:  Kisi task ko permanently delete karna                             ║
║                                                                              ║
║  Author:   Todo App Phase 3                                                  ║
║  Version:  1.0.0                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

STEP BY STEP GUIDE (Roman Urdu):
================================

Step 1: User Message Samjho
---------------------------
Jab user kuch aisa bole:
- "Task 2 delete kar do"
- "Grocery wala task hata do"
- "Remove task number 3"
- "Yeh kaam cancel hai, delete karo"

AI ko samajhna hai ke task delete karna hai.

Step 2: Parameters Extract Karo
-------------------------------
User message se yeh cheezein nikalo:
- task_id: Kaunsa task delete karna hai
- user_id: JWT token se automatically milega

Step 3: Ownership Verify Karo
-----------------------------
Check karo ke:
- Task exist karta hai
- Task us hi user ka hai (ownership)

Step 4: Task Delete Karo
------------------------
- session.delete(task)
- session.commit()
- PERMANENT hai - undo nahi ho sakta!

Step 5: Response Return Karo
----------------------------
Success pe: confirmation message
Error pe: friendly error message

⚠️ WARNING: Delete permanent hai!

"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field
from typing import Optional
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
DELETE_TASK_SCHEMA = {
    "name": "delete_task",
    "description": (
        "Kisi task ko permanently delete karta hai. "
        "⚠️ WARNING: Yeh action undo nahi ho sakta! "
        "Sirf logged-in user apna task delete kar sakta hai."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Current logged-in user ka ID (Better Auth se)"
            },
            "task_id": {
                "type": "integer",
                "description": "Task ka ID jo delete karna hai"
            }
        },
        "required": ["user_id", "task_id"],
        "additionalProperties": False
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "Deleted task ka ID"
            },
            "status": {
                "type": "string",
                "enum": ["deleted", "error"],
                "description": "Operation ka status"
            },
            "title": {
                "type": "string",
                "description": "Deleted task ka title"
            },
            "message": {
                "type": "string",
                "description": "Success/error message (Roman Urdu mein)"
            }
        },
        "required": ["task_id", "status", "title", "message"]
    }
}


# ============================================================================
# INPUT MODEL (Pydantic)
# ============================================================================
class DeleteTaskInput(BaseModel):
    """
    delete_task skill ke input parameters.

    Attributes:
        user_id: Current logged-in user ka ID (required)
        task_id: Task ka ID jo delete karna hai (required)

    Example:
        ```python
        input_data = DeleteTaskInput(
            user_id="user_abc123",
            task_id=2
        )
        ```
    """
    user_id: str = Field(
        ...,
        min_length=1,
        description="Current logged-in user ka ID"
    )
    task_id: int = Field(
        ...,
        gt=0,
        description="Task ka ID jo delete karna hai"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "task_id": 2
            }
        }


# ============================================================================
# OUTPUT MODEL (Pydantic)
# ============================================================================
class DeleteTaskOutput(BaseModel):
    """
    delete_task skill ka output/response.

    Attributes:
        task_id: Deleted task ka ID
        status: "deleted" ya "error"
        title: Deleted task ka title
        message: Success/error message (Roman Urdu mein)

    Example Success:
        ```json
        {
            "task_id": 2,
            "status": "deleted",
            "title": "Old task",
            "message": "Task 'Old task' delete ho gaya."
        }
        ```

    Example Error:
        ```json
        {
            "task_id": 2,
            "status": "error",
            "title": "",
            "message": "Task nahi mila. Shayad pehle se delete hai."
        }
        ```
    """
    task_id: int = Field(
        description="Deleted task ka ID"
    )
    status: str = Field(
        description="'deleted' ya 'error'"
    )
    title: str = Field(
        default="",
        description="Deleted task ka title"
    )
    message: str = Field(
        description="Success/error message (Roman Urdu mein)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 2,
                "status": "deleted",
                "title": "Old task",
                "message": "Task 'Old task' delete ho gaya."
            }
        }


# ============================================================================
# MAIN SKILL FUNCTION
# ============================================================================
def delete_task(input_data: DeleteTaskInput) -> DeleteTaskOutput:
    """
    MCP Skill: delete_task

    Task ko permanently delete karta hai.

    ⚠️ WARNING: Yeh action UNDO nahi ho sakta!

    STEP BY STEP PROCESS:
    ---------------------
    1. Input validation
    2. Task find karo by task_id
    3. Ownership verify karo (user_id match)
    4. Task delete karo (session.delete)
    5. Success/Error response return karo

    Args:
        input_data: DeleteTaskInput with user_id and task_id

    Returns:
        DeleteTaskOutput: task_id, status, title, message

    Example:
        ```python
        # Input
        input_data = DeleteTaskInput(
            user_id="user_abc123",
            task_id=2
        )

        # Call skill
        result = delete_task(input_data)

        # Output
        print(result.status)   # "deleted"
        print(result.message)  # "Task 'Old task' delete ho gaya."
        ```
    """

    # -------------------------------------------------------------------------
    # Step 1: Database Connection
    # -------------------------------------------------------------------------
    try:
        if engine is None:
            return DeleteTaskOutput(
                task_id=input_data.task_id,
                status="error",
                title="",
                message="Database connection nahi hai. Server restart karein."
            )

        with Session(engine) as session:

            # -----------------------------------------------------------------
            # Step 2: Task Find Karo
            # -----------------------------------------------------------------
            task = session.get(Task, input_data.task_id)

            if not task:
                return DeleteTaskOutput(
                    task_id=input_data.task_id,
                    status="error",
                    title="",
                    message="Task nahi mila. Shayad pehle se delete hai."
                )

            # -----------------------------------------------------------------
            # Step 3: Ownership Verify Karo
            # -----------------------------------------------------------------
            if task.user_id != input_data.user_id:
                return DeleteTaskOutput(
                    task_id=input_data.task_id,
                    status="error",
                    title="",
                    message="Yeh task aapka nahi hai. Sirf apna task delete kar sakte hain."
                )

            # -----------------------------------------------------------------
            # Step 4: Store Title Before Delete
            # -----------------------------------------------------------------
            deleted_title = task.title

            # -----------------------------------------------------------------
            # Step 5: Task Delete Karo (PERMANENT!)
            # -----------------------------------------------------------------
            session.delete(task)
            session.commit()

            # -----------------------------------------------------------------
            # Step 6: Success Response
            # -----------------------------------------------------------------
            return DeleteTaskOutput(
                task_id=input_data.task_id,
                status="deleted",
                title=deleted_title,
                message=f"Task '{deleted_title}' delete ho gaya."
            )

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------
    except Exception as e:
        return DeleteTaskOutput(
            task_id=input_data.task_id,
            status="error",
            title="",
            message=f"Task delete nahi ho saka. Error: {str(e)[:50]}"
        )


# ============================================================================
# ASYNC VERSION (FastAPI ke liye)
# ============================================================================
async def delete_task_async(
    user_id: str,
    task_id: int,
    session: Session = None
) -> DeleteTaskOutput:
    """
    Async version of delete_task skill for FastAPI endpoints.

    ⚠️ WARNING: Delete PERMANENT hai!

    Args:
        user_id: Current logged-in user ka ID
        task_id: Task ka ID jo delete karna hai
        session: SQLModel Session (injected via Depends)

    Returns:
        DeleteTaskOutput: task_id, status, title, message
    """
    try:
        # Task find karo
        task = session.get(Task, task_id)

        if not task:
            return DeleteTaskOutput(
                task_id=task_id,
                status="error",
                title="",
                message="Task nahi mila. Shayad pehle se delete hai."
            )

        # Ownership check
        if task.user_id != user_id:
            return DeleteTaskOutput(
                task_id=task_id,
                status="error",
                title="",
                message="Yeh task aapka nahi hai. Sirf apna task delete kar sakte hain."
            )

        # Store title before delete
        deleted_title = task.title

        # Delete karo (PERMANENT!)
        session.delete(task)
        session.commit()

        return DeleteTaskOutput(
            task_id=task_id,
            status="deleted",
            title=deleted_title,
            message=f"Task '{deleted_title}' delete ho gaya."
        )

    except Exception as e:
        return DeleteTaskOutput(
            task_id=task_id,
            status="error",
            title="",
            message=f"Task delete nahi ho saka. Error: {str(e)[:50]}"
        )


# ============================================================================
# SOFT DELETE VERSION (Optional - for future use)
# ============================================================================
async def soft_delete_task_async(
    user_id: str,
    task_id: int,
    session: Session = None
) -> DeleteTaskOutput:
    """
    Soft delete - Task ko actually delete nahi karta,
    sirf is_deleted = True mark karta hai.

    Note: Yeh feature abhi implement nahi hai Task model mein.
    Future mein add kar sakte hain agar undo feature chahiye.

    Args:
        user_id: Current logged-in user ka ID
        task_id: Task ka ID
        session: SQLModel Session

    Returns:
        DeleteTaskOutput: Status with message
    """
    # For now, use hard delete
    return await delete_task_async(user_id, task_id, session)


# ============================================================================
# MCP TOOL HANDLER (for MCP Server)
# ============================================================================
def handle_delete_task_tool(arguments: dict) -> dict:
    """
    MCP Server ke liye tool handler.

    Args:
        arguments: Dict with user_id and task_id

    Returns:
        Dict with task_id, status, title, message
    """
    try:
        input_data = DeleteTaskInput(
            user_id=arguments.get("user_id", ""),
            task_id=arguments.get("task_id", 0)
        )

        result = delete_task(input_data)

        return {
            "task_id": result.task_id,
            "status": result.status,
            "title": result.title,
            "message": result.message
        }

    except Exception as e:
        return {
            "task_id": arguments.get("task_id", 0),
            "status": "error",
            "title": "",
            "message": f"Skill execution failed: {str(e)}"
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_skill_schema() -> dict:
    """Return MCP compatible schema for this skill."""
    return DELETE_TASK_SCHEMA


def get_skill_info() -> dict:
    """Return skill metadata."""
    return {
        "name": "delete_task",
        "version": "1.0.0",
        "description": "Task ko permanently delete karta hai (UNDO nahi ho sakta!)",
        "author": "Todo App Phase 3",
        "parameters": ["user_id (required)", "task_id (required)"],
        "returns": ["task_id", "status", "title", "message"],
        "warning": "⚠️ Delete action is PERMANENT and cannot be undone!"
    }


# ============================================================================
# TESTING / STANDALONE EXECUTION
# ============================================================================
if __name__ == "__main__":
    import json

    print("=" * 60)
    print("MCP SKILL: delete_task - Test Mode")
    print("=" * 60)
    print("\n⚠️  WARNING: Delete is PERMANENT and cannot be undone!")

    print("\n📋 MCP Schema:")
    print(json.dumps(DELETE_TASK_SCHEMA, indent=2))

    print("\n📌 Skill Info:")
    print(json.dumps(get_skill_info(), indent=2))

    print("\n🧪 Test Input Example:")
    test_input = {"user_id": "user123", "task_id": 2}
    print(json.dumps(test_input, indent=2))

    print("\n✅ Expected Output (Success):")
    success_output = {
        "task_id": 2,
        "status": "deleted",
        "title": "Old task",
        "message": "Task 'Old task' delete ho gaya."
    }
    print(json.dumps(success_output, indent=2))

    print("\n❌ Expected Output (Error - Not Found):")
    error_output = {
        "task_id": 2,
        "status": "error",
        "title": "",
        "message": "Task nahi mila. Shayad pehle se delete hai."
    }
    print(json.dumps(error_output, indent=2))

    print("\n" + "=" * 60)
