"""
MCP Tools Router - FastAPI endpoints for MCP tools.

Yeh router MCP SDK compatible tools ko REST API ke through expose karta hai.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional
from pydantic import BaseModel, Field

from app.database import get_session
from app.auth import get_current_user_id
from app.mcp_tools.add_task import (
    add_task_tool_async,
    AddTaskOutput,
    ADD_TASK_TOOL_SCHEMA
)


# Router with /api/mcp prefix
router = APIRouter(prefix="/api/mcp", tags=["mcp-tools"])


# ============================================
# Request/Response Models
# ============================================
class AddTaskRequest(BaseModel):
    """add_task tool ke liye request body."""
    title: str = Field(
        ...,
        description="Task ka title",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="Task ki detail (optional)",
        max_length=1000
    )


class MCPToolResponse(BaseModel):
    """Generic MCP tool response wrapper."""
    tool_name: str
    success: bool
    result: dict


# ============================================
# MCP Tool: add_task Endpoint
# ============================================
@router.post("/tools/add_task", response_model=AddTaskOutput)
async def mcp_add_task(
    request: AddTaskRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> AddTaskOutput:
    """
    MCP Tool: add_task

    Naya task create karta hai authenticated user ke liye.

    **Security:**
    - user_id JWT token se automatically milta hai
    - Manual user_id accept nahi hota (security reason)

    **Input:**
    - title (required): Task ka title
    - description (optional): Task ki detail

    **Output:**
    - task_id: Naye task ka ID
    - status: "created" ya "error"
    - title: Jo title diya tha
    - message: Success/error message

    **Example Request:**
    ```json
    {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread"
    }
    ```

    **Example Response:**
    ```json
    {
        "task_id": 5,
        "status": "created",
        "title": "Buy groceries",
        "message": "Task 'Buy groceries' successfully add ho gaya!"
    }
    ```
    """
    result = await add_task_tool_async(
        user_id=current_user_id,  # JWT se - secure
        title=request.title,
        description=request.description,
        session=session
    )

    # Agar error aaya
    if result.status == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )

    return result


# ============================================
# MCP Tool Schema Endpoint
# ============================================
@router.get("/tools/add_task/schema")
async def get_add_task_schema():
    """
    add_task tool ka MCP compatible schema return karta hai.

    Yeh schema MCP clients ko batata hai ke tool kaise use karna hai.
    """
    return ADD_TASK_TOOL_SCHEMA


# ============================================
# List All Available MCP Tools
# ============================================
@router.get("/tools")
async def list_mcp_tools():
    """
    Saare available MCP tools ki list return karta hai.
    """
    return {
        "tools": [
            {
                "name": "add_task",
                "description": "Naya task create karta hai Neon DB mein",
                "endpoint": "/api/mcp/tools/add_task",
                "schema_endpoint": "/api/mcp/tools/add_task/schema"
            }
        ],
        "total": 1
    }
