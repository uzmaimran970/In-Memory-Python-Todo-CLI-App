---
id: 002
title: Initialize Hackathon Constitution
stage: constitution
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: pc
command: /sp.constitution
labels: ["constitution", "hackathon", "phase-ii", "spec-driven-development"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

# Hackathon Constitution
## Todo Application Evolution Challenge

### Project Overview
This hackathon challenges participants to evolve a simple Todo application across three distinct phases, demonstrating mastery of modern software development practices using an **Agentic Dev Stack** (spec-driven development with Claude Code and Spec-Kit Plus).

The application must progress as follows:
- **Phase I**: In-memory console application (completed)
- **Phase II**: Full-stack multi-user web application with persistent storage and authentication
- **Phase III**: AI-powered chatbot interface (future phase)

### Core Principles
All development must strictly follow these rules:

1. **No Manual Coding Allowed**
   Participants may NOT write or edit code directly. All implementation must be achieved through:
   - Writing or refining specifications
   - Generating plans
   - Breaking into tasks
   - Prompting Claude Code to implement based on specs

2. **Spec-Driven Development Mandatory**
   Every feature, change, or fix must originate from a written specification in the `/specs/` directory using Spec-Kit Plus conventions.

3. **Agentic Workflow Required**
   Use the full Agentic Dev Stack cycle:
   - Write/Update Spec → Generate Plan → Break into Tasks → Implement via Claude Code → Review → Iterate

4. **Clean Architecture & Best Practices**
   Code must follow professional standards:
   - Proper project structure
   - Type safety (TypeScript in frontend, Pydantic/SQLModel in backend)
   - Security best practices
   - Responsive, accessible UI
   - Error handling and validation

### Phase II Requirements (Current Phase)

#### Objective
Transform the Phase I console application into a modern, multi-user, full-stack web application with persistent storage.

#### Mandatory Features
- Implement all 5 basic CRUD operations as a secure web application:
  - Create task (title required, description optional)
  - View all tasks (with status indicators and filtering)
  - Update task details
  - Delete task
  - Mark task as complete/incomplete
- Full user authentication (signup/signin)
- Data persistence in Neon Serverless PostgreSQL
- User isolation (each user sees and modifies only their own tasks)

#### Technology Stack (Mandatory)
| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | Next.js 16+ (App Router), TypeScript, Tailwind CSS |
| Backend     | Python FastAPI                      |
| ORM         | SQLModel                            |
| Database    | Neon Serverless PostgreSQL          |
| Auth        | Better Auth with JWT tokens         |
| Development | Claude Code + Spec-Kit Plus         |

#### Security Requirements
- Better Auth configured to issue JWT tokens
- FastAPI backend must verify JWT tokens on every request
- Shared secret (BETTER_AUTH_SECRET) used in both services
- All API endpoints require valid JWT in Authorization header
- Task ownership strictly enforced (filter by authenticated user_id)
- Proper HTTP status codes (401, 403, 404, etc.)

#### Project Structure (Monorepo)
Must use monorepo structure with organized Spec-Kit folders.

## Response snapshot

Successfully created comprehensive constitution for Todo Application Evolution Challenge hackathon. The constitution defines:

**7 Core Principles**:
1. No Manual Coding (NON-NEGOTIABLE) - All work through specs and AI agents
2. Spec-Driven Development Mandatory - Every change starts with a spec
3. Agentic Workflow Required - Follow full Specify→Plan→Tasks→Implement→Review cycle
4. Clean Architecture & Best Practices - Professional code standards enforced
5. User Isolation & Multi-Tenancy - Strict data separation between users
6. Incremental Delivery via User Stories - Each story independently testable
7. Documentation & Traceability - PHRs and ADRs for all decisions

**Technology Stack Requirements**:
- Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- Backend: Python FastAPI, SQLModel
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth with JWT tokens
- Development: Claude Code + Spec-Kit Plus

**Security & Architecture Standards**:
- Detailed authentication flow (Better Auth → JWT → Backend verification)
- Database schema requirements (Users and Tasks tables with proper constraints)
- API endpoint contracts (6 required endpoints with ownership verification)
- Complete monorepo project structure

**Governance**:
- Amendment process with semantic versioning
- Compliance verification requirements
- Complexity justification guidelines
- Runtime guidance references

## Outcome

- ✅ Impact: Created version 1.0.0 of project constitution defining all hackathon requirements, principles, and standards
- 🧪 Tests: N/A (constitution document, no code)
- 📁 Files: Created/updated .specify/memory/constitution.md with complete hackathon requirements
- 🔁 Next prompts: Create Phase II feature specification using /sp.specify, then run /sp.plan for architectural design
- 🧠 Reflection: Constitution successfully captures all hackathon requirements including mandatory no-manual-coding rule, full tech stack, security requirements, and project structure. Templates (spec, plan, tasks) already align with constitution principles.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution template filled successfully
- Graders run and results (PASS/FAIL): Template validation PASS (all placeholders replaced, no TODO fields)
- Prompt variant (if applicable): N/A (initial constitution creation)
- Next experiment (smallest change to try): Begin Phase II spec creation to validate constitution guidance effectiveness
