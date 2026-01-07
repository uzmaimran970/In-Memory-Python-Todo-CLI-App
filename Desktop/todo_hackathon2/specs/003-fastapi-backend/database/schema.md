# Database Schema Specification: FastAPI Backend with Neon PostgreSQL

**Feature**: FastAPI Backend with SQLModel ORM and Neon Serverless PostgreSQL
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-01-05
**Last Updated**: 2026-01-05

---

## Overview

This specification defines the complete database schema for the Phase II Todo Hackathon backend service. The schema uses **SQLModel** (combination of SQLAlchemy and Pydantic) for ORM capabilities and integrates with **Neon Serverless PostgreSQL** for cloud-native database hosting.

**Key Design Principles**:
- **Security First**: All task operations enforce user isolation via `user_id` foreign key
- **Performance**: Strategic indexes on frequently queried columns (`user_id`, `completed`)
- **Type Safety**: SQLModel provides runtime validation and IDE autocompletion
- **Migration Ready**: Schema designed for Alembic migrations
- **Better Auth Integration**: Users table managed externally, referenced via foreign key

---

## Database Connection

### Neon PostgreSQL Configuration

**Connection String** (from environment):
```
DATABASE_URL=postgresql://neondb_owner:npg_fjZJF8XEs5dv@ep-patient-king-a1eko8at-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**Connection Parameters**:
- **Host**: `ep-patient-king-a1eko8at-pooler.ap-southeast-1.aws.neon.tech`
- **Database**: `neondb`
- **User**: `neondb_owner`
- **SSL Mode**: `require` (mandatory for Neon)
- **Channel Binding**: `require` (enhanced security)
- **Connection Pooling**: Enabled via Neon's built-in pooler

**Environment Variables** (`.env`):
```env
DATABASE_URL=postgresql://neondb_owner:npg_fjZJF8XEs5dv@ep-patient-king-a1eko8at-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
ENVIRONMENT=development
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

---

## Table Schemas

### 1. Users Table (Managed by Better Auth)

**Status**: External (Not created by this backend)
**Management**: Better Auth library handles user table creation and management
**Access**: Read-only reference via foreign key

**Referenced Schema** (for reference only):
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,                    -- Better Auth uses text IDs
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**SQLModel Reference** (Read-Only Model):
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    """
    User model - READ ONLY
    This table is managed by Better Auth.
    Backend only reads from this table for user validation.
    """
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Important Notes**:
- ⚠️ **DO NOT** create this table in backend migrations
- ⚠️ **DO NOT** modify this table structure
- ✅ **DO** validate `user_id` exists before creating tasks
- ✅ **DO** use this table for user lookups if needed

---

### 2. Tasks Table (Primary Backend Table)

**Status**: Managed by this backend
**Purpose**: Store user tasks with full CRUD operations and user isolation

**SQL Schema**:
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,

    -- Indexes for performance
    CONSTRAINT tasks_title_length CHECK (LENGTH(title) >= 1 AND LENGTH(title) <= 200),
    CONSTRAINT tasks_description_length CHECK (description IS NULL OR LENGTH(description) <= 1000)
);

-- Performance Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

**SQLModel Class**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.

    Security: All queries MUST filter by user_id from authenticated JWT.
    Performance: Indexed on user_id and completed for fast queries.
    """
    __tablename__ = "tasks"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Key to Better Auth users table
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
        description="User ID from Better Auth (extracted from JWT)"
    )

    # Task Fields
    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Task title (1-200 characters)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        nullable=True,
        description="Optional task description (max 1000 characters)"
    )

    completed: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Task completion status"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Task last update timestamp (UTC)"
    )

    # Relationships (optional, for ORM navigation)
    # user: Optional["User"] = Relationship(back_populates="tasks")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": "clx1234567890",
                "title": "Complete Phase II Hackathon",
                "description": "Build FastAPI backend with JWT authentication",
                "completed": False,
                "created_at": "2026-01-05T10:30:00Z",
                "updated_at": "2026-01-05T10:30:00Z"
            }
        }
```

**Pydantic Schemas for API** (Request/Response):
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    """Request schema for creating a new task"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "title": "Complete backend implementation",
                "description": "Implement all API endpoints with JWT authentication"
            }
        }

