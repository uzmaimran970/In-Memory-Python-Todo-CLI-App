# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `004-ai-chatbot-integration` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Phase**: 3 (AI-Powered Features)

---

## Summary

Integrate an AI-powered chatbot into the existing Todo application to enable natural language task management. Users interact via a floating chat icon that opens a modal interface. The backend uses Cohere API for AI generation and tool calling, executing existing MCP skills for task operations. The system is stateless with conversation history persisted in Neon PostgreSQL.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            SYSTEM ARCHITECTURE                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         FRONTEND (Next.js + Vercel)                      │    │
│  │                                                                          │    │
│  │   ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐        │    │
│  │   │ ChatbotIcon  │────►│  ChatModal   │────►│  API Client      │        │    │
│  │   │ (Floating)   │     │  (Messages)  │     │  POST /api/chat  │        │    │
│  │   └──────────────┘     └──────────────┘     └────────┬─────────┘        │    │
│  │                                                       │                  │    │
│  └───────────────────────────────────────────────────────┼──────────────────┘    │
│                                                          │                       │
│                                            JWT Token     │                       │
│                                            + Message     │                       │
│                                                          ▼                       │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                       BACKEND (FastAPI + Railway)                          │  │
│  │                                                                            │  │
│  │   ┌────────────────┐      ┌─────────────────┐      ┌─────────────────┐    │  │
│  │   │ Auth Middleware│─────►│  Chat Router    │─────►│ Cohere Client   │    │  │
│  │   │ (JWT Validate) │      │  /api/chat      │      │ (AI Generation) │    │  │
│  │   └────────────────┘      └────────┬────────┘      └────────┬────────┘    │  │
│  │                                    │                        │             │  │
│  │                    ┌───────────────┼────────────────────────┘             │  │
│  │                    │               │                                      │  │
│  │                    ▼               ▼                                      │  │
│  │   ┌─────────────────┐      ┌─────────────────┐                           │  │
│  │   │ MCP Skills      │      │ Conversation    │                           │  │
│  │   │ - add_task      │      │ Manager         │                           │  │
│  │   │ - list_tasks    │      │ (History)       │                           │  │
│  │   │ - complete_task │      └────────┬────────┘                           │  │
│  │   │ - delete_task   │               │                                    │  │
│  │   │ - update_task   │               │                                    │  │
│  │   └────────┬────────┘               │                                    │  │
│  │            │                        │                                    │  │
│  └────────────┼────────────────────────┼────────────────────────────────────┘  │
│               │                        │                                        │
│               ▼                        ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                      DATABASE (Neon PostgreSQL)                            │  │
│  │                                                                            │  │
│  │   ┌──────────┐    ┌───────────────┐    ┌──────────────┐                   │  │
│  │   │  users   │◄───│ conversations │◄───│   messages   │                   │  │
│  │   └────┬─────┘    └───────────────┘    └──────────────┘                   │  │
│  │        │                                                                   │  │
│  │        ▼                                                                   │  │
│  │   ┌──────────┐                                                            │  │
│  │   │  tasks   │  (Managed via MCP skills)                                  │  │
│  │   └──────────┘                                                            │  │
│  │                                                                            │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         EXTERNAL SERVICES                                   │ │
│  │                                                                             │ │
│  │   ┌─────────────────────────────────────────────────────────────────────┐  │ │
│  │   │                     COHERE API                                       │  │ │
│  │   │   - Model: command-r-plus (chat + tool use)                         │  │ │
│  │   │   - Embeddings: embed-multilingual-v3.0 (optional)                  │  │ │
│  │   │   - Multilingual: English + Roman Urdu                              │  │ │
│  │   └─────────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## Technical Context

| Aspect | Value |
|--------|-------|
| **Language/Version** | Python 3.11, TypeScript 5.x |
| **Primary Dependencies** | FastAPI, SQLModel, Cohere SDK, Next.js 14, Tailwind CSS |
| **Storage** | Neon PostgreSQL (existing) |
| **Testing** | pytest (backend), manual testing (frontend) |
| **Target Platform** | Web (Railway backend, Vercel frontend) |
| **Project Type** | Web application (frontend + backend) |
| **Performance Goals** | <3s response time, 100 concurrent users |
| **Constraints** | Stateless design, Cohere API rate limits |
| **Scale/Scope** | Single-tenant, conversation-per-user model |

