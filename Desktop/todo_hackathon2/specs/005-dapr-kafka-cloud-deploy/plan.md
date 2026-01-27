# Implementation Plan: Phase 5 — Dapr + Kafka Cloud Deployment

**Branch**: `005-dapr-kafka-cloud-deploy`
**Date**: 2026-01-23
**Status**: Ready for /sp.tasks

## Technical Context

| Aspect | Decision | Source |
|--------|----------|--------|
| Frontend | Next.js (existing) | Constitution |
| Backend | FastAPI (existing) | Constitution |
| Database | Neon DB PostgreSQL | Constitution |
| Message Broker | Kafka (Bitnami local, Redpanda Cloud) | Research |
| Runtime | Dapr 1.12+ | Constitution |
| Orchestration | Minikube (local), AKS/GKE (cloud) | Constitution |
| CI/CD | GitHub Actions | Constitution |
| Deployment | Helm Charts | Constitution |

## Constitution Check

| Principle | Gate | Status |
|-----------|------|--------|
| I. Spec-Driven Development | Spec exists at `specs/005-dapr-kafka-cloud-deploy/spec.md` | ✅ PASS |
| II. Microservices Architecture | 4 new services: notification, recurring, audit, websocket | ✅ PASS |
| III. Event-Driven Architecture | 3 Kafka topics: task-events, reminders, task-updates | ✅ PASS |
| IV. Dapr Abstraction Layer | All infra via Dapr components (pubsub, state, secrets, cron) | ✅ PASS |
| V. Security-First | Secrets via kubernetes-secrets store, no hardcoded creds | ✅ PASS |
| VI. Scalability & Modularity | Services loosely coupled via Kafka topics | ✅ PASS |
| VII. Test-First Development | Integration tests planned before implementation | ✅ PASS |

**Gate Evaluation**: All constitution gates PASS. Proceed to implementation planning.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    Dapr Service    ┌──────────────┐              │
│  │   Frontend   │◄───Invocation────►│   Backend    │              │
│  │  (Next.js)   │                    │  (FastAPI)   │              │
│  │  :8080       │                    │              │              │
│  └──────────────┘                    └──────┬───────┘              │
│                                             │                       │
│                                    Dapr Pub/Sub                     │
│                                             │                       │
│                           ┌─────────────────┼─────────────────┐    │
│                           │                 │                 │    │
│                           ▼                 ▼                 ▼    │
│                    ┌──────────┐      ┌──────────┐      ┌──────────┐│
│                    │task-events│      │reminders │      │task-     ││
│                    │          │      │          │      │updates   ││
│                    └────┬─────┘      └────┬─────┘      └────┬─────┘│
│                         │                 │                 │      │
│              ┌──────────┼─────┐           │                 │      │
│              │          │     │           │                 │      │
│              ▼          ▼     ▼           ▼                 ▼      │
│        ┌──────────┐┌──────────┐     ┌──────────┐     ┌──────────┐ │
│        │Recurring ││  Audit   │     │Notification│    │WebSocket │ │
│        │ Service  ││ Service  │     │  Service  │     │ Service  │ │
│        └──────────┘└──────────┘     └──────────┘     └──────────┘ │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │    Kafka     │    │   Neon DB    │    │    Dapr      │         │
│  │   (Broker)   │    │ (PostgreSQL) │    │  Components  │         │
│  └──────────────┘    └──────────────┘    └──────────────┘         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase A: Infrastructure Setup

**Objective**: Set up Dapr, Kafka, and Kubernetes infrastructure locally.

**Components**:
1. Dapr Helm installation on Minikube
2. Kafka Helm installation (Bitnami chart)
3. Dapr component YAML files:
   - `pubsub.kafka.yaml` — Kafka pub/sub
   - `statestore.yaml` — PostgreSQL state store
   - `secrets.yaml` — Kubernetes secrets store
   - `cron.yaml` — Reminder scanner cron binding
4. Kafka topic creation script
5. Kubernetes secrets for DB and Kafka credentials

**Verification**: All Dapr and Kafka pods running, components registered.

---

### Phase B: Database Schema Extension

**Objective**: Extend existing database with Phase 5 entities.

**Components**:
1. Alembic migration for `tasks` table extensions:
   - Add `priority` (enum: high/medium/low)
   - Add `tags` (JSONB array)
   - Add `due_date` (timestamp)
   - Add `recurrence_id` (FK to recurrence_rules)
2. New table: `recurrence_rules`
3. New table: `reminders`
4. New table: `audit_entries`
5. New table: `notifications`

**Verification**: Migrations apply cleanly, rollback works.

---

### Phase C: Backend Event Publishing

**Objective**: Modify backend to publish events via Dapr.

**Components**:
1. Dapr Python SDK integration (`dapr` package)
2. Event publishing service (`services/event_publisher.py`)
3. Modify task router to publish:
   - `task-events` on create/update/delete/complete
   - `task-updates` on all changes
   - `reminders` when due_date is set