class TaskUpdate(BaseModel):
    """Request schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None

    @validator('title')
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip() if v else v

class TaskResponse(BaseModel):
    """Response schema matching frontend expectations"""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool = Field(alias="is_completed")  # Frontend uses is_completed
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": "clx1234567890",
                "title": "Complete Phase II Hackathon",
                "description": "Build FastAPI backend with JWT authentication",
                "is_completed": False,
                "created_at": "2026-01-05T10:30:00Z",
                "updated_at": "2026-01-05T10:30:00Z"
            }
        }
```

---

## Indexes

### Performance Indexes

**Purpose**: Optimize common query patterns

1. **`idx_tasks_user_id`**:
   - **Column**: `user_id`
   - **Type**: B-tree
   - **Purpose**: Fast filtering of tasks by user (most common query)
   - **Query Benefit**: `SELECT * FROM tasks WHERE user_id = ?`

2. **`idx_tasks_completed`**:
   - **Column**: `completed`
   - **Type**: B-tree
   - **Purpose**: Filter tasks by completion status
   - **Query Benefit**: `SELECT * FROM tasks WHERE completed = false`

3. **`idx_tasks_user_completed`** (Composite):
   - **Columns**: `user_id`, `completed`
   - **Type**: B-tree
   - **Purpose**: Optimize filtered task lists (e.g., "show my active tasks")
   - **Query Benefit**: `SELECT * FROM tasks WHERE user_id = ? AND completed = false`

4. **`idx_tasks_created_at`**:
   - **Column**: `created_at DESC`
   - **Type**: B-tree
   - **Purpose**: Sort tasks by creation date (newest first)
   - **Query Benefit**: `SELECT * FROM tasks ORDER BY created_at DESC`

**Index Usage Strategy**:
```sql
-- Query 1: Get all user tasks (uses idx_tasks_user_id)
SELECT * FROM tasks WHERE user_id = 'clx123' ORDER BY created_at DESC;

-- Query 2: Get active tasks (uses idx_tasks_user_completed)
SELECT * FROM tasks WHERE user_id = 'clx123' AND completed = false;

-- Query 3: Get completed tasks (uses idx_tasks_user_completed)
SELECT * FROM tasks WHERE user_id = 'clx123' AND completed = true;
```

---

## Database Migrations

### Migration Strategy

**Tool**: Alembic (SQLAlchemy migration tool)

**Initial Migration** (Create Tasks Table):
```python
"""Initial migration - create tasks table

Revision ID: 001_initial
Revises:
Create Date: 2026-01-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('LENGTH(title) >= 1 AND LENGTH(title) <= 200', name='tasks_title_length'),
        sa.CheckConstraint('description IS NULL OR LENGTH(description) <= 1000', name='tasks_description_length')
    )

    # Create indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_completed', 'tasks', ['completed'])
    op.create_index('idx_tasks_user_completed', 'tasks', ['user_id', 'completed'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'], postgresql_ops={'created_at': 'DESC'})

def downgrade() -> None:
    op.drop_index('idx_tasks_created_at', table_name='tasks')
    op.drop_index('idx_tasks_user_completed', table_name='tasks')
    op.drop_index('idx_tasks_completed', table_name='tasks')
    op.drop_index('idx_tasks_user_id', table_name='tasks')
    op.drop_table('tasks')
```

**Migration Commands**:
```bash
# Initialize Alembic (first time only)
alembic init migrations

# Create new migration
alembic revision --autogenerate -m "Initial tasks table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current version
alembic current
```

---

## Database Connection Management

### SQLModel Engine Setup

**`db.py`** (Database Connection Module):
```python
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import NullPool
import os
from typing import Generator

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_fjZJF8XEs5dv@ep-patient-king-a1eko8at-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

# Create engine with Neon-optimized settings
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max connections beyond pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "sslmode": "require",
        "channel_binding": "require"
    }
)

def create_db_and_tables():
    """
    Create all database tables.
    Should be called on application startup.
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI route handlers.
    Provides a database session and ensures cleanup.

    Usage:
        @app.get("/api/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            tasks = session.exec(select(Task)).all()
            return tasks
    """
    with Session(engine) as session:
        yield session
```

---

## Security Constraints

### User Isolation Enforcement

**Critical Security Rule**: **ALL task queries MUST filter by `user_id` from authenticated JWT**

**Correct Implementation** (Secure):
```python
from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from typing import Annotated

# Extract user_id from JWT (see authentication.md spec)
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Extract and validate user_id from JWT"""
    # JWT verification logic here
    return user_id

@app.get("/api/tasks")
def get_user_tasks(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Get tasks for authenticated user ONLY"""
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks
```

**Incorrect Implementation** (Security Vulnerability):
```python
# ❌ NEVER DO THIS - Exposes all users' tasks
@app.get("/api/tasks")
def get_all_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()  # Missing user_id filter!
    return tasks

