# Tasks: Phase 5 — Dapr + Kafka Cloud Deployment

**Branch**: `005-dapr-kafka-cloud-deploy`
**Generated**: 2026-01-23
**Total Tasks**: 78

## User Story Mapping

| Story | Priority | Description | Tasks |
|-------|----------|-------------|-------|
| US6 | P1 | Local Minikube Deployment | T001-T020 (Foundational) |
| US1 | P1 | Recurring Tasks | T021-T032 |
| US2 | P1 | Due Date Reminders | T033-T044 |
| US3 | P2 | Real-time Task Sync | T045-T054 |
| US4 | P2 | Audit Trail | T055-T062 |
| US5 | P3 | Priorities, Tags, Search & Filter | T063-T072 |
| US7 | P3 | Cloud Kubernetes Deployment with CI/CD | T073-T078 |

---

## Phase 1: Setup

**Goal**: Initialize project structure and dependencies for Phase 5.

- [x] T001 Add Dapr Python SDK dependency to backend/requirements.txt
- [x] T002 Add websockets dependency to backend/requirements.txt
- [x] T003 Create services/ directory at project root for microservices
- [x] T004 Create deploy/dapr-components/ directory for Dapr YAML files
- [x] T005 Create deploy/scripts/ directory for deployment automation

---

## Phase 2: Foundational — Local Minikube Deployment (US6)

**Goal**: Deploy the entire system on local Minikube with Dapr and Kafka.

**Independent Test**: Run deployment scripts, verify all pods running, access localhost:8080, perform CRUD operations.

### Infrastructure Setup

- [x] T006 [US6] Create deploy/dapr-components/pubsub-kafka.yaml for Kafka pub/sub component
- [x] T007 [US6] Create deploy/dapr-components/statestore-postgres.yaml for PostgreSQL state store
- [x] T008 [US6] Create deploy/dapr-components/secretstore-kubernetes.yaml for K8s secrets
- [x] T009 [US6] Create deploy/dapr-components/cron-reminder.yaml for reminder scanner binding
- [x] T010 [P] [US6] Create deploy/scripts/install-dapr.sh for Dapr Helm installation
- [x] T011 [P] [US6] Create deploy/scripts/install-kafka.sh for Kafka Helm installation
- [x] T012 [P] [US6] Create deploy/scripts/create-topics.sh for Kafka topic creation
- [x] T013 [US6] Create deploy/scripts/create-secrets.sh for K8s secrets setup

### Helm Chart Updates

- [x] T014 [US6] Update deploy/helm-charts/backend/templates/deployment.yaml with Dapr annotations
- [x] T015 [P] [US6] Update deploy/helm-charts/frontend/templates/deployment.yaml with Dapr annotations
- [x] T016 [US6] Create deploy/helm-charts/notification-service/Chart.yaml and templates
- [x] T017 [P] [US6] Create deploy/helm-charts/recurring-service/Chart.yaml and templates
- [x] T018 [P] [US6] Create deploy/helm-charts/audit-service/Chart.yaml and templates
- [x] T019 [P] [US6] Create deploy/helm-charts/websocket-service/Chart.yaml and templates
- [x] T020 [US6] Update deploy/helm-charts/Chart.yaml to include all service dependencies

---

## Phase 3: Recurring Tasks (US1)

**Goal**: When a recurring task is completed, automatically generate the next occurrence.

**Independent Test**: Create recurring task "Daily standup", mark complete, verify new instance appears with next-day due date.

### Database Schema

- [ ] T021 [US1] Create Alembic migration for recurrence_rules table in backend/alembic/versions/
- [ ] T022 [US1] Update tasks table migration to add recurrence_id FK in backend/alembic/versions/

### Backend Models & Services

- [ ] T023 [US1] Create RecurrenceRule SQLModel in backend/app/models/recurrence.py
- [ ] T024 [US1] Update Task model with recurrence relationship in backend/app/models/task.py
- [ ] T025 [US1] Create event_publisher service in backend/app/services/event_publisher.py
- [ ] T026 [US1] Update task router POST /complete endpoint to publish task-events in backend/app/routers/tasks.py

### Recurring Service Microservice

