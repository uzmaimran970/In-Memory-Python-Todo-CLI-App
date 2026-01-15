# Tasks: AI-Powered Todo Chatbot Integration

**Input**: Design documents from `/specs/004-ai-chatbot-integration/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md
**Branch**: `004-ai-chatbot-integration`
**Tests**: Not explicitly requested - implementation tasks only

**Organization**: Tasks grouped by user story (7 user stories from spec.md)

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US7) - Setup/Foundational have no story label
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add dependencies and create folder structure

- [x] T001 Add `cohere>=5.0.0` to backend/requirements.txt
- [x] T002 [P] Create backend/app/services/ directory (if not exists)
- [x] T003 [P] Create frontend/src/components/chat/ directory
- [x] T004 [P] Create frontend/src/lib/chat-api.ts file (empty placeholder)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database models and Cohere client that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Add MessageRole enum and Conversation model to backend/app/models.py
- [x] T006 Add Message model with tool_calls JSON field to backend/app/models.py
- [x] T007 Create Cohere client wrapper with SYSTEM_PREAMBLE in backend/app/services/cohere_client.py
- [x] T008 Define MCP_TOOLS array with all 5 tool definitions in backend/app/services/cohere_client.py
- [x] T009 Implement chat_with_tools() function in backend/app/services/cohere_client.py
- [x] T010 Implement continue_with_tool_results() function in backend/app/services/cohere_client.py
- [x] T011 Create chat service with get_or_create_conversation() in backend/app/services/chat_service.py
- [x] T012 Implement get_chat_history() function in backend/app/services/chat_service.py
- [x] T013 Implement save_message() function in backend/app/services/chat_service.py
- [x] T014 Implement execute_tool() dispatcher for MCP skills in backend/app/services/chat_service.py
- [x] T015 Implement process_chat_message() main function in backend/app/services/chat_service.py
- [x] T016 Run database migration to create conversations and messages tables

**Checkpoint**: Foundation ready - Cohere integration and database ready for API endpoints

---

## Phase 3: User Story 6 - Chat Interface Access (Priority: P1)

**Goal**: User can access chat interface from floating icon on dashboard

**Independent Test**: Verify floating icon appears on authenticated pages, opens modal on click

**Why First**: This is the UI gateway - without accessible chat, no other stories work

### Implementation for User Story 6

- [x] T017 [P] [US6] Create ChatbotIcon component with floating button in frontend/src/components/chat/ChatbotIcon.tsx
- [x] T018 [P] [US6] Create ChatModal container component in frontend/src/components/chat/ChatModal.tsx
- [x] T019 [P] [US6] Create chat API client with sendChatMessage() in frontend/src/lib/chat-api.ts
- [x] T020 [P] [US6] Add getChatHistory() to frontend/src/lib/chat-api.ts
- [x] T021 [P] [US6] Add clearChatHistory() to frontend/src/lib/chat-api.ts
- [x] T022 [US6] Create chat component index exports in frontend/src/components/chat/index.ts
- [x] T023 [US6] Add ChatbotIcon to dashboard layout in frontend/src/app/dashboard/page.tsx
- [x] T024 [US6] Implement modal open/close state management in ChatbotIcon.tsx
- [x] T025 [US6] Add loading indicator for chat history in ChatModal.tsx
- [x] T026 [US6] Add empty state with greeting message in ChatModal.tsx
- [x] T027 [US6] Style chat modal for dark mode support in ChatModal.tsx

**Checkpoint**: Floating icon visible, modal opens/closes, ready for messages

---

## Phase 4: User Story 1 - Basic Task Creation via Chat (Priority: P1) - MVP

**Goal**: User creates tasks through natural language like "add task buy milk" or "mujhe grocery leni hai"

**Independent Test**: Send task creation message, verify task appears in task list

### Implementation for User Story 1

- [x] T028 [US1] Create chat router with POST /api/chat endpoint in backend/app/routers/chat.py
- [x] T029 [US1] Define ChatRequest and ChatResponse Pydantic models in backend/app/routers/chat.py
- [x] T030 [US1] Implement send_chat_message() endpoint handler in backend/app/routers/chat.py
- [x] T031 [US1] Register chat router in backend/app/main.py
- [x] T032 [US1] Implement message input field with send button in ChatModal.tsx
- [x] T033 [US1] Handle Enter key to send message in ChatModal.tsx
- [x] T034 [US1] Display user messages with right-aligned styling in ChatModal.tsx
- [x] T035 [US1] Display assistant responses with left-aligned styling in ChatModal.tsx
- [x] T036 [US1] Auto-scroll to latest message in ChatModal.tsx
- [x] T037 [US1] Show loading spinner while waiting for AI response in ChatModal.tsx
- [x] T038 [US1] Handle API errors with friendly message in ChatModal.tsx

**Checkpoint**: Users can create tasks via chat - MVP complete!

---

## Phase 5: User Story 2 - View and Query Tasks via Chat (Priority: P1)

**Goal**: User views tasks by asking "show my tasks" or "mere kitne tasks hain?"

**Independent Test**: Ask for tasks, verify response matches actual task list

### Implementation for User Story 2

- [x] T039 [US2] Ensure list_tasks tool is properly mapped in execute_tool() in backend/app/services/chat_service.py
- [x] T040 [US2] Format task list responses in chat for readability
- [x] T041 [US2] Handle empty task list case with helpful suggestion
- [x] T042 [US2] Support status filtering (pending/completed/all) in list_tasks

**Checkpoint**: Users can view and query their tasks via chat

---

## Phase 6: User Story 3 - Complete Tasks via Chat (Priority: P2)

**Goal**: User marks tasks complete by saying "complete task 1" or "task 2 done kar do"

**Independent Test**: Say "complete task X", verify task status changes in database

### Implementation for User Story 3

- [x] T043 [US3] Ensure complete_task tool is properly mapped in execute_tool() in backend/app/services/chat_service.py
- [x] T044 [US3] Handle task already completed case
- [x] T045 [US3] Handle task not found case with friendly message
- [x] T046 [US3] Confirm completion with task title in response

**Checkpoint**: Users can complete tasks via chat

---

## Phase 7: User Story 4 - Delete Tasks via Chat (Priority: P2)

**Goal**: User deletes tasks with confirmation via "delete task 1" or "task 2 hata do"

**Independent Test**: Request deletion, confirm, verify task removed from database

### Implementation for User Story 4

- [x] T047 [US4] Ensure delete_task tool is properly mapped in execute_tool() in backend/app/services/chat_service.py
- [x] T048 [US4] Implement confirmation flow in SYSTEM_PREAMBLE for delete operations
- [x] T049 [US4] Handle task not found case
- [x] T050 [US4] Confirm deletion with task title in response

**Checkpoint**: Users can delete tasks with confirmation via chat

---

## Phase 8: User Story 5 - Update Tasks via Chat (Priority: P2)

**Goal**: User updates task title/description via "change task 1 title to X"

**Independent Test**: Request title change, verify update in database

### Implementation for User Story 5

- [x] T051 [US5] Ensure update_task tool is properly mapped in execute_tool() in backend/app/services/chat_service.py
- [x] T052 [US5] Handle missing update parameters with clarifying question
- [x] T053 [US5] Handle task not found case
- [x] T054 [US5] Confirm update with old/new values in response

**Checkpoint**: Users can update tasks via chat

---

## Phase 9: User Story 7 - User Profile Information via Chat (Priority: P3)

**Goal**: User asks "mera naam kya hai?" or "mere kitne pending tasks hain?"

**Independent Test**: Ask profile question, verify correct user info returned

### Implementation for User Story 7

- [x] T055 [US7] Add get_user_info tool definition to MCP_TOOLS in backend/app/services/cohere_client.py
- [x] T056 [US7] Implement get_user_info in execute_tool() in backend/app/services/chat_service.py
- [x] T057 [US7] Return user name, email, task counts in user info response
- [x] T058 [US7] Support task statistics queries (pending count, completed count)

**Checkpoint**: Users can query their profile and task statistics

---

## Phase 10: Chat History Management

**Purpose**: Conversation persistence and history viewing

- [x] T059 Implement GET /api/chat/history endpoint in backend/app/routers/chat.py
- [x] T060 Define ChatHistoryResponse model in backend/app/routers/chat.py
- [x] T061 Implement DELETE /api/chat/clear endpoint in backend/app/routers/chat.py
- [x] T062 Load conversation history on modal open in ChatModal.tsx
- [x] T063 Add clear history button to ChatModal.tsx header
- [x] T064 Display historical messages on modal open

**Checkpoint**: Chat history persists across sessions

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, performance, deployment

- [ ] T065 [P] Add rate limiting for chat endpoint (optional - skipped for MVP)
- [x] T066 [P] Add request logging for chat endpoint in backend/app/routers/chat.py
- [x] T067 [P] Handle Cohere API timeout with retry (in cohere_client.py try/except)
- [x] T068 [P] Handle JWT expiry mid-chat with re-login prompt (in chat-api.ts)
- [x] T069 [P] Add mobile responsive styles to ChatModal.tsx
- [ ] T070 [P] Add COHERE_API_KEY to Railway environment variables (MANUAL - user action required)
- [ ] T071 Deploy backend to Railway (push to main branch) (MANUAL - user action required)
- [ ] T072 Deploy frontend to Vercel (push to main branch) (MANUAL - user action required)
- [ ] T073 Run quickstart.md verification checklist in production (MANUAL - user action required)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────► Phase 2 (Foundational) ─────────┐
                                                            │
                    ┌───────────────────────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │ US6: Chat UI  │ (Gateway - must be first)
            └───────┬───────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    ┌───────┐   ┌───────┐   (US3-US5 can wait)
    │ US1:  │   │ US2:  │
    │Create │   │ View  │
    └───────┘   └───────┘
        │           │
        └─────┬─────┘
              │
              ▼
        ┌───────────┐
        │US3-5: CRUD│
        └───────────┘
              │
              ▼
        ┌───────────┐
        │ US7: Info │
        └───────────┘
              │
              ▼
        ┌───────────┐
        │ History + │
        │  Polish   │
        └───────────┘
```