4. Task model extensions (priority, tags, due_date, recurrence)
5. New endpoints:
   - `POST /api/tasks/{id}/complete`
   - `POST /api/tasks/{id}/reminder`
   - `DELETE /api/tasks/{id}/reminder`
   - Extended `GET /api/tasks` with filter/sort params

**Verification**: Events appear in Kafka topics when tasks are modified.

---

### Phase D: Microservices Implementation

**Objective**: Build the 4 event consumer microservices.

**Service 1: Recurring Task Service** (`services/recurring/`)
- Subscribes to `task-events` topic
- Filters for `completed` events with recurrence
- Calculates next due date
- Creates new task via Dapr service invocation to backend

**Service 2: Notification Service** (`services/notification/`)
- Subscribes to `reminders` topic
- Receives `fire` action when reminder time arrives
- Creates notification record in database
- (Future: Send email/push notification)

**Service 3: Audit Service** (`services/audit/`)
- Subscribes to `task-events` topic
- Persists every event to `audit_entries` table
- No external dependencies

**Service 4: WebSocket Service** (`services/websocket/`)
- Subscribes to `task-updates` topic
- Maintains WebSocket connections per user
- Broadcasts changes to connected clients
- Uses Python `websockets` library

**Verification**: Each service receives and processes events correctly.

---

### Phase E: Frontend Integration

**Objective**: Update frontend for Phase 5 features.

**Components**:
1. Task form extensions (priority dropdown, tags input, due date picker)
2. Task list filtering UI (status, priority, tag filters)
3. Task list sorting UI (by priority, due date, created)
4. Search input with keyword filtering
5. WebSocket connection for real-time updates
6. Notification inbox component

**Verification**: UI reflects all task field extensions, real-time updates work.

---

### Phase F: Helm Chart Updates

**Objective**: Package all services for Kubernetes deployment.

**Components**:
1. Update root Helm chart with new services:
   - `notification-service` deployment
   - `recurring-service` deployment
   - `audit-service` deployment
   - `websocket-service` deployment
2. Service-specific values (replicas, resources, env vars)
3. Dapr annotations for sidecar injection
4. ConfigMaps for environment-specific config
5. Ingress rules (frontend on :8080, websocket on /ws)

**Verification**: `helm template` generates valid K8s manifests.

---

### Phase G: CI/CD Pipeline

**Objective**: Automate build and deployment.

**Components**:
1. GitHub Actions workflow: `.github/workflows/deploy.yml`
2. Build stage: Docker images for all services
3. Push stage: Push to GitHub Container Registry
4. Deploy stage: Helm upgrade on target cluster
5. Verify stage: Health check all pods
6. Rollback stage: Revert on failure
7. Environment secrets: KUBECONFIG, registry credentials

**Verification**: Push to main triggers full deployment pipeline.

---

### Phase H: Cloud Deployment

**Objective**: Deploy to production Kubernetes cluster.

**Components**:
1. Redpanda Cloud setup (free-tier serverless)
2. Cloud-specific Dapr component values
3. Kubernetes cluster (AKS or GKE) configuration
4. TLS/SSL certificate setup
5. Production values.yaml overrides
6. Monitoring/logging setup (Dapr metrics, K8s logs)

**Verification**: Application accessible at cloud URL with all features working.

---

## Related Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Feature Spec | `specs/005-dapr-kafka-cloud-deploy/spec.md` | ✅ Complete |
| Research | `specs/005-dapr-kafka-cloud-deploy/research.md` | ✅ Complete |
| Data Model | `specs/005-dapr-kafka-cloud-deploy/data-model.md` | ✅ Complete |
| Task API Contract | `specs/005-dapr-kafka-cloud-deploy/contracts/task-api.yaml` | ✅ Complete |
| Event Schemas | `specs/005-dapr-kafka-cloud-deploy/contracts/events.yaml` | ✅ Complete |
| Dapr Components | `specs/005-dapr-kafka-cloud-deploy/contracts/dapr-components.yaml` | ✅ Complete |
| Quickstart Guide | `specs/005-dapr-kafka-cloud-deploy/quickstart.md` | ✅ Complete |
| Quality Checklist | `specs/005-dapr-kafka-cloud-deploy/checklists/requirements.md` | ✅ Complete |

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Kafka unavailability | Events lost, features degraded | Dapr retry policy + dead-letter topics |
| WebSocket disconnections | Stale UI state | Auto-reconnect with sync on reconnect |
| Neon DB connection limits | Service failures | Connection pooling via Dapr state store |
| Redpanda Cloud free-tier limits | Cloud deployment blocked | Monitor usage, upgrade if needed |
| Helm chart complexity | Deployment failures | Thorough local testing before cloud |

## Next Steps

Run `/sp.tasks` to generate atomic implementation tasks from this plan.

---

📋 **Architectural decision detected**: Event-driven microservices with Dapr + Kafka
Document reasoning and tradeoffs? Run `/sp.adr dapr-kafka-event-architecture`
