# Research: Phase 5 — Dapr + Kafka Cloud Deployment

**Date**: 2026-01-23
**Branch**: `005-dapr-kafka-cloud-deploy`

## Research Areas

### 1. Dapr Pub/Sub with Kafka

**Decision**: Use `pubsub.kafka` Dapr component with Bitnami Kafka Helm chart (local) and Redpanda Cloud (cloud).

**Rationale**:
- Dapr's Kafka component abstracts broker details; app code uses Dapr HTTP/gRPC APIs only.
- Python services publish via `DaprClient.publish_event()` and subscribe via HTTP endpoints (`/dapr/subscribe` + topic handlers).
- CloudEvents format is used by default for message envelopes.

**Alternatives considered**:
- Raw confluent-kafka Python client: Rejected per constitution (Principle IV — no direct infrastructure connections).
- Dapr with Redis Streams: Rejected; Kafka required by constitution for production-grade event streaming.

**Component YAML pattern**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: kafka.default.svc.cluster.local:9092
  - name: authRequired
    value: "false"
```

---

### 2. Dapr State Store (PostgreSQL)

**Decision**: Use `state.postgresql` v2 component backed by Neon DB.

**Rationale**:
- Neon DB is already the project database (constitution constraint).
- Dapr state store provides key-value abstraction for task cache and conversation state.
- Connection string sourced from Kubernetes Secrets via Dapr Secrets component.

**Alternatives considered**:
- Redis state store: Adds another dependency; PostgreSQL already available.
- In-memory state: Not persistent across pod restarts.

**Component YAML pattern**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v2
  metadata:
  - name: connectionString
    secretKeyRef:
      name: db-credentials
      key: connection-string
  auth:
    secretStore: kubernetes-secrets
```

---

### 3. Dapr Scheduled Jobs (Reminders)

**Decision**: Use `bindings.cron` for periodic checks + Dapr Jobs API for one-time scheduled reminders.

**Rationale**:
- Cron binding handles periodic scanning for upcoming reminders.
- Individual task reminders with specific due dates use the Jobs API to schedule one-time triggers.
- Python service receives invocations at the configured endpoint.

**Alternatives considered**:
- APScheduler in Python: Rejected; not Dapr-native, doesn't scale across pods.
- External cron jobs (K8s CronJob): Rejected; doesn't integrate with Dapr lifecycle.

**Component YAML pattern**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 60s"
  - name: direction
    value: "input"
```

---

### 4. Dapr Secrets Management

**Decision**: Use `secretstores.kubernetes` component.

**Rationale**:
- Kubernetes Secrets are the simplest, most integrated option for K8s deployments.
- No external secret management service needed (no HashiCorp Vault complexity).
- All components reference secrets via `secretKeyRef`.

**Component YAML pattern**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
```

---

### 5. Dapr Service Invocation

**Decision**: Frontend calls backend via Dapr service invocation (HTTP proxy through sidecar).

**Rationale**:
- Dapr sidecar proxies HTTP requests to the backend app-id.
- Frontend's Next.js API routes call `http://localhost:3500/v1.0/invoke/backend-service/method/<endpoint>`.
- Provides mTLS, retries, and observability out of the box.

**Alternatives considered**:
- Direct K8s Service DNS: Rejected per constitution (Principle IV — use Dapr abstraction).
- Dapr gRPC invocation: HTTP is simpler for REST-based FastAPI backend.

---

### 6. Kafka Deployment Strategy

**Decision**: Bitnami Kafka Helm chart (local Minikube), Redpanda Cloud Serverless (cloud).

**Rationale**:
- Bitnami chart is well-maintained, supports single-node for dev.
- Redpanda Cloud serverless free-tier provides managed Kafka-compatible API with no ops overhead.
- Dapr pubsub.kafka component works with both (same brokers config, different values).

**Alternatives considered**:
- Strimzi Operator: More complex setup for local dev; better for production but Redpanda Cloud is simpler.
- Confluent Cloud: Not free-tier friendly; Redpanda offers generous free tier.

---

### 7. Microservice Architecture

**Decision**: 4 new microservices alongside existing backend:

| Service | App ID | Role | Consumes |
|---------|--------|------|----------|
| notification-service | notification-svc | Send reminders | `reminders` topic |
| recurring-service | recurring-svc | Generate next tasks | `task-events` topic |
| audit-service | audit-svc | Log all operations | `task-events` topic |
| websocket-service | websocket-svc | Push real-time updates | `task-updates` topic |

**Rationale**:
- Each service has a single responsibility (constitution Principle VI).
- All are Python FastAPI services for consistency with existing backend.
- Each runs as a separate K8s Deployment with Dapr sidecar.

---

### 8. WebSocket Strategy

**Decision**: Dedicated websocket-service consuming from Kafka and managing WebSocket connections.

**Rationale**:
- WebSocket connections are long-lived; separating from main backend avoids blocking API handlers.
- Service subscribes to `task-updates` via Dapr and broadcasts to connected clients.
- Frontend connects directly to websocket-service's exposed endpoint.

**Alternatives considered**:
- Server-Sent Events (SSE): Simpler but less interactive; WebSocket chosen for bidirectional capability.
- Socket.io: Adds Node.js dependency; pure WebSocket with Python's `websockets` library is sufficient.

---

### 9. CI/CD Pipeline

**Decision**: GitHub Actions with Helm chart deployment.

**Rationale**:
- Constitution mandates GitHub Actions for CI/CD.
- Pipeline: Build Docker images → Push to registry → Helm upgrade on cloud cluster.
- Separate workflows for local validation (minikube) and cloud deployment.

**Pipeline stages**:
1. Lint + Test (pytest, eslint)
2. Build Docker images (multi-stage)
3. Push to GitHub Container Registry (ghcr.io)
4. Helm upgrade on target cluster
5. Health check verification

---

### 10. Retry and Resilience

**Decision**: Dapr's built-in retry policies + dead-letter topics for failed events.

**Rationale**:
- Dapr Pub/Sub supports configurable retry policies per subscription.
- Dead-letter topics capture events that exceed retry attempts.
- Application code does not need custom retry logic.

**Configuration pattern**:
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-sub
spec:
  pubsubname: taskpubsub
  topic: task-events
  routes:
    default: /events/tasks
  deadLetterTopic: task-events-deadletter
```