---

## Constitution Check

| Principle | Status | Implementation |
|-----------|--------|----------------|
| I. User-Centric | PASS | Friendly responses, Roman Urdu support |
| II. Full Functionality | PASS | All 5 MCP skills accessible via chat |
| III. Security | PASS | JWT validation on every request |
| IV. AI Power | PASS | Cohere API with tool calling |
| V. Stateless | PASS | DB-persisted conversations |
| VI. Error Handling | PASS | User-friendly error messages |
| VII. Performance | PASS | <3s target, optimized queries |

**All constitution gates passed.**

---

## Project Structure

### Documentation (this feature)

```
specs/004-ai-chatbot-integration/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technical decisions
├── data-model.md        # Database entities
├── quickstart.md        # Setup guide
├── contracts/
│   └── chat-api.yaml    # OpenAPI specification
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Implementation tasks (via /sp.tasks)
```

### Source Code Changes

```
backend/
├── app/
│   ├── models.py            # ADD: Conversation, Message models
│   ├── routers/
│   │   └── chat.py          # NEW: Chat API endpoints
│   └── services/
│       ├── cohere_client.py # NEW: Cohere API wrapper
│       └── chat_service.py  # NEW: Chat processing logic
├── skills/                   # EXISTING: MCP skills (no changes)
└── requirements.txt          # ADD: cohere>=5.0.0

frontend/
├── src/
│   ├── components/
│   │   └── chat/
│   │       ├── ChatbotIcon.tsx   # NEW: Floating button
│   │       ├── ChatModal.tsx     # NEW: Modal container
│   │       ├── ChatMessages.tsx  # NEW: Message list
│   │       ├── ChatInput.tsx     # NEW: Input + send
│   │       └── index.ts          # NEW: Exports
│   ├── lib/
│   │   └── chat-api.ts           # NEW: API client
│   └── app/
│       └── (dashboard)/
│           └── layout.tsx        # MODIFY: Add ChatbotIcon
└── package.json                  # No new dependencies
```

---

## Implementation Phases

### Phase 1: Backend Foundation (Priority: P0)

#### Task 1.1: Add Database Models

**File**: `backend/app/models.py`

```python
# ADD to existing models.py

from enum import Enum
from uuid import uuid4
from sqlalchemy import Column, JSON

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", unique=True, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False)
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
```

#### Task 1.2: Create Cohere Client

**File**: `backend/app/services/cohere_client.py`

