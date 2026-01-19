---
id: 003
title: Create TodoAI Chatbot Constitution
stage: constitution
date: 2026-01-14
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: uzma
command: /sp.constitution
labels: ["constitution", "todoai", "ai-chatbot", "mcp-skills", "phase3"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

User ran /sp.constitution command with detailed TodoAI chatbot specifications:

"You are TodoAI, a highly intelligent and powerful AI chatbot for a full-stack Todo application. Your constitution is to be the ultimate task manager: helpful, friendly, accurate, and secure.

Core Principles:
1. User-Centric and Friendly - Roman Urdu/Hinglish support, warm communication
2. Full Functionality - 5 MCP skills (add_task, list_tasks, complete_task, delete_task, update_task)
3. Security and Privacy - JWT authentication, ownership checks, no data leakage
4. AI Power with Cohere and OpenAI Agent Style - Cohere API, multi-step reasoning, tool calling
5. Stateless and Scalable - FastAPI stateless operation, Neon PostgreSQL for persistence
6. Error Handling - User-friendly errors in Roman Urdu
7. Performance - <500ms response time target

Technical Stack: FastAPI, SQLModel, Neon PostgreSQL, Better Auth (JWT), Cohere API, OpenAI Agent SDK patterns"

## Response snapshot

Created comprehensive TodoAI constitution at `.specify/memory/constitution.md` with:

- 7 Core Principles fully documented with implementation details
- Technology Stack table (FastAPI, SQLModel, Neon PostgreSQL, Better Auth, Cohere, Railway/Vercel)
- Development Workflow for MCP skill creation
- Code Quality Gates for compliance
- Governance rules including amendment process and compliance requirements
- Version: 1.0.0, Ratified: 2026-01-14

Key sections:
- User-Centric approach with Roman Urdu/Hinglish support
- Full Task Management via 5 MCP skills
- Security with JWT and ownership enforcement
- AI capabilities with Cohere and Agent SDK patterns
- Stateless scalable architecture
- Error handling with friendly messages
- Performance targets

## Outcome

- Impact: Established authoritative constitution for TodoAI chatbot development
- Tests: N/A (documentation artifact)
- Files: 1 file modified (.specify/memory/constitution.md)
- Next prompts: Implement AI chat endpoint, integrate Cohere API, create conversation management
- Reflection: Constitution provides clear guidelines for Phase 3 AI features. All 7 principles documented with actionable requirements.

## Evaluation notes (flywheel)

- Failure modes observed: None - template filled successfully
- Graders run and results (PASS/FAIL): Manual review - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution principles during MCP skill implementation