### User Story Dependencies

- **US6 (Chat Interface)**: Gateway - must complete before any other story can be tested
- **US1 (Create Tasks)**: Depends on US6, no other story dependencies
- **US2 (View Tasks)**: Depends on US6, can run parallel to US1
- **US3-US5 (Complete/Delete/Update)**: Depend on US6, can run parallel to each other
- **US7 (User Info)**: Depends on US6, independent of US1-US5

### Parallel Opportunities per Phase

**Phase 2 (Foundational)**:
```
T005, T006 (models) can run in sequence in same file
T007, T008, T009, T010 can run in sequence in same file
T011, T012, T013, T014, T015 can run in sequence in same file
```

**Phase 3 (US6 - Chat UI)**:
```bash
# These can run in parallel (different files):
T017: ChatbotIcon.tsx
T018: ChatModal.tsx
T019, T020, T021: chat-api.ts
```

**Phase 4 (US1 - Create Tasks)**:
```bash
# Backend and Frontend can run in parallel:
Backend: T028, T029, T030, T031 (chat.py, main.py)
Frontend: T032-T038 (ChatModal.tsx updates)
```

---

## Implementation Strategy

### MVP First (US6 + US1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (models, Cohere client, chat service)
3. Complete Phase 3: US6 (Chat UI - gateway)
4. Complete Phase 4: US1 (Create Tasks)
5. **STOP and VALIDATE**: Test creating tasks via chat
6. Deploy if ready - this is MVP!

