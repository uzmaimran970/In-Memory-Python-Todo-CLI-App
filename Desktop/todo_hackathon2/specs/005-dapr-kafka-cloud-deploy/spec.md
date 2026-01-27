# Feature Specification: Phase 5 — Dapr + Kafka Cloud Deployment

**Feature Branch**: `005-dapr-kafka-cloud-deploy`
**Created**: 2026-01-23
**Status**: Draft
**Input**: User description: "Phase 5 advanced cloud deployment with Dapr, Kafka, event-driven architecture, recurring tasks, reminders, audit logs, and real-time sync"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recurring Tasks (Priority: P1)

As a user, when I complete a recurring task, the system automatically generates the next occurrence so I never have to manually recreate repetitive tasks.

**Why this priority**: Recurring tasks are the core Phase 5 feature that demonstrates event-driven architecture end-to-end. Completing a task triggers a Kafka event, which a consumer service processes to create the next instance.

**Independent Test**: Create a recurring task (e.g., "Daily standup"), mark it complete, and verify a new instance with the next occurrence date appears automatically without user intervention.

**Acceptance Scenarios**:

1. **Given** a task marked as recurring with frequency "daily", **When** the user completes it, **Then** a new task with the same title and next-day due date is created automatically.
2. **Given** a task marked as recurring with frequency "weekly", **When** the user completes it, **Then** a new task with the same title and next-week due date is created automatically.
3. **Given** a non-recurring task, **When** the user completes it, **Then** no new task is generated.

---

### User Story 2 - Due Date Reminders (Priority: P1)

As a user, I receive timely notifications when a task's due date is approaching, so I never miss a deadline.

**Why this priority**: Reminders demonstrate the Dapr Jobs API scheduling capability and the Notification Service consumer pattern. Critical for user value.

**Independent Test**: Create a task with a due date 5 minutes in the future, wait, and verify a notification is delivered at the scheduled time.

**Acceptance Scenarios**:

1. **Given** a task with a due date set, **When** the scheduled reminder time arrives, **Then** the user receives a notification with the task title and due date.
2. **Given** a task with no due date, **When** time passes, **Then** no reminder is generated.
3. **Given** a task that is completed before the reminder fires, **When** the reminder time arrives, **Then** no notification is sent.

---

### User Story 3 - Real-time Task Sync (Priority: P2)

As a user with multiple browser tabs or devices open, when I make a change to a task in one client, all other connected clients reflect the change immediately.

**Why this priority**: Demonstrates WebSocket Service consuming from Kafka `task-updates` topic. High user-experience value but depends on US1/US2 infrastructure.

**Independent Test**: Open two browser tabs, create/edit/complete a task in one tab, and verify the change appears in the other tab within 2 seconds.

**Acceptance Scenarios**:

1. **Given** two connected clients for the same user, **When** a task is created in client A, **Then** client B shows the new task within 2 seconds.
2. **Given** two connected clients, **When** a task is completed in client A, **Then** client B reflects the completion status within 2 seconds.
3. **Given** a client that loses connection, **When** reconnected, **Then** the client syncs to the latest state.

---

### User Story 4 - Audit Trail (Priority: P2)

As an administrator, I can view a complete history of all task operations (create, update, delete, complete) for accountability and debugging.

**Why this priority**: Demonstrates the Audit Log Service consuming from `task-events`. Important for traceability but lower user-facing impact than US1-US3.

**Independent Test**: Perform several task operations, then query the audit log and verify all operations are recorded with timestamps, user, and action type.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** the audit log is queried, **Then** it contains a "created" entry with timestamp, user ID, and task details.
2. **Given** a user deletes a task, **When** the audit log is queried, **Then** it contains a "deleted" entry with the task ID and timestamp.
3. **Given** multiple users performing operations, **When** the audit log is queried by user, **Then** only that user's operations are returned.

---

### User Story 5 - Task Priorities, Tags, Search & Filter (Priority: P3)

As a user, I can assign priorities and tags to tasks, and search/filter/sort my task list to find what I need quickly.

**Why this priority**: Enhances existing UI capabilities. Lower priority because it extends CRUD rather than demonstrating event-driven patterns.

**Independent Test**: Create several tasks with different priorities and tags, then use search/filter/sort to verify correct results are returned.

**Acceptance Scenarios**:

1. **Given** tasks with priorities (high, medium, low), **When** the user sorts by priority, **Then** tasks appear in priority order.
2. **Given** tasks with tags, **When** the user filters by a specific tag, **Then** only tasks with that tag are shown.
3. **Given** multiple tasks, **When** the user searches by keyword, **Then** only tasks containing that keyword in title or description are returned.

---

### User Story 6 - Local Minikube Deployment (Priority: P1)

As a developer, I can deploy the entire system (frontend, backend, Kafka, Dapr sidecars, all microservices) on a local Minikube cluster and access it at `localhost:8080`.

**Why this priority**: Foundation for all other stories. Without deployment infrastructure, event-driven features cannot run.

**Independent Test**: Run the deployment script/commands, verify all pods are running, access `localhost:8080`, and perform basic CRUD operations.

**Acceptance Scenarios**:

1. **Given** a fresh Minikube cluster with Dapr installed, **When** Helm charts are applied, **Then** all pods (frontend, backend, notification-service, recurring-service, audit-service, websocket-service, Kafka) reach Running state.
2. **Given** all pods are running, **When** a user accesses `localhost:8080`, **Then** the frontend loads and connects to the backend via Dapr service invocation.
3. **Given** a deployed cluster, **When** a task is created, **Then** Kafka events are published and consumed by the appropriate services.

