# Data Model: Phase 5 — Dapr + Kafka Cloud Deployment

**Date**: 2026-01-23
**Branch**: `005-dapr-kafka-cloud-deploy`

## Entities

### Task (Extended)

Extends existing Task model with Phase 5 fields.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| title | string | Yes | Task title |
| description | string | No | Task description |
| status | enum | Yes | pending, in_progress, completed, deleted |
| priority | enum | No | high, medium, low (default: medium) |
| tags | string[] | No | User-defined tags |
| due_date | datetime | No | Task due date/time |
| recurrence | RecurrenceRule | No | Recurrence configuration |
| user_id | UUID | Yes | Owner reference |
| created_at | datetime | Yes | Creation timestamp |
| updated_at | datetime | Yes | Last update timestamp |

**Validation rules**:
- title: 1-255 characters, non-empty
- priority: must be one of (high, medium, low)
- due_date: must be in the future when set
- tags: max 10 tags per task, each max 50 characters

---

### RecurrenceRule

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| frequency | enum | Yes | daily, weekly, monthly |
| interval | int | No | Every N units (default: 1) |
| end_date | datetime | No | Stop recurring after this date |
| days_of_week | int[] | No | For weekly: 0=Mon..6=Sun |

**Validation rules**:
- frequency: must be one of (daily, weekly, monthly)
- interval: must be >= 1
- end_date: must be after task creation date
- days_of_week: only valid when frequency=weekly, values 0-6

**State transitions**:
- When a recurring task is completed → RecurringService creates new Task with:
  - Same title, description, priority, tags, recurrence
  - New due_date calculated from frequency + interval
  - Status reset to "pending"
  - New UUID assigned

---

### TaskEvent (Kafka message)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_id | UUID | Yes | Unique event identifier |
| event_type | enum | Yes | created, updated, deleted, completed |
| task_id | UUID | Yes | Reference to task |
| user_id | UUID | Yes | User who triggered |
| timestamp | datetime | Yes | When event occurred |
| payload | object | Yes | Task state at event time |
| metadata | object | No | Additional context |

**Published to topics**:
- `task-events`: All CRUD operations (consumed by recurring-service, audit-service)
- `task-updates`: All changes (consumed by websocket-service)

---

### Reminder

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| task_id | UUID | Yes | Task reference |
| user_id | UUID | Yes | User to notify |
| scheduled_time | datetime | Yes | When to fire |
| status | enum | Yes | pending, sent, cancelled |
| created_at | datetime | Yes | Creation timestamp |

**State transitions**:
- Created (pending) → Scheduled via Dapr Jobs
- Scheduled time arrives → Notification sent → status=sent
- Task completed before fire → status=cancelled
- Task deleted → status=cancelled

**Validation rules**:
- scheduled_time: must be in the future
- Only one active reminder per task

---

### AuditEntry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| event_type | enum | Yes | created, updated, deleted, completed |
| task_id | UUID | Yes | Task reference |
| user_id | UUID | Yes | User who acted |
| timestamp | datetime | Yes | When action occurred |
| before_state | object | No | Task state before change |
| after_state | object | No | Task state after change |

**Characteristics**:
- Immutable: entries are never updated or deleted
- Append-only: new entries always added
- Queryable by: user_id, task_id, event_type, timestamp range

---

### Notification

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| user_id | UUID | Yes | Recipient |
| title | string | Yes | Notification title |
| body | string | Yes | Notification content |
| type | enum | Yes | reminder, system |
| read | boolean | Yes | Whether user has seen it |
| created_at | datetime | Yes | When created |

---

## Relationships

```text
User (1) ──── (*) Task
Task (1) ──── (0..1) RecurrenceRule
Task (1) ──── (0..1) Reminder
Task (1) ──── (*) AuditEntry
Task (1) ──── (*) TaskEvent (Kafka, not persisted in DB)
User (1) ──── (*) Notification
User (1) ──── (*) AuditEntry
```

## Database Schema Extensions

Phase 5 adds these tables to the existing Neon DB PostgreSQL:

1. **recurrence_rules** — stores recurrence patterns linked to tasks
2. **reminders** — stores scheduled reminder state
3. **audit_entries** — append-only audit log
4. **notifications** — user notification inbox

Existing `tasks` table gets new columns: `priority`, `tags`, `due_date`, `recurrence_id`.

## Dapr State Store Usage

The Dapr state store (PostgreSQL-backed) is used for:
- **Conversation state**: Chat context for the chatbot (existing)
- **Task cache**: Fast key-value lookups for frequently accessed tasks
- **WebSocket connections**: Track active client connections per user

These are separate from the relational database tables above.
