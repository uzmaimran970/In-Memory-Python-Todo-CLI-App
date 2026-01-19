"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        MCP SKILL: add_task                                   ║
║══════════════════════════════════════════════════════════════════════════════║
║  Purpose:  User ke natural language message se naya task create karna        ║
║            aur Neon PostgreSQL DB mein save karna.                           ║
║                                                                              ║
║  Author:   Todo App Phase 3                                                  ║
║  Version:  1.0.0                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

STEP BY STEP GUIDE (Roman Urdu):
================================

Step 1: User Message Samjho
---------------------------
Jab user kuch aisa bole:
- "Mujhe kal grocery leni hai"
- "Add task: Meeting at 3pm"
- "Naya kaam: Report submit karna hai"

AI ko samajhna hai ke yeh task add karna hai.

Step 2: Parameters Extract Karo
-------------------------------
User message se yeh cheezein nikalo:
- title: Main kaam kya hai (required)
- description: Extra detail agar ho (optional)
- user_id: JWT token se automatically milega

Step 3: Database Mein Save Karo
-------------------------------
SQLModel use karke Task table mein entry banao:
- user_id set karo (ownership ke liye)
- created_at = current UTC time
- updated_at = current UTC time
- completed = False (new task)

Step 4: Response Return Karo
----------------------------
Success pe: task_id, status="created", friendly message
Error pe: task_id=-1, status="error", error message