---

### User Story 7 - Cloud Kubernetes Deployment with CI/CD (Priority: P3)

As a DevOps engineer, I can deploy the same system to a cloud Kubernetes cluster (AKS/GKE) with Redpanda Cloud as the Kafka broker, using a GitHub Actions CI/CD pipeline.

**Why this priority**: Production-grade deployment. Depends on US6 being stable locally first.

**Independent Test**: Push to main branch, verify GitHub Actions pipeline runs, deploys to cloud cluster, and all pods are healthy.

**Acceptance Scenarios**:

1. **Given** a push to the main branch, **When** GitHub Actions pipeline triggers, **Then** the system deploys to the cloud cluster with all pods running.
2. **Given** a cloud deployment, **When** a user accesses the frontend URL, **Then** all Phase 5 features work identically to local deployment.
3. **Given** a failed deployment, **When** the pipeline detects errors, **Then** it rolls back to the previous stable state.

---

### Edge Cases

- What happens when Kafka is temporarily unavailable? Events MUST be retried with exponential backoff; no data loss.
- What happens when a recurring task frequency is invalid? System MUST reject with a clear error message.
- What happens when multiple reminders fire simultaneously? Notification Service MUST handle concurrent events without dropping any.
- What happens when WebSocket connection drops during a task update? Client MUST reconnect and sync missed updates.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST publish task CRUD events to the `task-events` Kafka topic via Dapr Pub/Sub.
- **FR-002**: Recurring Task Service MUST consume `task-events` and create next occurrences for completed recurring tasks.
- **FR-003**: System MUST publish reminder events to the `reminders` Kafka topic when tasks with due dates are created/updated.
- **FR-004**: Notification Service MUST consume `reminders` and deliver notifications at the scheduled time via Dapr Jobs API.
- **FR-005**: System MUST publish task change events to the `task-updates` Kafka topic for all CRUD operations.
- **FR-006**: WebSocket Service MUST consume `task-updates` and push real-time changes to all connected clients.
- **FR-007**: Audit Service MUST consume `task-events` and persist a complete operation log.
- **FR-008**: System MUST support task priorities (high, medium, low) and user-defined tags.
- **FR-009**: System MUST support search by keyword, filter by tag/priority/status, and sort by priority/due-date/created-date.
- **FR-010**: All services MUST be deployable on Minikube with Dapr sidecars and Kafka (Strimzi/Redpanda).
- **FR-011**: Frontend MUST be accessible only at port 8080; backend MUST NOT be directly browser-accessible.
- **FR-012**: All secrets (API keys, DB credentials) MUST be managed via Dapr Secrets backed by Kubernetes Secrets.
- **FR-013**: System MUST support cloud deployment on AKS/GKE with Redpanda Cloud (free-tier).
- **FR-014**: CI/CD pipeline MUST deploy via GitHub Actions using Helm chart updates.
- **FR-015**: System MUST handle Kafka unavailability gracefully with retry and no event loss.

### Key Entities

- **Task**: Core entity with title, description, status, priority, tags, due_date, recurrence (frequency + pattern), user_id, created_at, updated_at.
- **TaskEvent**: Published to Kafka; contains event_type (created/updated/deleted/completed), task_id, user_id, timestamp, payload.
- **Reminder**: Scheduled notification; contains task_id, user_id, scheduled_time, status (pending/sent/cancelled).
- **AuditEntry**: Immutable log record; contains event_type, task_id, user_id, timestamp, before_state, after_state.
- **RecurrenceRule**: Defines recurrence pattern; contains frequency (daily/weekly/monthly), interval, end_date (optional).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Recurring tasks generate next occurrence within 5 seconds of completion.
- **SC-002**: Reminders are delivered within 30 seconds of the scheduled time.
- **SC-003**: Real-time updates propagate to all connected clients within 2 seconds.
- **SC-004**: Audit log captures 100% of task operations with no gaps.
- **SC-005**: Search/filter returns results within 1 second for users with up to 1000 tasks.
- **SC-006**: Local Minikube deployment achieves all-pods-running state from a clean cluster within the documented setup steps.
- **SC-007**: Cloud deployment via CI/CD pipeline succeeds with zero manual intervention after initial cluster setup.
- **SC-008**: System recovers from Kafka downtime (up to 5 minutes) without permanent event loss.
- **SC-009**: Frontend remains accessible at port 8080 during and after all microservice scaling events.

## Assumptions

- Phase 1-4 codebase is stable and functional (Todo CRUD, Auth, Chatbot, Minikube deployment at port 8080).
- Existing UI components can be extended for priority/tag/search fields without full rewrite.
- Redpanda Cloud free-tier provides sufficient throughput for demonstration purposes.
- Notification delivery mechanism is in-app or email; push notifications are out of scope for MVP.
- Users have `minikube`, `kubectl`, `helm`, and `dapr` CLI tools installed for local deployment.
- Cloud cluster (AKS/GKE) is pre-provisioned; spec covers deployment automation, not cluster creation.

## Constraints

- Existing UI and backend code structure MUST remain unchanged; new features are additive.
- All infrastructure connections MUST go through Dapr (no raw Kafka clients in app code).
- Free-tier Redpanda Cloud MUST be used for cloud Kafka; no paid services.
- Folder structure of `todo_hackathon2` MUST NOT be modified.
- Phase 5 work MUST be fully traceable via Spec-KitPlus workflow (Specify > Plan > Tasks > Implement).
