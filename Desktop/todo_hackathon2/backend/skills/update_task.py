"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        MCP SKILL: update_task                                ║
║══════════════════════════════════════════════════════════════════════════════║
║  Purpose:  Task ka title ya description edit karna                           ║
║                                                                              ║
║  Author:   Todo App Phase 3                                                  ║
║  Version:  1.0.0                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

STEP BY STEP GUIDE (Roman Urdu):
================================

Step 1: User Message Samjho
---------------------------
Jab user kuch aisa bole:
- "Task 1 ka title change karo 'Buy vegetables'"
- "Grocery task mein bread bhi add karo description mein"
- "Update task 3: Meeting 3pm pe hai"
- "Pehle task ko rename karo"

AI ko samajhna hai ke task update karna hai.

Step 2: Parameters Extract Karo
-------------------------------
User message se yeh cheezein nikalo:
- task_id: Kaunsa task update karna hai
- title: Naya title (agar diya ho)
- description: Nayi description (agar di ho)
- user_id: JWT token se automatically milega

Step 3: Ownership Verify Karo
-----------------------------
Check karo ke:
- Task exist karta hai
- Task us hi user ka hai (ownership)

Step 4: Task Update Karo
------------------------
- Sirf wo fields update karo jo diye hain
- Agar title nahi diya, purana rahega
- Agar description nahi di, purani rahegi
- updated_at = current UTC time

Step 5: Response Return Karo
----------------------------
Success pe: confirmation message with updated title
Error pe: friendly error message

