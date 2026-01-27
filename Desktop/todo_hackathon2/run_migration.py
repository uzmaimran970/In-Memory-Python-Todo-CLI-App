"""Run Phase 5 migration on Neon database."""
import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_fjZJF8XEs5dv@ep-patient-king-a1eko8at-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

migration_sql = """
-- Add new columns to tasks table (if not exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tasks' AND column_name='priority') THEN
        ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tasks' AND column_name='tags') THEN
        ALTER TABLE tasks ADD COLUMN tags JSON;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tasks' AND column_name='due_date') THEN
        ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tasks' AND column_name='recurrence_id') THEN
        ALTER TABLE tasks ADD COLUMN recurrence_id INTEGER;
    END IF;
END $$;

-- Create recurrence_rules table if not exists
CREATE TABLE IF NOT EXISTS recurrence_rules (
    id SERIAL PRIMARY KEY,
    frequency VARCHAR(20) NOT NULL,
    interval INTEGER NOT NULL DEFAULT 1,
    end_date TIMESTAMP,
    days_of_week JSON,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create reminders table if not exists
CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    remind_at TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create audit_entries table if not exists
CREATE TABLE IF NOT EXISTS audit_entries (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(20) NOT NULL,
    task_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    before_state JSON,
    after_state JSON
);

-- Create notifications table if not exists
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    body VARCHAR(1000) NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'system',
    read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_reminders_task_id ON reminders(task_id);
CREATE INDEX IF NOT EXISTS ix_reminders_user_id ON reminders(user_id);
CREATE INDEX IF NOT EXISTS ix_audit_entries_task_id ON audit_entries(task_id);
CREATE INDEX IF NOT EXISTS ix_audit_entries_user_id ON audit_entries(user_id);
CREATE INDEX IF NOT EXISTS ix_audit_entries_timestamp ON audit_entries(timestamp);
CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id);
"""

if __name__ == "__main__":
    print("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    print("Running migration...")
    cur.execute(migration_sql)

    print("Migration completed successfully!")
    cur.close()
    conn.close()
