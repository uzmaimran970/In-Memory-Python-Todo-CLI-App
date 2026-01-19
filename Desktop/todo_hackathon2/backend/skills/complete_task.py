"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        MCP SKILL: complete_task                              ║
║══════════════════════════════════════════════════════════════════════════════║
║  Purpose:  Kisi task ko complete mark karna (completed = True)               ║
║                                                                              ║
║  Author:   Todo App Phase 3                                                  ║
║  Version:  1.0.0                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

STEP BY STEP GUIDE (Roman Urdu):
================================

Step 1: User Message Samjho
---------------------------
Jab user kuch aisa bole:
- "Task 3 complete ho gaya"
- "Grocery wala kaam done hai"
- "Mark task 5 as complete"
- "Pehla task finish"

AI ko samajhna hai ke task complete karna hai.

Step 2: Parameters Extract Karo
-------------------------------
User message se yeh cheezein nikalo:
- task_id: Kaunsa task complete karna hai
- user_id: JWT token se automatically milega

Step 3: Ownership Verify Karo
-----------------------------
Check karo ke:
- Task exist karta hai
- Task us hi user ka hai (ownership)

Step 4: Task Update Karo
------------------------
- completed = True set karo
- updated_at = current UTC time

Step 5: Response Return Karo
----------------------------
Success pe: confirmation message with 🎉
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
COMPLETE_TASK_SCHEMA = {
    "name": "complete_task",
    "description": (
        "Kisi task ko complete mark karta hai (completed = True). "
        "Sirf logged-in user apna task complete kar sakta hai. "
        "Task ID required hai."
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
                "description": "Task ka ID jo complete karna hai"
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
                "description": "Task ka ID"
            },
            "status": {
                "type": "string",
                "enum": ["completed", "error"],
                "description": "Operation ka status"
            },
            "title": {
                "type": "string",
                "description": "Task ka title"
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
class CompleteTaskInput(BaseModel):
    """
    complete_task skill ke input parameters.

    Attributes:
        user_id: Current logged-in user ka ID (required)
        task_id: Task ka ID jo complete karna hai (required)

    Example:
        ```python
        input_data = CompleteTaskInput(
            user_id="user_abc123",
            task_id=3
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
        description="Task ka ID jo complete karna hai"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "task_id": 3
            }
        }


# ============================================================================
# OUTPUT MODEL (Pydantic)
# ============================================================================
class CompleteTaskOutput(BaseModel):
    """
    complete_task skill ka output/response.

    Attributes:
        task_id: Task ka ID
        status: "completed" ya "error"
        title: Task ka title
        message: Success/error message (Roman Urdu mein)

    Example Success:
        ```json
        {
            "task_id": 3,
            "status": "completed",
            "title": "Call mom",
            "message": "Task 'Call mom' complete ho gaya! 🎉"
        }
        ```

    Example Error:
        ```json
        {
            "task_id": 3,
            "status": "error",
            "title": "",
            "message": "Task nahi mila. Shayad delete ho gaya hai."
        }
        ```
    """
    task_id: int = Field(
        description="Task ka ID"
    )
    status: str = Field(
        description="'completed' ya 'error'"
    )
    title: str = Field(
        default="",
        description="Task ka title"
    )
    message: str = Field(
        description="Success/error message (Roman Urdu mein)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 3,
                "status": "completed",
                "title": "Call mom",
                "message": "Task 'Call mom' complete ho gaya! 🎉"
            }
        }


# ============================================================================
# MAIN SKILL FUNCTION
# ============================================================================
def complete_task(input_data: CompleteTaskInput) -> CompleteTaskOutput:
    """
    MCP Skill: complete_task

    Task ko complete mark karta hai (completed = True).

    STEP BY STEP PROCESS:
    ---------------------
    1. Input validation
    2. Task find karo by task_id
    3. Ownership verify karo (user_id match)
    4. completed = True set karo
    5. updated_at update karo
    6. Success/Error response return karo

    Args:
        input_data: CompleteTaskInput with user_id and task_id

    Returns:
        CompleteTaskOutput: task_id, status, title, message

    Example:
        ```python
        # Input
        input_data = CompleteTaskInput(
            user_id="user_abc123",
            task_id=3
        )

        # Call skill
        result = complete_task(input_data)

        # Output
        print(result.status)   # "completed"
        print(result.message)  # "Task 'Call mom' complete ho gaya! 🎉"
        ```
    """

    # -------------------------------------------------------------------------
    # Step 1: Database Connection
    # -------------------------------------------------------------------------
    try:
        if engine is None:
            return CompleteTaskOutput(
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
                return CompleteTaskOutput(
                    task_id=input_data.task_id,
                    status="error",
                    title="",
                    message="Task nahi mila. Shayad delete ho gaya hai."
                )

            # -----------------------------------------------------------------
            # Step 3: Ownership Verify Karo
            # -----------------------------------------------------------------
            if task.user_id != input_data.user_id:
                return CompleteTaskOutput(
                    task_id=input_data.task_id,
                    status="error",
                    title="",
                    message="Yeh task aapka nahi hai. Sirf apna task complete kar sakte hain."
                )

            # -----------------------------------------------------------------
            # Step 4: Check Agar Already Complete Hai
            # -----------------------------------------------------------------
            if task.completed:
                return CompleteTaskOutput(
                    task_id=task.id,
                    status="completed",
                    title=task.title,
                    message=f"Task '{task.title}' pehle se complete hai! ✓"
                )

            # -----------------------------------------------------------------
            # Step 5: Task Complete Karo
            # -----------------------------------------------------------------
            task.completed = True
            task.updated_at = datetime.utcnow()

            # Save to database
            session.add(task)
            session.commit()
            session.refresh(task)

            # -----------------------------------------------------------------
            # Step 6: Success Response
            # -----------------------------------------------------------------
            return CompleteTaskOutput(
                task_id=task.id,
                status="completed",
                title=task.title,
                message=f"Task '{task.title}' complete ho gaya! 🎉 Shabash!"
            )

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------
    except Exception as e:
        return CompleteTaskOutput(
            task_id=input_data.task_id,
            status="error",
            title="",
            message=f"Task complete nahi ho saka. Error: {str(e)[:50]}"
        )


# ============================================================================
# ASYNC VERSION (FastAPI ke liye)
# ============================================================================
async def complete_task_async(
    user_id: str,
    task_id: int,
    session: Session = None
) -> CompleteTaskOutput:
    """
    Async version of complete_task skill for FastAPI endpoints.

    Args:
        user_id: Current logged-in user ka ID
        task_id: Task ka ID jo complete karna hai
        session: SQLModel Session (injected via Depends)

    Returns:
        CompleteTaskOutput: task_id, status, title, message
    """
    try:
        # Task find karo
        task = session.get(Task, task_id)

        if not task:
            return CompleteTaskOutput(
                task_id=task_id,
                status="error",
                title="",
                message="Task nahi mila. Shayad delete ho gaya hai."
            )

        # Ownership check
        if task.user_id != user_id:
            return CompleteTaskOutput(
                task_id=task_id,
                status="error",
                title="",
                message="Yeh task aapka nahi hai. Sirf apna task complete kar sakte hain."
            )

        # Already complete check
        if task.completed:
            return CompleteTaskOutput(
                task_id=task.id,
                status="completed",
                title=task.title,
                message=f"Task '{task.title}' pehle se complete hai! ✓"
            )

        # Complete karo
        task.completed = True
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return CompleteTaskOutput(
            task_id=task.id,
            status="completed",
            title=task.title,
            message=f"Task '{task.title}' complete ho gaya! 🎉 Shabash!"
        )

    except Exception as e:
        return CompleteTaskOutput(
            task_id=task_id,
            status="error",
            title="",
            message=f"Task complete nahi ho saka. Error: {str(e)[:50]}"
        )


# ============================================================================
# TOGGLE VERSION (Complete ↔ Incomplete)
# ============================================================================
async def toggle_task_async(
    user_id: str,
    task_id: int,
    session: Session = None
) -> CompleteTaskOutput:
    """
    Toggle task completion status (complete ↔ incomplete).

    Yeh function existing PATCH /tasks/{id}/complete endpoint ke saath
    compatible hai jo toggle karta hai.

    Args:
        user_id: Current logged-in user ka ID
        task_id: Task ka ID
        session: SQLModel Session

    Returns:
        CompleteTaskOutput: Updated task status
    """
    try:
        task = session.get(Task, task_id)

        if not task:
            return CompleteTaskOutput(
                task_id=task_id,
                status="error",
                title="",
                message="Task nahi mila."
            )

        if task.user_id != user_id:
            return CompleteTaskOutput(
                task_id=task_id,
                status="error",
                title="",
                message="Yeh task aapka nahi hai."
            )

        # Toggle
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        if task.completed:
            message = f"Task '{task.title}' complete ho gaya! 🎉"
            status = "completed"
        else:
            message = f"Task '{task.title}' incomplete mark ho gaya."
            status = "incomplete"

        return CompleteTaskOutput(
            task_id=task.id,
            status=status,
            title=task.title,
            message=message
        )

    except Exception as e:
        return CompleteTaskOutput(
            task_id=task_id,
            status="error",
            title="",
            message=f"Error: {str(e)[:50]}"
        )


# ============================================================================
# MCP TOOL HANDLER (for MCP Server)
# ============================================================================
def handle_complete_task_tool(arguments: dict) -> dict:
    """
    MCP Server ke liye tool handler.

    Args:
        arguments: Dict with user_id and task_id

    Returns:
        Dict with task_id, status, title, message
    """
    try:
        input_data = CompleteTaskInput(
            user_id=arguments.get("user_id", ""),
            task_id=arguments.get("task_id", 0)
        )

        result = complete_task(input_data)

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
    return COMPLETE_TASK_SCHEMA


def get_skill_info() -> dict:
    """Return skill metadata."""
    return {
        "name": "complete_task",
        "version": "1.0.0",
        "description": "Task ko complete mark karta hai",
        "author": "Todo App Phase 3",
        "parameters": ["user_id (required)", "task_id (required)"],
        "returns": ["task_id", "status", "title", "message"]
    }


# ============================================================================
# TESTING / STANDALONE EXECUTION
# ============================================================================
if __name__ == "__main__":
    import json

    print("=" * 60)
    print("MCP SKILL: complete_task - Test Mode")
    print("=" * 60)

    print("\n📋 MCP Schema:")
    print(json.dumps(COMPLETE_TASK_SCHEMA, indent=2))

    print("\n📌 Skill Info:")
    print(json.dumps(get_skill_info(), indent=2))

    print("\n🧪 Test Input Example:")
    test_input = {"user_id": "user123", "task_id": 3}
    print(json.dumps(test_input, indent=2))

    print("\n✅ Expected Output (Success):")
    success_output = {
        "task_id": 3,
        "status": "completed",
        "title": "Call mom",
        "message": "Task 'Call mom' complete ho gaya! 🎉 Shabash!"
    }
    print(json.dumps(success_output, indent=2))

    print("\n❌ Expected Output (Error):")
    error_output = {
        "task_id": 3,
        "status": "error",
        "title": "",
        "message": "Task nahi mila. Shayad delete ho gaya hai."
    }
    print(json.dumps(error_output, indent=2))

    print("\n" + "=" * 60)