"""

# ============================================================================
# IMPORTS
# ============================================================================
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from sqlmodel import Session, select
import sys
import os

# App imports (when running from backend directory)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.models import Task, User
    from app.database import engine, get_session
except ImportError:
    # Fallback for standalone testing
    Task = None
    User = None
    engine = None


# ============================================================================
# MCP SDK COMPATIBLE SCHEMA
# ============================================================================
ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": (
        "User ke natural language message se naya task create karta hai "
        "aur Neon PostgreSQL DB mein save karta hai. "
        "Title required hai, description optional hai."
    ),
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
        "additionalProperties": False
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "Naya task ka auto-generated ID"
            },
            "status": {
                "type": "string",
                "enum": ["created", "error"],
                "description": "Operation ka status"
            },
            "title": {
                "type": "string",
                "description": "Jo title diya tha"
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
class AddTaskInput(BaseModel):
    """
    add_task skill ke input parameters.

    Attributes:
        user_id: Better Auth se current logged-in user ka ID (required)
        title: Task ka main title (required, 1-200 chars)
        description: Task ki detail ya note (optional, max 1000 chars)

    Example:
        ```python
        input_data = AddTaskInput(
            user_id="user_abc123",
            title="Buy groceries",
            description="Milk, eggs, bread"
        )
        ```
    """
    user_id: str = Field(
        ...,
        min_length=1,
        description="Better Auth se current logged-in user ka ID"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task ka main title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task ki detail ya note (optional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }


# ============================================================================
# OUTPUT MODEL (Pydantic)
# ============================================================================
class AddTaskOutput(BaseModel):
    """
    add_task skill ka output/response.

    Attributes:
        task_id: Naya task ka auto-generated ID (-1 agar error)
        status: "created" ya "error"
        title: Jo title diya tha
        message: Success/error message (Roman Urdu mein)

    Example Success:
        ```json
        {
            "task_id": 5,
            "status": "created",
            "title": "Buy groceries",
            "message": "Task 'Buy groceries' successfully add ho gaya! ✓"
        }
        ```

    Example Error:
        ```json
        {
            "task_id": -1,
            "status": "error",
            "title": "Buy groceries",
            "message": "Task add nahi ho saka. Dobara try karein."
        }
        ```
    """
    task_id: int = Field(
        description="Naya task ka auto-generated ID (-1 agar error)"
    )
    status: str = Field(
        description="'created' ya 'error'"
    )
    title: str = Field(
        description="Jo title diya tha"
    )
    message: str = Field(
        description="Success/error message (Roman Urdu mein)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 5,
                "status": "created",
                "title": "Buy groceries",
                "message": "Task 'Buy groceries' successfully add ho gaya! ✓"
            }
        }


# ============================================================================
# MAIN SKILL FUNCTION
# ============================================================================
def add_task(input_data: AddTaskInput) -> AddTaskOutput:
    """
    MCP Skill: add_task

    Naya task create karta hai aur Neon PostgreSQL DB mein save karta hai.

    STEP BY STEP PROCESS:
    ---------------------
    1. Input validation (Pydantic automatically karega)
    2. User existence check (Better Auth se verify)
    3. Task object create karo SQLModel se
    4. Database mein save karo
    5. Success/Error response return karo

    Args:
        input_data: AddTaskInput object with user_id, title, description

    Returns:
        AddTaskOutput: task_id, status, title, message

    Raises:
        No exceptions raised - errors are returned in AddTaskOutput

    Example:
        ```python
        # Input
        input_data = AddTaskInput(
            user_id="user_abc123",
            title="Buy groceries",
            description="Milk, eggs, bread"
        )

        # Call skill
        result = add_task(input_data)

        # Output
        print(result.task_id)   # 5
        print(result.status)    # "created"
        print(result.message)   # "Task 'Buy groceries' successfully add ho gaya! ✓"
        ```
    """

    # -------------------------------------------------------------------------
    # Step 1: Database Connection
    # -------------------------------------------------------------------------
    try:
        if engine is None:
            return AddTaskOutput(
                task_id=-1,
                status="error",
                title=input_data.title,
                message="Database connection nahi hai. Server restart karein."
            )

        with Session(engine) as session:

            # -----------------------------------------------------------------
            # Step 2: User Verification (Better Auth se)
            # -----------------------------------------------------------------
            # Check ke user exist karta hai ya nahi
            user = session.exec(
                select(User).where(User.id == input_data.user_id)
            ).first()

            if not user:
                return AddTaskOutput(
                    task_id=-1,
                    status="error",
                    title=input_data.title,
                    message="User verify nahi ho saka. Pehle login karein."
                )

            # -----------------------------------------------------------------
            # Step 3: Task Object Create Karo (SQLModel)
            # -----------------------------------------------------------------
            new_task = Task(
                user_id=input_data.user_id,      # Ownership set karo
                title=input_data.title,           # Required field
                description=input_data.description,  # Optional field
                completed=False,                  # New task = incomplete
                created_at=datetime.utcnow(),     # Current UTC time
                updated_at=datetime.utcnow()      # Current UTC time
            )

            # -----------------------------------------------------------------
            # Step 4: Database Mein Save Karo
            # -----------------------------------------------------------------
            session.add(new_task)
            session.commit()
            session.refresh(new_task)  # Auto-generated ID lene ke liye

            # -----------------------------------------------------------------
            # Step 5: Success Response
            # -----------------------------------------------------------------
            return AddTaskOutput(
                task_id=new_task.id,
                status="created",
                title=new_task.title,
                message=f"Task '{new_task.title}' successfully add ho gaya! ✓"
            )

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------
    except Exception as e:
        error_msg = str(e)

        # Friendly error messages
        if "duplicate" in error_msg.lower():
            friendly_msg = "Yeh task pehle se exist karta hai."
        elif "connection" in error_msg.lower():
            friendly_msg = "Database se connection nahi ho saka. Thodi der baad try karein."
        elif "timeout" in error_msg.lower():
            friendly_msg = "Request timeout ho gayi. Dobara try karein."
        else:
            friendly_msg = f"Task add nahi ho saka. Error: {error_msg[:50]}"

        return AddTaskOutput(
            task_id=-1,
            status="error",
            title=input_data.title,
            message=friendly_msg
        )


# ============================================================================
# ASYNC VERSION (FastAPI ke liye)
# ============================================================================
async def add_task_async(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    session: Session = None
) -> AddTaskOutput:
    """
    Async version of add_task skill for FastAPI endpoints.

    Use with FastAPI Depends:
        ```python
        @router.post("/tasks")
        async def create_task(
            data: TaskCreate,
            user_id: str = Depends(get_current_user_id),
            session: Session = Depends(get_session)
        ):
            result = await add_task_async(
                user_id=user_id,
                title=data.title,
                description=data.description,
                session=session
            )
            return result
        ```

    Args:
        user_id: Better Auth se user ID
        title: Task ka title
        description: Task ki description (optional)
        session: SQLModel Session (injected via Depends)

    Returns:
        AddTaskOutput: Same as sync version
    """
    try:
        # User verification
        user = session.exec(
            select(User).where(User.id == user_id)
        ).first()

        if not user:
            return AddTaskOutput(
                task_id=-1,
                status="error",
                title=title,
                message="User verify nahi ho saka. Pehle login karein."
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

        # Save to DB
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return AddTaskOutput(
            task_id=new_task.id,
            status="created",
            title=new_task.title,
            message=f"Task '{new_task.title}' successfully add ho gaya! ✓"
        )

    except Exception as e:
        return AddTaskOutput(
            task_id=-1,
            status="error",
            title=title,
            message=f"Task add nahi ho saka. Error: {str(e)[:50]}"
        )


# ============================================================================
# FASTAPI ENDPOINT CODE
# ============================================================================
"""
FastAPI Router mein add karo (app/routers/mcp.py):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.auth import get_current_user_id
from skills.add_task import add_task_async, AddTaskInput, AddTaskOutput