```python
import os
import cohere
from typing import Optional

# Initialize Cohere client
co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

# System preamble for TodoAI
SYSTEM_PREAMBLE = """
You are TodoAI, a friendly and helpful task management assistant.

LANGUAGE RULES:
- If user writes in Roman Urdu/Hinglish, respond in Roman Urdu
- If user writes in English, respond in English
- Be warm, encouraging, and supportive
- Use "aap" (respectful) for users

CAPABILITIES (use these tools):
- add_task: Create new tasks
- list_tasks: Show user's tasks (can filter by status)
- complete_task: Mark tasks as done
- delete_task: Remove tasks (always ask confirmation first)
- update_task: Edit task title or description

BEHAVIOR:
- For ambiguous requests, ask clarifying questions
- Confirm destructive actions before executing
- Provide helpful suggestions when appropriate
- Keep responses concise but friendly
"""

# MCP Tool definitions for Cohere
MCP_TOOLS = [
    {
        "name": "add_task",
        "description": "Create a new task for the user",
        "parameter_definitions": {
            "title": {
                "type": "str",
                "description": "Task title (required)",
                "required": True
            },
            "description": {
                "type": "str",
                "description": "Task description (optional)",
                "required": False
            }
        }
    },
    {
        "name": "list_tasks",
        "description": "Get user's tasks, optionally filtered by status",
        "parameter_definitions": {
            "status": {
                "type": "str",
                "description": "Filter: 'all', 'pending', or 'completed'",
                "required": False
            }
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed",
        "parameter_definitions": {
            "task_id": {
                "type": "int",
                "description": "ID of task to complete",
                "required": True
            }
        }
    },
    {
        "name": "delete_task",
        "description": "Permanently delete a task (ask confirmation first)",
        "parameter_definitions": {
            "task_id": {
                "type": "int",
                "description": "ID of task to delete",
                "required": True
            }
        }
    },
    {
        "name": "update_task",
        "description": "Update task title or description",
        "parameter_definitions": {
            "task_id": {
                "type": "int",
                "description": "ID of task to update",
                "required": True
            },
            "title": {
                "type": "str",
                "description": "New title (optional)",
                "required": False
            },
            "description": {
                "type": "str",
                "description": "New description (optional)",
                "required": False
            }
        }
    }
]

def chat_with_tools(
    message: str,
    chat_history: list[dict],
    conversation_id: Optional[str] = None
) -> dict:
    """
    Send message to Cohere with tool calling support.

    Args:
        message: User's message
        chat_history: Previous messages for context
        conversation_id: Optional conversation ID for Cohere

    Returns:
        dict with 'text', 'tool_calls', and metadata
    """
    response = co.chat(
        model="command-r-plus",
        message=message,
        preamble=SYSTEM_PREAMBLE,
        chat_history=chat_history,
        tools=MCP_TOOLS,
        conversation_id=conversation_id
    )

    return {
        "text": response.text,
        "tool_calls": [
            {
                "name": tc.name,
                "parameters": tc.parameters
            }
            for tc in (response.tool_calls or [])
        ],
        "conversation_id": response.conversation_id
    }

def continue_with_tool_results(
    tool_results: list[dict],
    conversation_id: str
) -> dict:
    """
    Continue conversation after tool execution.

    Args:
        tool_results: Results from executed tools
        conversation_id: Cohere conversation ID

    Returns:
        dict with final response
    """
    response = co.chat(
        model="command-r-plus",
        message="",
        preamble=SYSTEM_PREAMBLE,
        tool_results=tool_results,
        conversation_id=conversation_id
    )

    return {
        "text": response.text,
        "tool_calls": [],
        "conversation_id": response.conversation_id
    }
```

#### Task 1.3: Create Chat Service

**File**: `backend/app/services/chat_service.py`

```python
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional

from app.models import Conversation, Message, MessageRole
from app.services.cohere_client import chat_with_tools, continue_with_tool_results
from skills import (
    add_task_async, list_tasks_async, complete_task_async,
    delete_task_async, update_task_async,
    AddTaskInput, ListTasksInput, CompleteTaskInput,
    DeleteTaskInput, UpdateTaskInput
)

async def get_or_create_conversation(user_id: str, session: Session) -> Conversation:
    """Get existing conversation or create new one."""
    conversation = session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    return conversation

async def get_chat_history(conversation_id: str, session: Session, limit: int = 20) -> list[dict]:
    """Get recent messages formatted for Cohere."""
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()

    # Reverse for chronological order and format for Cohere
    return [
        {
            "role": "USER" if msg.role == MessageRole.USER else "CHATBOT",
            "message": msg.content
        }
        for msg in reversed(messages)
    ]

async def save_message(
    conversation_id: str,
    role: MessageRole,
    content: str,
    tool_calls: Optional[dict],
    session: Session
) -> Message:
    """Save message to database."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(message)
    return message

async def execute_tool(tool_name: str, parameters: dict, user_id: str, session: Session) -> dict:
    """Execute MCP skill and return result."""
    try:
        if tool_name == "add_task":
            result = await add_task_async(
                user_id=user_id,
                title=parameters.get("title", ""),
                description=parameters.get("description"),
                session=session
            )
            return {"status": result.status, "task_id": result.task_id, "message": result.message}

        elif tool_name == "list_tasks":
            result = await list_tasks_async(
                user_id=user_id,
                status=parameters.get("status", "all"),
                session=session
            )
            return {"tasks": [t.dict() for t in result.tasks], "total": result.total}

        elif tool_name == "complete_task":
            result = await complete_task_async(
                user_id=user_id,
                task_id=parameters.get("task_id"),
                session=session
            )
            return {"status": result.status, "message": result.message}

        elif tool_name == "delete_task":
            result = await delete_task_async(
                user_id=user_id,
                task_id=parameters.get("task_id"),
                session=session
            )
            return {"status": result.status, "message": result.message}

        elif tool_name == "update_task":
            result = await update_task_async(
                user_id=user_id,
                task_id=parameters.get("task_id"),
                title=parameters.get("title"),
                description=parameters.get("description"),
                session=session
            )
            return {"status": result.status, "message": result.message}

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        return {"error": str(e)}

async def process_chat_message(
    user_id: str,
    message: str,
    session: Session
) -> dict:
    """
    Process user message through AI and execute any tool calls.

    Returns:
        dict with 'response', 'conversation_id', 'tool_calls'
    """
    # Get or create conversation
    conversation = await get_or_create_conversation(user_id, session)

    # Load chat history
    history = await get_chat_history(conversation.id, session)

    # Save user message
    await save_message(conversation.id, MessageRole.USER, message, None, session)

    # Call Cohere
    ai_response = chat_with_tools(message, history, conversation.id)

    # Execute tool calls if any
    tool_results = []
    executed_tools = []

    if ai_response["tool_calls"]:
        for tool_call in ai_response["tool_calls"]:
            result = await execute_tool(
                tool_call["name"],
                tool_call["parameters"],
                user_id,
                session
            )
            tool_results.append({
                "call": tool_call,
                "outputs": [result]
            })
            executed_tools.append({
                "name": tool_call["name"],
                "result": result
            })

        # Continue conversation with tool results
        final_response = continue_with_tool_results(
            tool_results,
            ai_response["conversation_id"]
        )
        response_text = final_response["text"]
    else:
        response_text = ai_response["text"]

    # Save assistant response
    await save_message(
        conversation.id,
        MessageRole.ASSISTANT,
        response_text,
        {"tool_calls": executed_tools} if executed_tools else None,
        session
    )

    return {
        "response": response_text,
        "conversation_id": conversation.id,
        "tool_calls": executed_tools
    }
```

