<!--
Sync Impact Report:
Version: 1.0.0 → 1.0.0 (Initial constitution for hackathon)
Modified Principles: N/A (first version)
Added Sections:
  - Core Principles (7 principles for spec-driven agentic workflow)
  - Technology Stack Requirements
  - Security & Architecture Standards
  - Governance
Templates Status:
  ✅ plan-template.md - Constitution Check section ready for Phase II requirements
  ✅ spec-template.md - User story prioritization aligns with hackathon incremental approach
  ✅ tasks-template.md - Phase-based organization matches hackathon structure
Follow-up TODOs: None
-->

# Todo Application Evolution Challenge Constitution

## Core Principles

### I. No Manual Coding (NON-NEGOTIABLE)

Participants MUST NOT write or edit code directly. All implementation must be achieved exclusively through:
- Writing or refining specifications in `/specs/` directory
- Generating architectural plans via `/sp.plan`
- Breaking work into tasks via `/sp.tasks`
- Prompting Claude Code agents to implement based on specs

**Rationale**: This hackathon validates the Agentic Dev Stack workflow. Manual coding undermines the core learning objective and disqualifies submissions.

### II. Spec-Driven Development Mandatory

Every feature, change, bug fix, or modification MUST originate from a written specification in `/specs/` following Spec-Kit Plus conventions.

Requirements:
- Specifications MUST precede implementation
- Specifications MUST include user stories with acceptance scenarios
- Specifications MUST define measurable success criteria
- Specifications MUST be technology-agnostic (focus on "what", not "how")

**Rationale**: Specifications provide clear contracts between intention and implementation, enabling AI agents to work autonomously and preventing scope creep.

### III. Agentic Workflow Required

MUST follow the complete Agentic Dev Stack cycle for all work:

1. **Specify** (`/sp.specify`): Write/update feature specification
2. **Plan** (`/sp.plan`): Generate architectural design and research
3. **Tasks** (`/sp.tasks`): Break plan into atomic, testable tasks
4. **Implement** (`/sp.implement`): Execute via Claude Code specialized agents
5. **Review**: Validate against acceptance criteria
6. **Iterate**: Refine specs and repeat as needed

**Rationale**: This workflow ensures traceability, enables incremental delivery, and teaches systematic software development practices.

### IV. Clean Architecture & Best Practices

Code MUST follow professional standards:

**Structure**:
- Monorepo with clear separation: `backend/`, `frontend/`
- Each layer isolated: models, services, API, UI components
- No business logic in presentation layer
- No UI concerns in business logic

**Type Safety**:
- TypeScript in frontend (strict mode enabled)
- Pydantic/SQLModel in backend
- All public APIs fully typed

**Security**:
- JWT token verification on every backend request
- User isolation enforced at database query level
- No secrets in code (use environment variables)
- Input validation and sanitization
- Proper HTTP status codes (401, 403, 404, 500)

**Quality**:
- Responsive, accessible UI (WCAG 2.1 AA minimum)
- Comprehensive error handling with user-friendly messages
- Proper logging for debugging
- Clear, self-documenting code

**Rationale**: Professional-grade code is required for Phase II evaluation. Clean architecture enables maintainability and future AI chatbot integration (Phase III).

### V. User Isolation & Multi-Tenancy

MUST enforce strict data isolation between users:

- Every task MUST be associated with a `user_id`
- All database queries MUST filter by authenticated user's ID
- API endpoints MUST return 403 Forbidden for unauthorized access attempts
- Users MUST NOT be able to view, modify, or delete other users' tasks

**Rationale**: Multi-user support is a Phase II requirement. Security violations disqualify submissions.

### VI. Incremental Delivery via User Stories

Features MUST be developed as independently testable user stories:

- Each user story prioritized (P1, P2, P3, etc.)
- User Story 1 (P1) MUST deliver a viable MVP
- Each story MUST be testable independently
- Each story MUST add value without breaking previous stories

**Rationale**: Incremental delivery demonstrates ability to ship value iteratively, a core skill for production software development.

### VII. Documentation & Traceability

All decisions and work MUST be documented:

**Prompt History Records (PHRs)**:
- Create PHR after every significant interaction
- Route constitution changes to `history/prompts/constitution/`
- Route feature work to `history/prompts/<feature-name>/`
- Route general work to `history/prompts/general/`
- PHRs MUST include full user input (verbatim, not truncated)

**Architecture Decision Records (ADRs)**:
- When significant architectural decisions are made, suggest ADR creation
- Require user consent before creating ADR
- ADRs MUST document: context, options considered, decision, consequences

**Rationale**: Documentation enables knowledge transfer, supports iterative refinement, and provides audit trail for hackathon evaluation.

## Technology Stack Requirements

Phase II MUST use the following mandatory technologies:

| Layer       | Technology                                  | Version   |
|-------------|---------------------------------------------|-----------|
| Frontend    | Next.js (App Router)                       | 16+       |
| Frontend    | TypeScript                                  | 5.0+      |
| Frontend    | Tailwind CSS                                | 3.4+      |
| Backend     | Python FastAPI                              | 0.100+    |
| ORM         | SQLModel                                    | 0.0.14+   |
| Database    | Neon Serverless PostgreSQL                  | Latest    |
| Auth        | Better Auth (with JWT tokens)               | Latest    |
| Development | Claude Code + Spec-Kit Plus                 | Latest    |