- [ ] T027 [US1] Create services/recurring/__init__.py with FastAPI app setup
- [ ] T028 [US1] Create services/recurring/main.py with Dapr subscription endpoint /events/tasks
- [ ] T029 [US1] Implement next occurrence date calculation in services/recurring/recurrence_calculator.py
- [ ] T030 [US1] Implement create-next-task via Dapr service invocation in services/recurring/task_client.py
- [ ] T031 [US1] Create services/recurring/Dockerfile for containerization
- [ ] T032 [US1] Create services/recurring/requirements.txt with dependencies

---

## Phase 4: Due Date Reminders (US2)

**Goal**: Users receive notifications when task due dates approach.

**Independent Test**: Create task with due date 5 minutes in future, wait, verify notification delivered.

### Database Schema

- [ ] T033 [US2] Create Alembic migration for reminders table in backend/alembic/versions/
- [ ] T034 [US2] Create Alembic migration for notifications table in backend/alembic/versions/

### Backend Models & Endpoints

- [ ] T035 [US2] Create Reminder SQLModel in backend/app/models/reminder.py
- [ ] T036 [US2] Create Notification SQLModel in backend/app/models/notification.py
- [ ] T037 [US2] Update tasks table migration to add due_date column in backend/alembic/versions/
- [ ] T038 [US2] Add POST /api/tasks/{id}/reminder endpoint in backend/app/routers/tasks.py
- [ ] T039 [US2] Add DELETE /api/tasks/{id}/reminder endpoint in backend/app/routers/tasks.py
- [ ] T040 [US2] Publish reminders topic event when due_date set in backend/app/services/event_publisher.py

### Notification Service Microservice

- [ ] T041 [US2] Create services/notification/__init__.py with FastAPI app setup
- [ ] T042 [US2] Create services/notification/main.py with Dapr subscription endpoint /events/reminders
- [ ] T043 [US2] Implement notification creation logic in services/notification/notification_handler.py
- [ ] T044 [US2] Create services/notification/Dockerfile and requirements.txt

---

## Phase 5: Real-time Task Sync (US3)

**Goal**: Changes in one client appear immediately in all connected clients.

**Independent Test**: Open two browser tabs, create task in one, verify appears in other within 2 seconds.

### Backend Event Publishing

- [ ] T045 [US3] Add task-updates topic publishing for all CRUD operations in backend/app/services/event_publisher.py

### WebSocket Service Microservice

- [ ] T046 [US3] Create services/websocket/__init__.py with FastAPI + WebSocket app
- [ ] T047 [US3] Create services/websocket/main.py with Dapr subscription endpoint /events/updates
- [ ] T048 [US3] Implement WebSocket connection manager in services/websocket/connection_manager.py
- [ ] T049 [US3] Implement broadcast logic for task updates in services/websocket/broadcaster.py
- [ ] T050 [US3] Create services/websocket/Dockerfile and requirements.txt

### Frontend WebSocket Integration

- [ ] T051 [US3] Create WebSocket hook in frontend/src/hooks/useTaskSync.ts
- [ ] T052 [US3] Update task list component to subscribe to WebSocket in frontend/src/components/TaskList.tsx
- [ ] T053 [US3] Implement reconnection logic with sync on reconnect in frontend/src/hooks/useTaskSync.ts
- [ ] T054 [US3] Update deploy/helm-charts/websocket-service/templates/service.yaml with WebSocket ingress

---

## Phase 6: Audit Trail (US4)

**Goal**: Complete history of all task operations for accountability.

**Independent Test**: Perform task operations, query audit log, verify all recorded with timestamps.

### Database Schema

- [ ] T055 [US4] Create Alembic migration for audit_entries table in backend/alembic/versions/

### Audit Service Microservice

- [ ] T056 [US4] Create services/audit/__init__.py with FastAPI app setup
- [ ] T057 [US4] Create services/audit/main.py with Dapr subscription endpoint /events/tasks
- [ ] T058 [US4] Create AuditEntry SQLModel in services/audit/models.py
- [ ] T059 [US4] Implement audit entry persistence in services/audit/audit_handler.py
- [ ] T060 [US4] Create services/audit/Dockerfile and requirements.txt

### Backend Audit Query Endpoint

- [ ] T061 [US4] Add GET /api/audit endpoint with filters in backend/app/routers/audit.py
- [ ] T062 [US4] Register audit router in backend/app/main.py

---

## Phase 7: Priorities, Tags, Search & Filter (US5)

**Goal**: Users can assign priorities/tags and search/filter/sort tasks.

**Independent Test**: Create tasks with different priorities/tags, use filters, verify correct results.

### Database Schema

- [ ] T063 [US5] Update tasks table migration to add priority and tags columns in backend/alembic/versions/