#### Task 1.4: Create Chat Router

**File**: `backend/app/routers/chat.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from typing import Optional

from app.database import get_session
from app.auth import get_current_user_id
from app.models import Conversation, Message, MessageRole
from app.services.chat_service import process_chat_message, get_chat_history

router = APIRouter(prefix="/api", tags=["chat"])

# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

class ToolCallInfo(BaseModel):
    name: str
    result: dict

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    tool_calls: Optional[list[ToolCallInfo]] = None

class MessageItem(BaseModel):
    id: str
    role: str
    content: str
    created_at: str

class ChatHistoryResponse(BaseModel):
    conversation_id: Optional[str]
    messages: list[MessageItem]
    total: int

class ClearHistoryResponse(BaseModel):
    message: str
    deleted_count: int

# Endpoints
@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Process chat message through AI chatbot.
    Supports natural language task management.
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
            tool_calls=result.get("tool_calls")
        )

    except Exception as e:
        # Log error but return friendly message
        print(f"Chat error: {e}")
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
    """Get conversation history for current user."""
    conversation = session.exec(
        select(Conversation).where(Conversation.user_id == current_user_id)
    ).first()

    if not conversation:
        return ChatHistoryResponse(
            conversation_id=None,
            messages=[],
            total=0
        )

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
            for msg in reversed(messages)
        ],
        total=len(messages)
    )

@router.delete("/chat/clear", response_model=ClearHistoryResponse)
async def clear_chat_history(
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Clear all messages in user's conversation."""
    conversation = session.exec(
        select(Conversation).where(Conversation.user_id == current_user_id)
    ).first()

    if not conversation:
        return ClearHistoryResponse(message="No history to clear", deleted_count=0)

    # Count and delete messages
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
```

#### Task 1.5: Register Router

**File**: `backend/app/main.py` (modify)

```python
# ADD import
from app.routers import chat

# ADD router registration (after existing routers)
app.include_router(chat.router)
```

---

### Phase 2: Frontend Chat UI (Priority: P0)

#### Task 2.1: Create Chat API Client

**File**: `frontend/src/lib/chat-api.ts`

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  tool_calls?: Array<{
    name: string;
    result: Record<string, unknown>;
  }>;
}

export interface ChatHistoryResponse {
  conversation_id: string | null;
  messages: ChatMessage[];
  total: number;
}