router = APIRouter(prefix="/api/mcp", tags=["mcp-skills"])

@router.post("/skills/add_task", response_model=AddTaskOutput)
async def mcp_add_task(
    request: AddTaskInput,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> AddTaskOutput:
    '''
    MCP Skill: add_task

    Naya task create karta hai authenticated user ke liye.
    user_id JWT token se automatically milta hai (security).
    '''
    # Override user_id with JWT user_id for security
    result = await add_task_async(
        user_id=current_user_id,  # JWT se - secure
        title=request.title,
        description=request.description,
        session=session
    )

    if result.status == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )

    return result
```
"""


# ============================================================================
# MCP TOOL HANDLER (for MCP Server)
# ============================================================================
def handle_add_task_tool(arguments: dict) -> dict:
    """
    MCP Server ke liye tool handler.

    MCP Server se call hoga jab client "add_task" tool use karega.

    Args:
        arguments: Dict with user_id, title, description

    Returns:
        Dict with task_id, status, title, message

    Example MCP Request:
        ```json
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "add_task",
                "arguments": {
                    "user_id": "user123",
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread"
                }
            }
        }
        ```

    Example MCP Response:
        ```json
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [{
                    "type": "text",
                    "text": "{\"task_id\": 5, \"status\": \"created\", ...}"
                }]
            }
        }
        ```
    """
    try:
        # Input validation
        input_data = AddTaskInput(
            user_id=arguments.get("user_id", ""),
            title=arguments.get("title", ""),
            description=arguments.get("description")
        )

        # Call main skill function
        result = add_task(input_data)

        # Return as dict
        return {
            "task_id": result.task_id,
            "status": result.status,
            "title": result.title,
            "message": result.message
        }

    except Exception as e:
        return {
            "task_id": -1,
            "status": "error",
            "title": arguments.get("title", "Unknown"),
            "message": f"Skill execution failed: {str(e)}"
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_skill_schema() -> dict:
    """Return MCP compatible schema for this skill."""
    return ADD_TASK_SCHEMA


def get_skill_info() -> dict:
    """Return skill metadata."""
    return {
        "name": "add_task",
        "version": "1.0.0",
        "description": "Naya task create karta hai Neon PostgreSQL DB mein",
        "author": "Todo App Phase 3",
        "parameters": ["user_id (required)", "title (required)", "description (optional)"],
        "returns": ["task_id", "status", "title", "message"]
    }


# ============================================================================
# TESTING / STANDALONE EXECUTION
# ============================================================================
if __name__ == "__main__":
    """
    Standalone testing ke liye run karo:
        python skills/add_task.py
    """
    import json

    print("=" * 60)
    print("MCP SKILL: add_task - Test Mode")
    print("=" * 60)

    # Print schema
    print("\n📋 MCP Schema:")
    print(json.dumps(ADD_TASK_SCHEMA, indent=2))

    # Print skill info
    print("\n📌 Skill Info:")
    print(json.dumps(get_skill_info(), indent=2))

    # Test input
    print("\n🧪 Test Input:")
    test_input = {
        "user_id": "test_user_123",
        "title": "Buy groceries",
        "description": "Milk, eggs, bread"
    }
    print(json.dumps(test_input, indent=2))

    # Note about actual testing
    print("\n⚠️  Note:")
    print("   Actual database testing ke liye backend server start karo:")
    print("   cd backend && uvicorn app.main:app --reload")
    print("\n   Phir curl se test karo:")
    print('   curl -X POST "http://localhost:8000/api/mcp/skills/add_task" \\')
    print('        -H "Authorization: Bearer YOUR_JWT_TOKEN" \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"title": "Buy groceries", "description": "Milk, eggs"}\'')

    print("\n" + "=" * 60)