### Backend Model & Endpoint Updates

- [ ] T064 [US5] Update Task SQLModel with priority and tags fields in backend/app/models/task.py
- [ ] T065 [US5] Add filter/sort query params to GET /api/tasks in backend/app/routers/tasks.py
- [ ] T066 [US5] Implement search by keyword in task service in backend/app/services/task_service.py

### Frontend UI Extensions

- [ ] T067 [P] [US5] Add priority dropdown to task form in frontend/src/components/TaskForm.tsx
- [ ] T068 [P] [US5] Add tags input component in frontend/src/components/TagsInput.tsx
- [ ] T069 [P] [US5] Add due date picker to task form in frontend/src/components/TaskForm.tsx
- [ ] T070 [US5] Create filter bar component in frontend/src/components/FilterBar.tsx
- [ ] T071 [US5] Create sort dropdown component in frontend/src/components/SortDropdown.tsx
- [ ] T072 [US5] Integrate filters/sort with task list API calls in frontend/src/lib/api.ts

---

## Phase 8: Cloud Kubernetes Deployment with CI/CD (US7)

**Goal**: Deploy to cloud K8s cluster via GitHub Actions.

**Independent Test**: Push to main, verify pipeline runs, deploys successfully, all pods healthy.

### CI/CD Pipeline

- [ ] T073 [US7] Create .github/workflows/build.yml for Docker image builds
- [ ] T074 [US7] Create .github/workflows/deploy.yml for Helm deployment
- [ ] T075 [US7] Add health check verification step to deploy workflow

### Cloud Configuration

- [ ] T076 [US7] Create deploy/values-cloud.yaml with Redpanda Cloud broker config
- [ ] T077 [US7] Update deploy/dapr-components/pubsub-kafka.yaml with cloud auth secrets
- [ ] T078 [US7] Create deploy/scripts/setup-cloud-secrets.sh for cloud secret provisioning

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Error handling, edge cases, documentation.

- [ ] T079 Add Dapr retry policy to all subscriptions in deploy/dapr-components/subscriptions.yaml
- [ ] T080 Add dead-letter topic handling in all microservices
- [ ] T081 Update docs/LOCAL_DEPLOYMENT.md with Phase 5 setup instructions
- [ ] T082 Update docs/CLOUD_DEPLOYMENT.md with AKS/GKE instructions
- [ ] T083 Add integration tests for event flow in tests/integration/test_event_flow.py

---

## Dependencies

```text
Phase 1 (Setup)
    ↓
Phase 2 (US6: Local Deployment) ← BLOCKER for all features
    ↓
┌───────────────┬───────────────┐
│               │               │
Phase 3 (US1)   Phase 4 (US2)   Phase 7 (US5)
Recurring       Reminders       Priorities/Tags
    │               │               │
    └───────┬───────┘               │
            ↓                       │
      Phase 5 (US3)                 │
      Real-time Sync               │
            │                       │
            └───────────────────────┘
                      ↓
              Phase 6 (US4)
              Audit Trail
                      ↓
              Phase 8 (US7)
              Cloud Deploy
                      ↓
              Phase 9 (Polish)
```

## Parallel Execution Opportunities

### Within Phase 2 (US6):
- T010, T011, T012 can run in parallel (independent scripts)
- T015, T016, T017, T018, T019 can run in parallel (independent Helm charts)

### Across User Stories:
- Phase 3 (US1), Phase 4 (US2), Phase 7 (US5) can start in parallel after Phase 2
- T067, T068, T069 can run in parallel (independent frontend components)

### Task Summary by Story

| Story | Task Count | Parallelizable |
|-------|------------|----------------|
| Setup | 5 | 0 |
| US6 | 15 | 8 |
| US1 | 12 | 0 |
| US2 | 12 | 0 |
| US3 | 10 | 0 |
| US4 | 8 | 0 |
| US5 | 10 | 3 |
| US7 | 6 | 0 |
| Polish | 5 | 0 |
| **Total** | **83** | **11** |

## Implementation Strategy

### MVP Scope (Recommended First Iteration)
- Phase 1 (Setup)
- Phase 2 (US6: Local Deployment)
- Phase 3 (US1: Recurring Tasks)

This delivers a working event-driven system demonstrating the core architecture.

### Full Scope
All phases 1-9 for complete Phase 5 functionality.

---

**Next Step**: Run `/sp.implement` to begin task execution.
