"""
Chat API Endpoints for TodoAI Chatbot
Handles chat messaging, history, and conversation management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from typing import Optional

from app.database import get_session
from app.auth import get_current_user_id
from app.models import Conversation, Message, MessageRole
from app.services.chat_service import process_chat_message, get_chat_history as get_history_service

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["chat"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for sending a chat message."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's message text"
    )


class ToolCallInfo(BaseModel):
    """Information about an executed tool call."""
    name: str
    result: dict


class ChatResponse(BaseModel):
    """Response model for chat messages."""
    message: str = Field(..., description="AI assistant's response")
    conversation_id: str = Field(..., description="Conversation identifier")
    tool_calls: Optional[list[ToolCallInfo]] = Field(
        default=None,
        description="Tools executed by the assistant"
    )


class MessageItem(BaseModel):
    """Single message in chat history."""
    id: str
    role: str
    content: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation ID (null if no conversation exists)"
    )
    messages: list[MessageItem] = Field(
        default=[],
        description="List of messages in chronological order"
    )
    total: int = Field(..., description="Total number of messages returned")


class ClearHistoryResponse(BaseModel):
    """Response model for clearing chat history."""
    message: str = Field(..., description="Status message")
    deleted_count: int = Field(..., description="Number of messages deleted")


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Process a chat message through the AI assistant.

    The assistant can:
    - Create, list, complete, delete, and update tasks
    - Answer questions about the user's tasks
    - Respond in English or Roman Urdu based on user's language

    Security:
    - Requires valid JWT token
    - All task operations are scoped to the authenticated user

    Args:
        request: ChatRequest with user's message
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        ChatResponse with AI response and any executed tool calls

    Raises:
        401: Missing or invalid JWT token
        500: AI service error (returns friendly message)
    """
    try:
        result = await process_chat_message(
            user_id=current_user_id,
            message=request.message,
            session=session
        )

        return ChatResponse(
            message=result["response"],
            conversation_id=result["conversation_id"],
            tool_calls=[
                ToolCallInfo(name=tc["name"], result=tc["result"])
                for tc in result.get("tool_calls", [])
            ] if result.get("tool_calls") else None
        )

    except Exception as e:
        # Log error but return friendly message to user
        print(f"[CHAT] Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Abhi thodi problem hai. Please dobara try karein."
        )


@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_conversation_history(
    limit: int = 50,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Get conversation history for the current user.

    Returns messages in chronological order (oldest first).

    Args:
        limit: Maximum number of messages to return (default 50)
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        ChatHistoryResponse with messages and conversation ID

    Raises:
        401: Missing or invalid JWT token
    """
    # Find user's conversation
    conversation = session.exec(
        select(Conversation).where(Conversation.user_id == current_user_id)
    ).first()

    if not conversation:
        return ChatHistoryResponse(
            conversation_id=None,
            messages=[],
            total=0
        )

    # Get messages
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()

    return ChatHistoryResponse(
        conversation_id=conversation.id,
        messages=[
            MessageItem(
                id=msg.id,
                role=msg.role.value,
                content=msg.content,
                created_at=msg.created_at.isoformat()
            )
            for msg in reversed(messages)  # Chronological order
        ],
        total=len(messages)
    )


@router.delete("/chat/clear", response_model=ClearHistoryResponse)
async def clear_chat_history(
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Clear all messages in the user's conversation.

    This permanently deletes all chat messages but keeps the conversation.
    Cannot be undone.

    Args:
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        ClearHistoryResponse with deletion count

    Raises:
        401: Missing or invalid JWT token
    """
    # Find user's conversation
    conversation = session.exec(
        select(Conversation).where(Conversation.user_id == current_user_id)
    ).first()

    if not conversation:
        return ClearHistoryResponse(
            message="No history to clear",
            deleted_count=0
        )

    # Get and delete all messages
    messages = session.exec(
        select(Message).where(Message.conversation_id == conversation.id)
    ).all()

    count = len(messages)
    for msg in messages:
        session.delete(msg)

    session.commit()

    return ClearHistoryResponse(
        message="Chat history clear ho gaya.",
        deleted_count=count
    )