export async function sendChatMessage(
  message: string,
  token: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Chat request failed');
  }

  return response.json();
}

export async function getChatHistory(
  token: string,
  limit: number = 50
): Promise<ChatHistoryResponse> {
  const response = await fetch(
    `${API_BASE}/api/chat/history?limit=${limit}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error('Failed to load chat history');
  }

  return response.json();
}

export async function clearChatHistory(token: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/chat/clear`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to clear chat history');
  }
}
```

#### Task 2.2: Create ChatbotIcon Component

**File**: `frontend/src/components/chat/ChatbotIcon.tsx`

```typescript
'use client';

import { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import { ChatModal } from './ChatModal';

export function ChatbotIcon() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`
          fixed bottom-6 right-6 z-50
          w-14 h-14 rounded-full
          bg-gradient-to-r from-purple-600 to-blue-600
          hover:from-purple-700 hover:to-blue-700
          text-white shadow-lg
          flex items-center justify-center
          transition-all duration-300
          hover:scale-110 hover:shadow-xl
          ${isOpen ? 'hidden' : 'flex'}
        `}
        aria-label="Open chat"
      >
        <MessageCircle className="w-6 h-6" />
      </button>

      {/* Chat Modal */}
      {isOpen && (
        <ChatModal onClose={() => setIsOpen(false)} />
      )}
    </>
  );
}
```

#### Task 2.3: Create ChatModal Component

**File**: `frontend/src/components/chat/ChatModal.tsx`

```typescript
'use client';

import { useState, useEffect, useRef } from 'react';
import { X, Send, Loader2, Trash2 } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import {
  sendChatMessage,
  getChatHistory,
  clearChatHistory,
  ChatMessage,
} from '@/lib/chat-api';

interface ChatModalProps {
  onClose: () => void;
}

