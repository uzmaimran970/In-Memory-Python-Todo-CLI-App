# Research: AI-Powered Todo Chatbot Integration

**Feature**: 004-ai-chatbot-integration
**Date**: 2026-01-14
**Status**: Complete

---

## 1. Cohere API Integration

### Decision: Use Cohere Chat API with Tool Use

**Rationale**:
- Cohere's Chat API natively supports tool calling (similar to OpenAI function calling)
- `command-r-plus` model excels at multi-step reasoning and tool orchestration
- Native support for multilingual responses (English + Roman Urdu)
- Cost-effective compared to alternatives

**Alternatives Considered**:
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| OpenAI GPT-4 | Better NLU | Higher cost, different API | User specified Cohere |
| Anthropic Claude | Strong reasoning | Different tool format | User specified Cohere |
| Local LLM | No API costs | High infra, slower | Not feasible for Railway |

**Implementation Pattern**:
```python
import cohere

co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

# Tool definitions for MCP skills
tools = [
    {
        "name": "add_task",
        "description": "Create a new task for the user",
        "parameters": {...}
    },
    # ... other tools
]

# Chat with tool use
response = co.chat(
    model="command-r-plus",
    message=user_message,
    conversation_id=conversation_id,
    tools=tools,
    preamble="You are TodoAI, a helpful task manager..."
)
```

---

## 2. Conversation Persistence Strategy

### Decision: SQLModel with Conversation + Message Tables

**Rationale**:
- Consistent with existing SQLModel/Neon PostgreSQL stack
- Simple schema supports stateless operation
- Each user has one active conversation (simplified model)
- Messages stored with role (user/assistant) for context replay

**Alternatives Considered**:
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Redis | Fast in-memory | Data loss risk, extra infra | Complexity not justified |
| File-based | Simple | Not scalable, no queries | Poor for production |
| External service | Managed | Cost, dependency | Over-engineering |

**Schema Design**:
```
conversations
├── id (UUID)
├── user_id (FK → users)
├── created_at (timestamp)
└── updated_at (timestamp)

messages
├── id (UUID)
├── conversation_id (FK → conversations)
├── role (enum: user/assistant)
├── content (text)
└── created_at (timestamp)
```

---

## 3. Frontend Chat UI Architecture

### Decision: Custom Modal with Tailwind CSS

**Rationale**:
- Full control over styling and behavior
- Consistent with existing Tailwind setup
- No additional dependencies (ChatKit adds complexity)
- Floating icon pattern is well-established UX

**Alternatives Considered**:
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| ChatKit | Pre-built components | Heavy dependency, style conflicts | Over-engineering |
| Stream Chat | Real-time features | Overkill for AI chat, cost | Not needed |
| Headless UI Dialog | Accessible | Still need custom styling | Minimal benefit |

**Component Structure**:
```
frontend/src/components/
├── chat/
│   ├── ChatbotIcon.tsx      # Floating FAB button
│   ├── ChatModal.tsx        # Modal container
│   ├── ChatMessages.tsx     # Message list with scroll
│   ├── ChatInput.tsx        # Input + send button
│   └── MessageBubble.tsx    # Individual message styling
```

---

## 4. Agent Architecture Pattern

### Decision: Function-Based Routing (Not Class Agents)

**Rationale**:
- Simpler than full agent SDK implementation
- Cohere handles multi-step reasoning internally
- MCP skills already exist as functions
- Faster development, easier debugging

**Alternatives Considered**:
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| LangChain Agents | Full framework | Heavy, learning curve | Over-engineering |
| OpenAI Agent SDK | Native agents | Wrong API (Cohere specified) | Incompatible |
| Custom Agent Classes | OOP patterns | More code, indirection | YAGNI |

**Implementation Pattern**:
```python
# Instead of agent classes, use Cohere tools + dispatcher

async def process_chat_message(user_id: str, message: str, session: Session):
    # 1. Load conversation history
    history = load_conversation(user_id, session)

    # 2. Call Cohere with tools
    response = co.chat(
        message=message,
        tools=MCP_TOOLS,
        chat_history=history
    )

    # 3. Execute tool calls if any
    if response.tool_calls:
        for tool_call in response.tool_calls:
            result = execute_mcp_skill(tool_call, user_id, session)
            # Continue conversation with tool result

    # 4. Save messages and return
    save_message(user_id, "user", message, session)
    save_message(user_id, "assistant", response.text, session)
    return response.text
```

---

## 5. Authentication Flow

### Decision: JWT in Authorization Header

**Rationale**:
- Consistent with existing Better Auth setup
- Standard pattern for API requests
- Already implemented for task endpoints
- No new auth mechanism needed

**Flow**:
```
Frontend                Backend
   │                       │
   ├─── POST /api/chat ───►│
   │    Authorization:     │
   │    Bearer {jwt}       │
   │                       ├── Validate JWT
   │                       ├── Extract user_id
   │                       ├── Process message
   │◄── Response ──────────┤
```

---

## 6. Error Handling Strategy

### Decision: Graceful Degradation with User-Friendly Messages

**Rationale**:
- Constitution mandates friendly errors
- Users should never see technical errors
- Fallback responses for AI service failures
- Log errors for debugging, show friendly message to user

**Error Categories**:
| Error | User Message | Log Level |
|-------|--------------|-----------|
| JWT Invalid | "Please login again" | WARN |
| Cohere API Error | "AI busy, try again" | ERROR |
| Task Not Found | "Task nahi mila" | INFO |
| Rate Limited | "Thoda ruko, bohot fast ho" | WARN |
| Database Error | "Technical issue, try later" | ERROR |

---

## 7. Language Detection

### Decision: Cohere-Based Detection via Preamble

**Rationale**:
- Cohere models understand context and can detect language
- Preamble instruction handles language matching
- No separate language detection API needed
- Simpler than external language detection services

**Preamble Configuration**:
```python
SYSTEM_PREAMBLE = """
You are TodoAI, a friendly task manager assistant.

LANGUAGE RULES:
- If user writes in Roman Urdu/Hinglish, respond in Roman Urdu
- If user writes in English, respond in English
- Be warm, helpful, and encouraging
- Use "aap" (respectful) not "tum" for users

CAPABILITIES:
- add_task: Create new tasks
- list_tasks: Show user's tasks
- complete_task: Mark tasks done
- delete_task: Remove tasks (ask confirmation)
- update_task: Edit task details
"""
```

---

## 8. Performance Optimization

### Decision: Conversation Context Window of 20 Messages

**Rationale**:
- Full history too large for API context
- Last 20 messages sufficient for continuity
- Reduces API costs and latency
- Matches typical user session length

**Implementation**:
```python
def load_recent_messages(conversation_id: str, limit: int = 20):
    return session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()[::-1]  # Reverse to chronological order
```

---

## 9. Deployment Strategy

### Decision: Same Railway + Vercel Setup

**Rationale**:
- Existing infrastructure proven working
- No additional costs or complexity
- Environment variables already configured
- Just add COHERE_API_KEY to Railway

**Steps**:
1. Add `COHERE_API_KEY` to Railway environment
2. Deploy backend with new chat endpoint
3. Deploy frontend with chat components
4. Test end-to-end

---

## Research Complete

All technical decisions documented. Ready for Phase 1 design artifacts.

**Next Step**: Create data-model.md and API contracts
