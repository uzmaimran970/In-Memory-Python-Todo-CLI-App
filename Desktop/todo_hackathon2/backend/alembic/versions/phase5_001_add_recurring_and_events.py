"""Phase 5: Add recurring tasks, reminders, audit, notifications

Revision ID: phase5_001
Revises:
Create Date: 2026-01-23

Tasks: T021, T022, T033, T034, T037, T055, T063
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'phase5_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # T021: Create recurrence_rules table
    op.create_table(
        'recurrence_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('days_of_week', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # T022, T037, T063: Add new columns to tasks table
    op.add_column('tasks', sa.Column('priority', sa.String(length=20), nullable=True, server_default='medium'))
    op.add_column('tasks', sa.Column('tags', sa.JSON(), nullable=True))
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_id', sa.Integer(), nullable=True))

    # Add foreign key constraint for recurrence_id
    op.create_foreign_key(
        'fk_tasks_recurrence_id',
        'tasks', 'recurrence_rules',
        ['recurrence_id'], ['id'],
        ondelete='SET NULL'
    )

    # T033: Create reminders table
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('remind_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE')
    )
    op.create_index('ix_reminders_task_id', 'reminders', ['task_id'])
    op.create_index('ix_reminders_user_id', 'reminders', ['user_id'])

    # T055: Create audit_entries table
    op.create_table(
        'audit_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=20), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('before_state', sa.JSON(), nullable=True),
        sa.Column('after_state', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_entries_task_id', 'audit_entries', ['task_id'])
    op.create_index('ix_audit_entries_user_id', 'audit_entries', ['user_id'])
    op.create_index('ix_audit_entries_timestamp', 'audit_entries', ['timestamp'])

    # T034: Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('body', sa.String(length=1000), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False, server_default='system'),
        sa.Column('read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])


def downgrade() -> None:
    # Drop notifications table
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')

    # Drop audit_entries table
    op.drop_index('ix_audit_entries_timestamp', table_name='audit_entries')
    op.drop_index('ix_audit_entries_user_id', table_name='audit_entries')
    op.drop_index('ix_audit_entries_task_id', table_name='audit_entries')
    op.drop_table('audit_entries')

    # Drop reminders table
    op.drop_index('ix_reminders_user_id', table_name='reminders')
    op.drop_index('ix_reminders_task_id', table_name='reminders')
    op.drop_table('reminders')

    # Remove columns from tasks table
    op.drop_constraint('fk_tasks_recurrence_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'recurrence_id')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')

    # Drop recurrence_rules table
    op.drop_table('recurrence_rules')