### Incremental Delivery

1. MVP: US6 + US1 → Users can open chat and create tasks
2. +US2: Users can view their tasks via chat
3. +US3-US5: Full CRUD operations via chat
4. +US7: User profile queries
5. +History: Persistent conversations

### Task Count Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Phase 1 | 4 | Setup |
| Phase 2 | 12 | Foundational |
| Phase 3 (US6) | 11 | Chat Interface |
| Phase 4 (US1) | 11 | Create Tasks (MVP) |
| Phase 5 (US2) | 4 | View Tasks |
| Phase 6 (US3) | 4 | Complete Tasks |
| Phase 7 (US4) | 4 | Delete Tasks |
| Phase 8 (US5) | 4 | Update Tasks |
| Phase 9 (US7) | 4 | User Info |
| Phase 10 | 6 | Chat History |
| Phase 11 | 9 | Polish & Deploy |
| **Total** | **73** | |

### MVP Scope

- **Minimum Tasks for MVP**: T001-T038 (38 tasks)
- **MVP Deliverable**: Floating chat icon, create tasks via natural language
- **MVP User Stories**: US6 + US1

---

## Notes

- All tasks include exact file paths for immediate execution
- [P] tasks can run in parallel within same phase
- [USx] labels map to spec.md user stories
- US6 is gateway - blocks all other stories
- Commit after each phase completion
- Run quickstart.md checklist before deployment

---

**Generated**: 2026-01-15 | **Branch**: 004-ai-chatbot-integration | **Total Tasks**: 73
