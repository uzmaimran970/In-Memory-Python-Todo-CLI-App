# Data Model: AI-Powered Todo Chatbot

**Feature**: 004-ai-chatbot-integration
**Date**: 2026-01-14
**Database**: Neon PostgreSQL via SQLModel

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE SCHEMA                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐         ┌──────────────────┐                     │
│   │    users     │         │   conversations  │                     │
│   │ (existing)   │◄────────│                  │                     │
│   ├──────────────┤   1:1   ├──────────────────┤                     │
│   │ id (PK)      │         │ id (PK, UUID)    │                     │
│   │ email        │         │ user_id (FK)     │                     │
│   │ name         │         │ created_at       │                     │
│   │ ...          │         │ updated_at       │                     │
│   └──────────────┘         └────────┬─────────┘                     │
│                                     │                                │
│                                     │ 1:N                            │
│                                     │                                │
│                            ┌────────▼─────────┐                     │
│                            │    messages      │                     │
│                            ├──────────────────┤                     │
│                            │ id (PK, UUID)    │                     │
│                            │ conversation_id  │                     │
│                            │ role (enum)      │                     │
│                            │ content (text)   │                     │
│                            │ tool_calls (JSON)│                     │
│                            │ created_at       │                     │
│                            └──────────────────┘                     │
│                                                                      │
│   ┌──────────────┐                                                  │
│   │    tasks     │ ◄─── Managed via MCP skills                      │
│   │ (existing)   │      (add_task, list_tasks, etc.)                │
│   ├──────────────┤                                                  │
│   │ id (PK)      │                                                  │
│   │ user_id (FK) │                                                  │
│   │ title        │                                                  │
│   │ description  │                                                  │
│   │ completed    │                                                  │
│   │ created_at   │                                                  │
│   │ updated_at   │                                                  │
│   └──────────────┘                                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## New Entities

### 1. Conversation

Represents a chat session between a user and the AI assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, auto-generated | Unique conversation identifier |
| `user_id` | String | FK → users.id, NOT NULL, UNIQUE | Owner of conversation |
| `created_at` | DateTime | NOT NULL, default=now() | When conversation started |
| `updated_at` | DateTime | NOT NULL, auto-update | Last activity timestamp |

**Business Rules**:
- Each user has exactly ONE active conversation (1:1 relationship)
- Conversation is created automatically on first chat message
- `updated_at` refreshes on every new message

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Unique conversation ID"
    )
    user_id: str = Field(
        foreign_key="user.id",
        unique=True,
        nullable=False,
        index=True,
        description="Owner user ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Conversation start time"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False,
        description="Last activity time"
    )

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

---

### 2. Message

Represents a single message in a conversation (user or assistant).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, auto-generated | Unique message identifier |
| `conversation_id` | UUID | FK → conversations.id, NOT NULL | Parent conversation |
| `role` | Enum | NOT NULL, values: user/assistant | Who sent the message |
| `content` | Text | NOT NULL | Message text content |
| `tool_calls` | JSON | NULL allowed | Tool calls made (if assistant) |
| `created_at` | DateTime | NOT NULL, default=now() | When message was sent |

**Business Rules**:
- Messages are immutable after creation (no updates)
- `role` determines message styling in UI
- `tool_calls` stores Cohere tool invocations for debugging
- Messages ordered by `created_at` for display

**SQLModel Definition**:
```python
from enum import Enum
from typing import Optional, Any

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Unique message ID"
    )
    conversation_id: str = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Parent conversation ID"
    )
    role: MessageRole = Field(
        nullable=False,
        description="Message sender role"
    )
    content: str = Field(
        nullable=False,
        description="Message text content"
    )
    tool_calls: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Tool calls made by assistant"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Message timestamp"
    )

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
```

---

## Existing Entities (Reference)

### User (No Changes)

Already exists in `backend/app/models.py`. Chat feature uses `user.id` for ownership.

### Task (No Changes)

Already exists in `backend/app/models.py`. Managed via existing MCP skills:
- `add_task` → Creates new Task
- `list_tasks` → Queries Tasks by user_id
- `complete_task` → Updates Task.completed
- `delete_task` → Removes Task
- `update_task` → Updates Task.title/description

---

## Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| conversations | idx_conv_user | user_id | Fast lookup by user |
| messages | idx_msg_conv | conversation_id | Fast message retrieval |
| messages | idx_msg_created | created_at | Chronological ordering |

**SQL Migration**:
```sql
-- Index for user conversation lookup
CREATE UNIQUE INDEX idx_conv_user ON conversations(user_id);

-- Index for message retrieval
CREATE INDEX idx_msg_conv ON messages(conversation_id);
CREATE INDEX idx_msg_created ON messages(created_at);
```

---

## State Transitions

### Conversation Lifecycle

```
┌─────────────┐     User sends      ┌─────────────┐
│   (none)    │────first message───►│   ACTIVE    │
└─────────────┘                     └──────┬──────┘
                                           │
                                    Each message
                                    updates updated_at
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │   ACTIVE    │◄─── Stays active
                                    └─────────────┘     indefinitely
```

### Message Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    MESSAGE FLOW                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Input         AI Processing         Tool Execution     │
│      │                    │                     │            │
│      ▼                    ▼                     ▼            │
│  ┌────────┐         ┌──────────┐         ┌──────────┐       │
│  │ USER   │────────►│ COHERE   │────────►│ MCP      │       │
│  │ MESSAGE│         │ CHAT API │         │ SKILLS   │       │
│  └────────┘         └────┬─────┘         └────┬─────┘       │
│                          │                    │              │
│                          ▼                    │              │
│                    ┌──────────┐               │              │
│                    │ASSISTANT │◄──────────────┘              │
│                    │ MESSAGE  │                              │
│                    └──────────┘                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Validation Rules

### Conversation

| Rule | Validation | Error Message |
|------|------------|---------------|
| user_id required | NOT NULL | "User ID is required" |
| user_id unique | UNIQUE constraint | "User already has conversation" |
| user exists | FK constraint | "User not found" |

### Message

| Rule | Validation | Error Message |
|------|------------|---------------|
| conversation_id required | NOT NULL | "Conversation ID required" |
| role valid | Enum check | "Invalid message role" |
| content not empty | len(content) > 0 | "Message cannot be empty" |
| content max length | len(content) <= 10000 | "Message too long" |

---

## Query Patterns

### Get or Create Conversation
```python
def get_or_create_conversation(user_id: str, session: Session) -> Conversation:
    conversation = session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    return conversation
```

### Get Recent Messages
```python
def get_recent_messages(conversation_id: str, limit: int = 20, session: Session) -> list[Message]:
    return session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()[::-1]  # Reverse for chronological order
```

### Save Message
```python
def save_message(
    conversation_id: str,
    role: MessageRole,
    content: str,
    tool_calls: dict | None = None,
    session: Session
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)

    # Update conversation timestamp
    session.exec(
        update(Conversation)
        .where(Conversation.id == conversation_id)
        .values(updated_at=datetime.utcnow())
    )

    session.commit()
    session.refresh(message)
    return message
```

---

## Migration Strategy

### Step 1: Create Tables
```bash
# Alembic migration (if using)
alembic revision --autogenerate -m "Add conversations and messages tables"
alembic upgrade head

# Or direct SQLModel creation
SQLModel.metadata.create_all(engine)
```

### Step 2: Verify Schema
```sql
-- Verify tables created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('conversations', 'messages');
```

### Rollback Plan
```sql
-- If needed, drop new tables (no existing data affected)
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;
```

---

**Data Model Complete** | Ready for API contracts
