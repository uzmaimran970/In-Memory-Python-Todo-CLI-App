INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Generating static SQL
INFO  [alembic.runtime.migration] Will assume transactional DDL.
COHERE_API_KEY loaded: me...me
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INFO  [alembic.runtime.migration] Running upgrade  -> phase5_001, Phase 5: Add recurring tasks, reminders, audit, notifications
-- Running upgrade  -> phase5_001

CREATE TABLE recurrence_rules (
    id SERIAL NOT NULL, 
    frequency VARCHAR(20) NOT NULL, 
    interval INTEGER DEFAULT '1' NOT NULL, 
    end_date TIMESTAMP WITHOUT TIME ZONE, 
    days_of_week JSON, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id)
);

ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';

ALTER TABLE tasks ADD COLUMN tags JSON;

ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITHOUT TIME ZONE;

ALTER TABLE tasks ADD COLUMN recurrence_id INTEGER;

ALTER TABLE tasks ADD CONSTRAINT fk_tasks_recurrence_id FOREIGN KEY(recurrence_id) REFERENCES recurrence_rules (id) ON DELETE SET NULL;

CREATE TABLE reminders (
    id SERIAL NOT NULL, 
    task_id INTEGER NOT NULL, 
    user_id VARCHAR(255) NOT NULL, 
    scheduled_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    status VARCHAR(20) DEFAULT 'pending' NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(task_id) REFERENCES tasks (id) ON DELETE CASCADE
);

CREATE INDEX ix_reminders_task_id ON reminders (task_id);

CREATE INDEX ix_reminders_user_id ON reminders (user_id);

CREATE TABLE audit_entries (
    id SERIAL NOT NULL, 
    event_type VARCHAR(20) NOT NULL, 
    task_id INTEGER NOT NULL, 
    user_id VARCHAR(255) NOT NULL, 
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    before_state JSON, 
    after_state JSON, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_audit_entries_task_id ON audit_entries (task_id);

CREATE INDEX ix_audit_entries_user_id ON audit_entries (user_id);

CREATE INDEX ix_audit_entries_timestamp ON audit_entries (timestamp);

CREATE TABLE notifications (
    id SERIAL NOT NULL, 
    user_id VARCHAR(255) NOT NULL, 
    title VARCHAR(200) NOT NULL, 
    body VARCHAR(1000) NOT NULL, 
    type VARCHAR(20) DEFAULT 'system' NOT NULL, 
    read BOOLEAN DEFAULT 'false' NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_notifications_user_id ON notifications (user_id);

INSERT INTO alembic_version (version_num) VALUES ('phase5_001') RETURNING alembic_version.version_num;

COMMIT;

