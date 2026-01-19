"""
MCP Tool: add_task
Purpose: User ke natural language se naya task create karna aur Neon DB mein save karna.

MCP SDK Compatible Format
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlmodel import Session, select

from app.models import Task, User
from app.database import engine


# ============================================
# Step 1: Input Schema (Parameters)
# ============================================
class AddTaskInput(BaseModel):
    """
    add_task tool ke input parameters.

    Example:
        {
            "user_id": "user123",
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        }
    """
    user_id: str = Field(
        ...,  # Required
        description="Current user ka ID (Better Auth se milega)",
        min_length=1
    )
    title: str = Field(
        ...,  # Required
        description="Task ka title",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="Task ki detail (optional)",
        max_length=1000
    )


# ============================================
# Step 2: Output Schema (Returns)
# ============================================
class AddTaskOutput(BaseModel):
    """
    add_task tool ka output.

    Example:
        {
            "task_id": 5,
            "status": "created",
            "title": "Buy groceries"
        }
    """
    task_id: int = Field(description="Naya task ka ID")
    status: str = Field(description="Task creation status")
    title: str = Field(description="Jo title diya tha")
    message: Optional[str] = Field(default=None, description="Additional message")


# ============================================
# Step 3: MCP Tool Definition (Schema)
# ============================================
ADD_TASK_TOOL_SCHEMA = {
    "name": "add_task",
    "description": "User ke natural language se naya task create karta hai aur Neon DB mein save karta hai. Task title required hai, description optional hai.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Current user ka ID (Better Auth se milega)"
            },
            "title": {
                "type": "string",
                "description": "Task ka title (required, 1-200 characters)"
            },
            "description": {
                "type": "string",
                "description": "Task ki detail (optional, max 1000 characters)"
            }
        },
        "required": ["user_id", "title"]
    }
}


# ============================================
# Step 4: Tool Implementation
# ============================================
def add_task_tool(input_data: AddTaskInput) -> AddTaskOutput:
    """
    MCP Tool: add_task

    Naya task create karta hai aur database mein save karta hai.

    Args:
        input_data: AddTaskInput with user_id, title, description

    Returns:
        AddTaskOutput with task_id, status, title

    Behavior:
        - user_id check karta hai ke valid user hai
        - created_at aur updated_at automatically set hote hain
        - Error aaye to friendly message return karta hai
    """
    try:
        with Session(engine) as session:
            # Step 4a: User validation (optional but recommended)
            user = session.exec(
                select(User).where(User.id == input_data.user_id)
            ).first()

            if not user:
                return AddTaskOutput(
                    task_id=-1,
                    status="error",
                    title=input_data.title,
                    message="User nahi mila. Pehle login karein."
                )

            # Step 4b: Task create karo
            new_task = Task(
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Step 4c: Database mein save karo
            session.add(new_task)
            session.commit()
            session.refresh(new_task)  # Auto-generated ID lene ke liye

            # Step 4d: Success response
            return AddTaskOutput(
                task_id=new_task.id,
                status="created",
                title=new_task.title,
                message=f"Task '{new_task.title}' successfully add ho gaya!"
            )

    except Exception as e:
        # Step 4e: Error handling - friendly message
        return AddTaskOutput(
            task_id=-1,
            status="error",
            title=input_data.title,
            message=f"Task add nahi ho saka. Error: {str(e)}"
        )


# ============================================
# Step 5: Async version for FastAPI
# ============================================
async def add_task_tool_async(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    session: Session = None
) -> AddTaskOutput:
    """
    Async version of add_task tool for FastAPI endpoints.

    Use with dependency injection:
        session: Session = Depends(get_session)
    """
    try:
        # User validation
        user = session.exec(
            select(User).where(User.id == user_id)
        ).first()

        if not user:
            return AddTaskOutput(
                task_id=-1,
                status="error",
                title=title,
                message="User nahi mila. Pehle login karein."
            )

        # Task create karo
        new_task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return AddTaskOutput(
            task_id=new_task.id,
            status="created",
            title=new_task.title,
            message=f"Task '{new_task.title}' successfully add ho gaya!"
        )

    except Exception as e:
        return AddTaskOutput(
            task_id=-1,
            status="error",
            title=title,
            message=f"Task add nahi ho saka. Error: {str(e)}"
        )