**Shared Authentication Secret**:
- `BETTER_AUTH_SECRET` MUST be shared between frontend and backend
- Backend MUST verify JWT signature using this secret
- Frontend MUST send JWT in `Authorization: Bearer <token>` header

**Rationale**: Standardized stack enables fair evaluation and ensures compatibility with judging infrastructure.

## Security & Architecture Standards

### Authentication Flow

1. **User Registration** (Better Auth):
   - Frontend sends credentials to Better Auth
   - Better Auth creates user and issues JWT token
   - Token stored in frontend (secure cookie or localStorage)

2. **Protected API Requests**:
   - Frontend includes JWT in Authorization header: `Bearer <token>`
   - Backend extracts and verifies JWT signature
   - Backend extracts `user_id` from verified token
   - Backend filters all queries by `user_id`

3. **Error Responses**:
   - `401 Unauthorized`: Missing or invalid JWT token
   - `403 Forbidden`: Valid token but accessing another user's resource
   - `404 Not Found`: Resource doesn't exist for authenticated user

### Database Schema Requirements

**Users Table**:
- `id` (primary key, auto-generated)
- `email` (unique, indexed)
- `password_hash` (hashed, never plain text)
- `created_at`, `updated_at` (timestamps)

**Tasks Table**:
- `id` (primary key, auto-generated)
- `user_id` (foreign key to users.id, indexed, NOT NULL)
- `title` (varchar, required, max 200 chars)
- `description` (text, optional, max 1000 chars)
- `is_completed` (boolean, default false)
- `created_at`, `updated_at` (timestamps)

**Constraints**:
- Composite index on `(user_id, id)` for fast user-scoped lookups
- Foreign key constraint on `user_id` with CASCADE delete

### API Endpoint Contracts

All CRUD endpoints MUST:
- Accept JWT in Authorization header
- Return JSON responses
- Filter by authenticated user_id
- Handle errors gracefully
- Return appropriate HTTP status codes

**Required Endpoints**:
- `POST /api/tasks` - Create task (title required, description optional)
- `GET /api/tasks` - List all tasks for authenticated user
- `GET /api/tasks/{id}` - Get single task (verify ownership)
- `PATCH /api/tasks/{id}` - Update task (verify ownership)
- `DELETE /api/tasks/{id}` - Delete task (verify ownership)
- `PATCH /api/tasks/{id}/toggle` - Toggle completion status (verify ownership)

### Project Structure (Monorepo)

```
todo_hackathon2/
├── .specify/                    # Spec-Kit Plus configuration
│   ├── memory/
│   │   └── constitution.md      # This file
│   ├── templates/               # Spec/plan/task templates
│   └── scripts/                 # Automation scripts
├── specs/                       # Feature specifications
│   ├── 001-todo-console-app/    # Phase I (completed)
│   └── 002-fullstack-webapp/    # Phase II (current)
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── research.md
│       ├── data-model.md
│       └── contracts/
├── history/
│   ├── prompts/                 # Prompt History Records
│   │   ├── constitution/
│   │   ├── <feature-name>/
│   │   └── general/
│   └── adr/                     # Architecture Decision Records
├── backend/
│   ├── src/
│   │   ├── models/              # SQLModel entities
│   │   ├── services/            # Business logic
│   │   ├── api/                 # FastAPI routes
│   │   └── auth/                # JWT verification middleware
│   ├── tests/
│   │   ├── contract/
│   │   ├── integration/
│   │   └── unit/
│   ├── alembic/                 # Database migrations
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   ├── components/          # React components
│   │   ├── lib/                 # Utilities and API client
│   │   └── types/               # TypeScript types
│   ├── public/
│   ├── package.json
│   └── .env.local.example
├── README.md
└── docker-compose.yml           # Local development environment
```

## Governance

### Amendment Process

This constitution supersedes all other practices and conventions.

**Amendments require**:
1. Documentation of proposed change with rationale
2. Impact analysis on existing specs, plans, and tasks
3. User approval (for hackathon: participant decision)
4. Version increment following semantic versioning:
   - **MAJOR**: Backward-incompatible principle removals or redefinitions
   - **MINOR**: New principle/section added or materially expanded
   - **PATCH**: Clarifications, wording fixes, non-semantic refinements
5. Migration plan for affected artifacts
6. Updated Sync Impact Report (HTML comment at top of this file)

### Compliance Verification

All PRs, commits, and implementations MUST:
- Verify compliance with constitution principles
- Reference source specification in commit messages
- Include traceability to user story and acceptance criteria
- Pass constitution checks defined in plan-template.md

### Complexity Justification

Any violation of simplicity principles (e.g., additional abstraction layers, third-party dependencies not in approved stack, premature optimization) MUST be justified:
- Document in "Complexity Tracking" section of plan.md
- Explain why needed and why simpler alternatives were rejected
- Obtain explicit approval before implementation

### Runtime Guidance

For day-to-day development guidance beyond this constitution, refer to:
- `CLAUDE.md` - Claude Code agent instructions
- `.specify/templates/` - Template files for specs, plans, tasks
- `README.md` - Project-specific setup and usage

**Version**: 1.0.0 | **Ratified**: 2026-01-05 | **Last Amended**: 2026-01-05