# ❌ NEVER DO THIS - Allows access to any user's task
@app.get("/api/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)  # Missing user_id verification!
    if not task:
        raise HTTPException(404)
    return task
```

**Enforcement Checklist**:
- ✅ All `SELECT` queries filter by `user_id = current_user.id`
- ✅ All `UPDATE` queries verify `task.user_id == current_user.id`
- ✅ All `DELETE` queries verify `task.user_id == current_user.id`
- ✅ `user_id` is extracted from verified JWT token, never from request body
- ✅ Return 403 Forbidden if user tries to access another user's task

---

## Validation Rules

### Field Validation

**Title**:
- ✅ Required (not null)
- ✅ Minimum length: 1 character
- ✅ Maximum length: 200 characters
- ✅ Must not be empty or whitespace-only
- ❌ Reject: `""`, `"   "`, null

**Description**:
- ✅ Optional (nullable)
- ✅ Maximum length: 1000 characters
- ✅ Can be null or empty string

**Completed**:
- ✅ Boolean type
- ✅ Default: `false`
- ✅ Not null

**User ID**:
- ✅ Must reference existing user in `users` table
- ✅ Extracted from JWT, never from request body
- ✅ Immutable after task creation
- ❌ Reject: Invalid user IDs, missing users

**Timestamps**:
- ✅ `created_at`: Set on INSERT, immutable
- ✅ `updated_at`: Set on INSERT, auto-updated on UPDATE
- ✅ Use UTC timezone for all timestamps

---

## Acceptance Criteria

### Database Schema

- [ ] **Schema Creation**
  - Tasks table created with all specified columns
  - Proper data types for each column
  - Primary key on `id` with auto-increment
  - Foreign key constraint to `users.id` with CASCADE delete

- [ ] **Constraints**
  - `title` is NOT NULL with length constraint (1-200)
  - `description` is nullable with max length 1000
  - `completed` defaults to FALSE
  - `created_at` and `updated_at` auto-populate

- [ ] **Indexes Created**
  - Index on `user_id` for fast user filtering
  - Index on `completed` for status filtering
  - Composite index on `(user_id, completed)`
  - Descending index on `created_at` for sorting

### SQLModel Integration

- [ ] **Model Definition**
  - `Task` class defined with SQLModel
  - All fields have proper types and validators
  - Pydantic validation enabled
  - JSON serialization works correctly

- [ ] **CRUD Operations**
  - Can create tasks with valid data
  - Can query tasks by user_id
  - Can update task fields
  - Can delete tasks
  - Can toggle completed status

### Security

- [ ] **User Isolation**
  - All queries filter by authenticated `user_id`
  - Cannot access other users' tasks
  - 403 Forbidden returned for unauthorized access
  - `user_id` extracted from JWT, not request body

- [ ] **Data Integrity**
  - Foreign key prevents orphaned tasks
  - Cascade delete removes tasks when user deleted
  - Validation prevents invalid data
  - Timestamps automatically managed

### Performance

- [ ] **Query Performance**
  - Queries for user tasks use `idx_tasks_user_id`
  - Filtered queries use composite index
  - Sorting by `created_at` uses index
  - EXPLAIN ANALYZE shows index usage

### Migration

- [ ] **Alembic Migration**
  - Initial migration creates table successfully
  - Migration can be applied: `alembic upgrade head`
  - Migration can be rolled back: `alembic downgrade -1`
  - Migration script includes all indexes

---

## Integration with Better Auth

### User Table Reference

**Better Auth manages the `users` table**:
- Creates users on signup
- Handles password hashing
- Issues JWT tokens
- Manages user sessions

**Backend responsibilities**:
1. **Read user data**: Query `users` table to validate `user_id`
2. **Reference users**: Store `user_id` foreign key in tasks
3. **Respect cascade**: Tasks deleted when user deleted

**Integration Flow**:
```
1. User signs up via Better Auth → users table updated
2. Better Auth issues JWT with user_id claim
3. Frontend sends JWT in Authorization header
4. Backend extracts user_id from JWT
5. Backend creates/queries tasks with that user_id
6. Foreign key ensures referential integrity
```

**Example User Validation** (Optional):
```python
from sqlmodel import Session, select

def validate_user_exists(user_id: str, session: Session) -> bool:
    """
    Optional: Verify user_id exists in users table.
    Better Auth ensures this, but can add extra validation.
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user is not None
```

---

## Testing Checklist

### Unit Tests

- [ ] Test task creation with valid data
- [ ] Test task creation with invalid title (empty, too long)
- [ ] Test task creation with invalid description (too long)
- [ ] Test task query filtering by user_id
- [ ] Test task update with valid data
- [ ] Test task deletion
- [ ] Test cascade delete when user removed

### Integration Tests

- [ ] Test database connection to Neon
- [ ] Test migration apply and rollback
- [ ] Test index creation
- [ ] Test foreign key constraint
- [ ] Test concurrent user operations

### Security Tests

- [ ] Test user cannot access other users' tasks
- [ ] Test invalid JWT returns 401
- [ ] Test mismatched user_id returns 403
- [ ] Test SQL injection attempts
- [ ] Test input validation

---

## Notes

**Technology Stack**:
- **ORM**: SQLModel 0.0.14+
- **Database**: Neon Serverless PostgreSQL
- **Migration Tool**: Alembic 1.13+
- **Validation**: Pydantic (via SQLModel)

**Performance Considerations**:
- Neon provides automatic connection pooling
- Indexes optimized for common query patterns
- Use `pool_pre_ping=True` to handle stale connections
- Consider `updated_at` trigger for automatic updates

**Future Enhancements** (Out of Scope):
- Task tags/categories
- Task due dates
- Task priority levels
- Task attachments
- Task comments
- Full-text search on title/description

---

## Cross-References

- **Authentication Spec**: `specs/003-fastapi-backend/features/authentication.md`
- **API Endpoints Spec**: `specs/003-fastapi-backend/api/rest-endpoints.md`
- **Task CRUD Spec**: `specs/003-fastapi-backend/features/task-crud.md`
- **Integration Guide**: `specs/003-fastapi-backend/integration.md`

---

**Document Status**: Ready for Planning (`/sp.plan`)
