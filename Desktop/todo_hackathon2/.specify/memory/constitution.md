<!--
Sync Impact Report:
- Version change: 1.1.0 → 2.0.0
- Modified principles:
  - "Clean Architecture" → "Spec-Driven Development (SDD)"
  - "CLI-First Interface" → REMOVED (replaced by Microservices)
  - "Test-First (NON-NEGOTIABLE)" → kept as "Test-First Development"
  - "Minimal Dependencies" → REMOVED (replaced by defined tech stack)
  - "User Experience Focus" → REMOVED (implicit in full-stack)
  - "Spec-Driven Development" → promoted to Principle I
- Added sections:
  - Principle II: Microservices Architecture
  - Principle III: Event-Driven Architecture
  - Principle IV: Dapr Abstraction Layer
  - Principle V: Security-First
  - Principle VI: Scalability & Modularity
  - Principle VII: Test-First Development
  - Project Scope (Phase I–V)
  - Tech Stack Constraints (expanded)
  - Deployment & Operations
  - Rules for Agents
- Removed sections:
  - "CLI-First Interface" principle
  - "Minimal Dependencies" principle
  - "User Experience Focus" principle
  - "Additional Constraints" (replaced by Tech Stack Constraints)
  - "Development Workflow" (replaced by Rules for Agents)
- Templates requiring updates:
  - ⚠ .specify/templates/plan-template.md - Constitution Check section
    references old principles; agents MUST re-derive gates at plan time
  - ⚠ .specify/templates/spec-template.md - No structural changes needed
  - ⚠ .specify/templates/tasks-template.md - Path conventions now reflect
    backend/frontend/deploy structure
- Follow-up TODOs:
  - Plan template Constitution Check gates should reference new principles
    when next /sp.plan runs (auto-derived, no template edit needed)
-->

# Todo Hackathon 2 — Project Constitution

## Project Scope

1. Single application: Existing `todo_hackathon2` project.
2. Frontend + Backend deployed together; no new UI or external frontend
   MUST be created.
3. Features span Phase I to Phase V:
   - **Phase I**: Basic Todo CRUD + Authentication (Login/Signup)
   - **Phase II**: Chatbot integration
   - **Phase III**: Frontend deployed to Vercel
   - **Phase IV**: Kubernetes deployment on local Minikube →
     production-grade containerized deployment
   - **Phase V**: Advanced cloud deployment with Dapr + Kafka and
     event-driven architecture

## Core Principles

### I. Spec-Driven Development (SDD)

All features MUST be planned and documented before implementation.
The hierarchy is strictly enforced:

1. `/sp.specify` → defines WHAT to build.
2. `/sp.plan` → defines HOW to build (architecture + components).
3. `/sp.tasks` → defines atomic actionable tasks.
4. Code implementation MUST reference the above explicitly.

No code MUST be written without tasks defined in `/sp.tasks`. No
architecture changes MUST occur without updating `/sp.plan`. No
features MUST be added without updating `/sp.specify`.

### II. Microservices Architecture

Backend services (FastAPI) and Notification/Recurring-task services
are separate microservices. Services communicate via Kafka topics
(event-driven) or via Dapr Pub/Sub abstraction. Each service has
distinct responsibilities and dependencies flow through well-defined
API contracts.

### III. Event-Driven Architecture

Kafka/Redpanda Cloud serves as the primary message broker. All domain
events MUST use defined topics: `task-events`, `reminders`,
`task-updates`. Dapr MUST be used to abstract infrastructure
(Pub/Sub, State, Bindings, Jobs, Secrets). Producers and consumers
are decoupled through topic-based messaging.

### IV. Dapr Abstraction Layer

All infrastructure interactions MUST be abstracted through Dapr:

- **Pub/Sub** for event publishing and subscription
- **State management** for conversation and task cache
- **Service Invocation** for frontend-backend communication
- **Jobs API** for scheduled reminders and recurring tasks
- **Secrets** for credential management (K8s Secrets as backing store)

Direct infrastructure connections (raw Kafka clients, direct DB
connections bypassing Dapr state) MUST NOT be coded in application
services.

### V. Security-First

No credentials, tokens, or secrets MUST exist in source code. All
keys MUST be stored via Dapr Secrets or Kubernetes Secrets.
HTTPS/SSL MUST be used for production deployment. Environment
variables for local development MUST use `.env` files excluded
from version control.

### VI. Scalability & Modularity

Services MUST be loosely coupled. Kafka topics decouple event
producers and consumers, enabling independent scaling. Dapr
abstracts backend infrastructure so services can scale
independently. Each microservice MUST be independently deployable
and testable.

### VII. Test-First Development

TDD is mandatory for all new features: Tests written before
implementation → Tests MUST fail → Implement functionality →
Refactor. Automated validation tests MUST cover all core
functionality with clear pass/fail indicators. Integration tests
MUST verify cross-service communication.

## Tech Stack Constraints

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (React) |
| Backend | FastAPI (Python) |
| Database | Neon DB (PostgreSQL) |
| Kubernetes | Minikube (local) → AKS/GKE (cloud) |
| Dapr | Pub/Sub, State, Jobs, Secrets, Service Invocation |
| Event Broker | Kafka / Redpanda Cloud |
| CI/CD | GitHub Actions |
| Deployment | Helm Charts (required) |

The existing folder structure of `todo_hackathon2` MUST NOT be changed.

## Deployment & Operations

1. Kubernetes pods MUST include Dapr sidecars where applicable.
2. Frontend exposes only port `8080`.
3. Backend communicates via Dapr or internal K8s services only;
   backend MUST NOT be directly accessible by browser.
4. Scheduled tasks (reminders, recurring tasks) MUST be handled via
   Dapr Jobs API.
5. Logging, monitoring, and CI/CD pipelines MUST follow cloud
   provider best practices.
6. Local development: Minikube + Dapr sidecar.
7. Cloud deployment: AKS/GKE + Dapr + Kafka (Redpanda/Strimzi).

## Rules for Agents

1. **No freestyle code**: MUST follow `/sp.tasks`.
2. **No architecture changes** without updating `/sp.plan`.
3. **No feature additions** without updating `/sp.specify`.
4. **All code files MUST reference Task ID**.
5. If a task is missing or unclear → request clarification; do not
   improvise.
6. Follow the hierarchy strictly:
   Constitution > Specify > Plan > Tasks > Implement.
7. Use Dapr to abstract Kafka, DB, Secrets — do not code
   infrastructure connections directly.

## Governance

This constitution governs all development decisions for the
todo_hackathon2 application. All code changes MUST align with these
principles. Amendments require documentation in version control and
explicit version bump following semantic versioning:

- **MAJOR**: Backward-incompatible principle removals or
  redefinitions.
- **MINOR**: New principle/section added or materially expanded.
- **PATCH**: Clarifications, wording, typo fixes.

Regular compliance reviews ensure continued adherence to these
principles.

**Version**: 2.0.0 | **Ratified**: 2025-06-13 | **Last Amended**: 2026-01-23