"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field
from typing import Optional
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
UPDATE_TASK_SCHEMA = {
    "name": "update_task",
    "description": (
        "Task ka title ya description edit karta hai. "
        "Sirf di gayi fields update hoti hain, baaki same rehti hain. "
        "Sirf logged-in user apna task update kar sakta hai."
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
                "description": "Task ka ID jo update karna hai"
            },
            "title": {
                "type": "string",
                "description": "Naya title (optional - agar nahi diya to purana rahega)",
                "minLength": 1,
                "maxLength": 200
            },
            "description": {
                "type": "string",
                "description": "Nayi description (optional - agar nahi di to purani rahegi)",
                "maxLength": 1000
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
                "description": "Updated task ka ID"
            },
            "status": {
                "type": "string",
                "enum": ["updated", "error"],
                "description": "Operation ka status"
            },
            "title": {
                "type": "string",
                "description": "Updated title"
            },
            "description": {
                "type": "string",
                "description": "Updated description"
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
class UpdateTaskInput(BaseModel):
    """
    update_task skill ke input parameters.

    Attributes:
        user_id: Current logged-in user ka ID (required)
        task_id: Task ka ID jo update karna hai (required)
        title: Naya title (optional)
        description: Nayi description (optional)

    Example:
        ```python
        input_data = UpdateTaskInput(
            user_id="user_abc123",
            task_id=1,
            title="Buy groceries and fruits"
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
        description="Task ka ID jo update karna hai"
    )
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Naya title (optional)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Nayi description (optional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "task_id": 1,
                "title": "Buy groceries and fruits"
            }
        }


# ============================================================================
# OUTPUT MODEL (Pydantic)
# ============================================================================
class UpdateTaskOutput(BaseModel):
    """
    update_task skill ka output/response.

    Attributes:
        task_id: Updated task ka ID
        status: "updated" ya "error"
        title: Updated title
        description: Updated description
        message: Success/error message (Roman Urdu mein)

    Example Success:
        ```json
        {
            "task_id": 1,
            "status": "updated",
            "title": "Buy groceries and fruits",
            "description": "Milk, eggs, apples",
            "message": "Task update ho gaya!"
        }
        ```

    Example Error:
        ```json
        {
            "task_id": 1,
            "status": "error",
            "title": "",
            "description": "",
            "message": "Task nahi mila."
        }
        ```
    """
    task_id: int = Field(
        description="Updated task ka ID"
    )
    status: str = Field(
        description="'updated' ya 'error'"
    )
    title: str = Field(
        default="",
        description="Updated title"
    )
    description: Optional[str] = Field(
        default=None,
        description="Updated description"
    )
    message: str = Field(
        description="Success/error message (Roman Urdu mein)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "status": "updated",
                "title": "Buy groceries and fruits",
                "description": "Milk, eggs, apples",
                "message": "Task update ho gaya!"
            }
        }


# ============================================================================
# MAIN SKILL FUNCTION
# ============================================================================
def update_task(input_data: UpdateTaskInput) -> UpdateTaskOutput:
    """
    MCP Skill: update_task

    Task ka title ya description update karta hai.

    STEP BY STEP PROCESS:
    ---------------------
    1. Input validation
    2. Check ke kuch update karne ko hai
    3. Task find karo by task_id
    4. Ownership verify karo (user_id match)
    5. Sirf di gayi fields update karo
    6. updated_at update karo
    7. Success/Error response return karo

    Args:
        input_data: UpdateTaskInput with user_id, task_id, title, description

    Returns:
        UpdateTaskOutput: task_id, status, title, description, message

    Example:
        ```python
        # Input
        input_data = UpdateTaskInput(
            user_id="user_abc123",
            task_id=1,
            title="Buy groceries and fruits"
        )

        # Call skill
        result = update_task(input_data)

        # Output
        print(result.status)   # "updated"
        print(result.title)    # "Buy groceries and fruits"
        print(result.message)  # "Task title update ho gaya!"
        ```
    """

    # -------------------------------------------------------------------------
    # Step 1: Database Connection
    # -------------------------------------------------------------------------
    try:
        if engine is None:
            return UpdateTaskOutput(
                task_id=input_data.task_id,
                status="error",
                title="",
                description=None,
                message="Database connection nahi hai. Server restart karein."
            )

        # -----------------------------------------------------------------
        # Step 2: Check Ke Kuch Update Karne Ko Hai
        # -----------------------------------------------------------------
        if input_data.title is None and input_data.description is None:
            return UpdateTaskOutput(
                task_id=input_data.task_id,
                status="error",
                title="",
                description=None,
                message="Kuch update karne ko nahi hai. Title ya description dein."
            )

        with Session(engine) as session:

            # -----------------------------------------------------------------
            # Step 3: Task Find Karo
            # -----------------------------------------------------------------
            task = session.get(Task, input_data.task_id)

            if not task:
                return UpdateTaskOutput(
                    task_id=input_data.task_id,
                    status="error",
                    title="",
                    description=None,
                    message="Task nahi mila. Shayad delete ho gaya hai."
                )

            # -----------------------------------------------------------------
            # Step 4: Ownership Verify Karo
            # -----------------------------------------------------------------
            if task.user_id != input_data.user_id:
                return UpdateTaskOutput(
                    task_id=input_data.task_id,
                    status="error",
                    title="",
                    description=None,
                    message="Yeh task aapka nahi hai. Sirf apna task update kar sakte hain."
                )

            # -----------------------------------------------------------------
            # Step 5: Sirf Di Gayi Fields Update Karo
            # -----------------------------------------------------------------
            changes = []

            if input_data.title is not None:
                old_title = task.title
                task.title = input_data.title
                changes.append("title")

            if input_data.description is not None:
                task.description = input_data.description
                changes.append("description")

            # -----------------------------------------------------------------
            # Step 6: updated_at Update Karo
            # -----------------------------------------------------------------
            task.updated_at = datetime.utcnow()

            # Save to database
            session.add(task)
            session.commit()
            session.refresh(task)

            # -----------------------------------------------------------------
            # Step 7: Success Response
            # -----------------------------------------------------------------
            # Build message based on what was updated
            if len(changes) == 2:
                message = "Task title aur description dono update ho gaye!"
            elif "title" in changes:
                message = f"Task title update ho gaya!"
            else:
                message = "Task description update ho gayi!"

            return UpdateTaskOutput(
                task_id=task.id,
                status="updated",
                title=task.title,
                description=task.description,
                message=message
            )

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------
    except Exception as e:
        return UpdateTaskOutput(
            task_id=input_data.task_id,
            status="error",
            title="",
            description=None,
            message=f"Task update nahi ho saka. Error: {str(e)[:50]}"
        )


# ============================================================================
# ASYNC VERSION (FastAPI ke liye)
# ============================================================================
async def update_task_async(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    session: Session = None
) -> UpdateTaskOutput:
    """
    Async version of update_task skill for FastAPI endpoints.

    Args:
        user_id: Current logged-in user ka ID
        task_id: Task ka ID jo update karna hai
        title: Naya title (optional)
        description: Nayi description (optional)
        session: SQLModel Session (injected via Depends)

    Returns:
        UpdateTaskOutput: task_id, status, title, description, message
    """
    try:
        # Check ke kuch update karne ko hai
        if title is None and description is None:
            return UpdateTaskOutput(
                task_id=task_id,
                status="error",
                title="",
                description=None,
                message="Kuch update karne ko nahi hai. Title ya description dein."
            )

        # Task find karo
        task = session.get(Task, task_id)

        if not task:
            return UpdateTaskOutput(
                task_id=task_id,
                status="error",
                title="",
                description=None,
                message="Task nahi mila. Shayad delete ho gaya hai."
            )

        # Ownership check
        if task.user_id != user_id:
            return UpdateTaskOutput(
                task_id=task_id,
                status="error",
                title="",
                description=None,
                message="Yeh task aapka nahi hai. Sirf apna task update kar sakte hain."
            )

        # Update fields
        changes = []

        if title is not None:
            task.title = title
            changes.append("title")

        if description is not None:
            task.description = description
            changes.append("description")

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

        return UpdateTaskOutput(
            task_id=task.id,
            status="updated",
            title=task.title,
            description=task.description,
            message=message
        )

    except Exception as e:
        return UpdateTaskOutput(
            task_id=task_id,
            status="error",
            title="",
            description=None,
            message=f"Task update nahi ho saka. Error: {str(e)[:50]}"
        )


# ============================================================================
# MCP TOOL HANDLER (for MCP Server)
# ============================================================================
def handle_update_task_tool(arguments: dict) -> dict:
    """
    MCP Server ke liye tool handler.

    Args:
        arguments: Dict with user_id, task_id, title, description

    Returns:
        Dict with task_id, status, title, description, message
    """
    try:
        input_data = UpdateTaskInput(
            user_id=arguments.get("user_id", ""),
            task_id=arguments.get("task_id", 0),
            title=arguments.get("title"),
            description=arguments.get("description")
        )

        result = update_task(input_data)

        return {
            "task_id": result.task_id,
            "status": result.status,
            "title": result.title,
            "description": result.description,
            "message": result.message
        }

    except Exception as e:
        return {
            "task_id": arguments.get("task_id", 0),
            "status": "error",
            "title": "",
            "description": None,
            "message": f"Skill execution failed: {str(e)}"
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_skill_schema() -> dict:
    """Return MCP compatible schema for this skill."""
    return UPDATE_TASK_SCHEMA


def get_skill_info() -> dict:
    """Return skill metadata."""
    return {
        "name": "update_task",
        "version": "1.0.0",
        "description": "Task ka title ya description edit karta hai",
        "author": "Todo App Phase 3",
        "parameters": [
            "user_id (required)",
            "task_id (required)",
            "title (optional)",
            "description (optional)"
        ],
        "returns": ["task_id", "status", "title", "description", "message"]
    }


# ============================================================================
# TESTING / STANDALONE EXECUTION
# ============================================================================
if __name__ == "__main__":
    import json

    print("=" * 60)
    print("MCP SKILL: update_task - Test Mode")
    print("=" * 60)

    print("\n📋 MCP Schema:")
    print(json.dumps(UPDATE_TASK_SCHEMA, indent=2))

    print("\n📌 Skill Info:")
    print(json.dumps(get_skill_info(), indent=2))

    print("\n🧪 Test Input Examples:")
    examples = [
        {"user_id": "user123", "task_id": 1, "title": "Buy groceries and fruits"},
        {"user_id": "user123", "task_id": 1, "description": "Milk, eggs, apples, bananas"},
        {"user_id": "user123", "task_id": 1, "title": "Shopping", "description": "Weekly groceries"}
    ]
    for ex in examples:
        print(f"  - {json.dumps(ex)}")

    print("\n✅ Expected Output (Success - Title Updated):")
    success_output = {
        "task_id": 1,
        "status": "updated",
        "title": "Buy groceries and fruits",
        "description": "Milk, eggs",
        "message": "Task title update ho gaya!"
    }
    print(json.dumps(success_output, indent=2))

    print("\n✅ Expected Output (Success - Both Updated):")
    both_output = {
        "task_id": 1,
        "status": "updated",
        "title": "Shopping",
        "description": "Weekly groceries",
        "message": "Task title aur description dono update ho gaye!"
    }
    print(json.dumps(both_output, indent=2))

    print("\n❌ Expected Output (Error - Nothing to Update):")
    error_output = {
        "task_id": 1,
        "status": "error",
        "title": "",
        "description": None,
        "message": "Kuch update karne ko nahi hai. Title ya description dein."
    }
    print(json.dumps(error_output, indent=2))

    print("\n" + "=" * 60)