export function ChatModal({ onClose }: ChatModalProps) {
  const { token } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load history on mount
  useEffect(() => {
    if (token) {
      loadHistory();
    }
  }, [token]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadHistory = async () => {
    try {
      setIsLoadingHistory(true);
      const history = await getChatHistory(token!, 50);
      setMessages(history.messages);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading || !token) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(input.trim(), token);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Maaf kijiye, kuch problem ho gayi. Dobara try karein.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = async () => {
    if (!token) return;
    try {
      await clearChatHistory(token);
      setMessages([]);
    } catch (error) {
      console.error('Clear error:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 w-96 h-[32rem] flex flex-col bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
          <h3 className="font-semibold text-gray-900 dark:text-white">
            TodoAI Assistant
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleClear}
            className="p-2 text-gray-500 hover:text-red-500 transition-colors"
            title="Clear history"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {isLoadingHistory ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-6 h-6 animate-spin text-purple-600" />
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
            <p className="text-lg mb-2">Assalam o Alaikum! 👋</p>
            <p className="text-sm">
              Main TodoAI hoon. Tasks manage karne mein help karun?
            </p>
            <p className="text-xs mt-4 text-gray-400">
              Try: "mujhe grocery leni hai" or "show my tasks"
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] px-4 py-2 rounded-2xl ${
                  msg.role === 'user'
                    ? 'bg-purple-600 text-white rounded-br-md'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-bl-md'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-800 px-4 py-2 rounded-2xl rounded-bl-md">
              <Loader2 className="w-5 h-5 animate-spin text-purple-600" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 dark:text-white"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="p-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-full transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
```

#### Task 2.4: Create Index Export

**File**: `frontend/src/components/chat/index.ts`

```typescript
export { ChatbotIcon } from './ChatbotIcon';
export { ChatModal } from './ChatModal';
```

#### Task 2.5: Add to Layout

**File**: `frontend/src/app/(dashboard)/layout.tsx` (modify)

```typescript
// ADD import at top
import { ChatbotIcon } from '@/components/chat';

// ADD component before closing tag of return
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
      {/* existing content */}
      {children}

      {/* ADD: Floating chat icon */}
      <ChatbotIcon />
    </div>
  );
}
```

---

### Phase 3: Integration & Testing (Priority: P1)

#### Task 3.1: Add Cohere Dependency

**File**: `backend/requirements.txt` (add line)

```
cohere>=5.0.0
```

#### Task 3.2: Run Database Migration

```bash
cd backend

# Create tables (SQLModel auto-create)
python -c "
from app.database import engine
from app.models import Conversation, Message
from sqlmodel import SQLModel
SQLModel.metadata.create_all(engine)
print('Tables created!')
"
```

#### Task 3.3: Local Testing

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Test API
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

---

### Phase 4: Deployment (Priority: P1)

#### Task 4.1: Update Railway Environment

```bash
# Via Railway CLI or Dashboard
COHERE_API_KEY=sW7XFBBpDLE77rTergTCa2nL5oizsC458LA47cF8
```

#### Task 4.2: Deploy Backend

```bash
git add .
git commit -m "Add AI chatbot feature with Cohere integration"
git push origin 004-ai-chatbot-integration

# Merge to main for Railway auto-deploy
git checkout main
git merge 004-ai-chatbot-integration
git push origin main
```

#### Task 4.3: Deploy Frontend

Frontend auto-deploys on push to main (Vercel).

#### Task 4.4: Production Verification

```bash
# Test production endpoint
curl -X POST https://in-memory-python-todo-cli-app-production.up.railway.app/api/chat \
  -H "Authorization: Bearer PROD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

---

## Environment Variables

| Variable | Location | Value |
|----------|----------|-------|
| `COHERE_API_KEY` | Railway Backend | `sW7XFBBpDLE77rTergTCa2nL5oizsC458LA47cF8` |
| `NEXT_PUBLIC_API_URL` | Vercel Frontend | `https://in-memory-python-todo-cli-app-production.up.railway.app` |

---

## Deliverables Checklist

### Backend Files

- [ ] `backend/app/models.py` - Add Conversation, Message models
- [ ] `backend/app/services/cohere_client.py` - Cohere API wrapper
- [ ] `backend/app/services/chat_service.py` - Chat processing logic
- [ ] `backend/app/routers/chat.py` - API endpoints
- [ ] `backend/app/main.py` - Register chat router
- [ ] `backend/requirements.txt` - Add cohere dependency

### Frontend Files

- [ ] `frontend/src/lib/chat-api.ts` - API client
- [ ] `frontend/src/components/chat/ChatbotIcon.tsx` - Floating button
- [ ] `frontend/src/components/chat/ChatModal.tsx` - Chat interface
- [ ] `frontend/src/components/chat/index.ts` - Exports
- [ ] `frontend/src/app/(dashboard)/layout.tsx` - Add ChatbotIcon

### Documentation

- [x] `specs/004-ai-chatbot-integration/spec.md`
- [x] `specs/004-ai-chatbot-integration/plan.md`
- [x] `specs/004-ai-chatbot-integration/research.md`
- [x] `specs/004-ai-chatbot-integration/data-model.md`
- [x] `specs/004-ai-chatbot-integration/quickstart.md`
- [x] `specs/004-ai-chatbot-integration/contracts/chat-api.yaml`
- [ ] `specs/004-ai-chatbot-integration/tasks.md` (via /sp.tasks)

---

## Priority Order

| Priority | Phase | Tasks | Estimate |
|----------|-------|-------|----------|
| P0 | 1 | Backend models, Cohere client, chat service, router | Core |
| P0 | 2 | Frontend chat components, API client, layout integration | Core |
| P1 | 3 | Testing, verification | Integration |
| P1 | 4 | Railway + Vercel deployment | Deployment |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Cohere API rate limits | Implement retry with backoff |
| Long response times | Show loading indicator, timeout handling |
| Token expiry mid-chat | Detect 401, prompt re-login |
| Tool execution failures | Graceful error messages, don't crash |
| Context too long | Limit to 20 recent messages |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response time | <3s | Monitor API latency |
| Correct interpretation | 90% | Manual testing |
| UI responsiveness | <1s | Lighthouse audit |
| Error rate | <5% | Log monitoring |
| User adoption | 50% of active users | Analytics |

---

**Plan Complete** | Ready for `/sp.tasks` to generate implementation tasks

---

**Version**: 1.0.0 | **Created**: 2026-01-14 | **Branch**: 004-ai-chatbot-integration
