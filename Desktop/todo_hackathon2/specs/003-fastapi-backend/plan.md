# Implementation Plan: FastAPI Backend for Todo Application

**Feature**: FastAPI Backend with JWT Authentication and Task CRUD
**Created**: 2026-01-05
**Branch**: `003-fastapi-backend`
**Status**: Planning Complete

## Executive Summary

This plan details the implementation of a production-ready FastAPI backend for the Todo application. The backend provides JWT-authenticated REST API endpoints for task CRUD operations, enforces strict user isolation, and integrates seamlessly with the existing Next.js frontend and Better Auth authentication system.

**Key Technologies**:
- FastAPI 0.100+ (REST API framework)
- SQLModel 0.0.14+ (ORM with Pydantic integration)
- PyJWT (JWT token verification)
- Neon PostgreSQL (serverless database)
- UV (Python dependency management)
- Uvicorn (ASGI server)

**Integration Points**:
- Frontend: Next.js 16 at `http://localhost:3000`
- Authentication: Better Auth JWT tokens (shared `BETTER_AUTH_SECRET`)
- Database: Neon PostgreSQL with connection pooling

---

## Technical Context

### Dependencies

**Specifications**:
- ✅ [Database Schema](database/schema.md) - SQLModel Task model, indexes, Neon PostgreSQL config
- ✅ [Authentication](features/authentication.md) - JWT verification, FastAPI dependencies
- ✅ [REST API Endpoints](api/rest-endpoints.md) - 6 CRUD endpoints with contracts
- ✅ [Task CRUD Operations](features/task-crud.md) - User stories, implementation details

**External Systems**:
- Better Auth (frontend): Issues JWT tokens with `{sub: user_id, email, exp, aud, iss}`
- Neon PostgreSQL: Serverless database with connection pooler
- Frontend API Client: Sends requests with `Authorization: Bearer <token>` header

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | FastAPI | 0.100+ | REST API with auto-validation |
| ORM | SQLModel | 0.0.14+ | Type-safe database models |
| Database | PostgreSQL (Neon) | Latest | Serverless PostgreSQL |
| JWT | PyJWT | Latest | Token signature verification |
| Validation | Pydantic | 2.0+ | Request/response validation |
| Server | Uvicorn | Latest | ASGI application server |
| Package Manager | UV | Latest | Fast Python dependency management |

### Architecture Decisions

**1. Stateless Authentication**
- **Decision**: JWT tokens verified on every request, no server-side sessions
- **Rationale**: Scalable, works with serverless, follows REST principles
- **Alternatives Considered**: Session-based auth (rejected: requires state, not serverless-friendly)

**2. User Isolation at Query Level**
- **Decision**: All database queries filter by `user_id` from JWT
- **Rationale**: Security-first design, prevents data leakage
- **Alternatives Considered**: Application-level filtering (rejected: error-prone, easy to forget)

**3. FastAPI Dependency Injection for Auth**
- **Decision**: Use `Depends(get_current_user_id)` on all routes
- **Rationale**: DRY principle, automatic auth enforcement, testable
- **Alternatives Considered**: Manual JWT extraction per route (rejected: repetitive, error-prone)

**4. SQLModel for ORM**
- **Decision**: SQLModel (SQLAlchemy + Pydantic hybrid)
- **Rationale**: Type safety, integrates with FastAPI validation, reduces boilerplate
- **Alternatives Considered**: Raw SQLAlchemy (rejected: more verbose), Django ORM (rejected: wrong framework)

**5. UV for Dependency Management**
- **Decision**: Use UV instead of pip/poetry
- **Rationale**: Fast installs, lock file support, modern Python tooling
- **Alternatives Considered**: pip (rejected: slow, no lock file), poetry (rejected: slower than UV)

### File Structure

```
backend/
├── .env.example              # Environment variable template
├── .env                      # Environment variables (gitignored)
├── pyproject.toml            # UV project configuration
├── uv.lock                   # UV lock file
├── alembic.ini               # Alembic migration config
├── alembic/
│   ├── env.py                # Migration environment
│   └── versions/             # Migration files
│       └── 001_initial_schema.py
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application entry point
│   ├── config.py             # Settings and environment variables
│   ├── database.py           # Database connection and session
│   ├── models.py             # SQLModel Task class
│   ├── schemas.py            # Pydantic request/response models
│   ├── auth.py               # JWT verification and dependencies
│   └── routers/
│       ├── __init__.py
│       └── tasks.py          # Task CRUD endpoints
└── tests/
    ├── __init__.py
    ├── conftest.py           # Pytest fixtures
    ├── test_auth.py          # Authentication tests
    └── test_tasks.py         # Task CRUD tests
```

### Environment Variables

**Required**:
- `DATABASE_URL` - Neon PostgreSQL connection string with pooler
- `BETTER_AUTH_SECRET` - Shared secret for JWT verification (same as frontend)

**Optional**:
- `JWT_ALGORITHM` - Default: "HS256"
- `JWT_AUDIENCE` - Default: "http://localhost:3000"
- `JWT_ISSUER` - Default: "better-auth"
- `CORS_ORIGINS` - Default: "http://localhost:3000"

### Performance Considerations

**Database Indexes** (from schema.md):
- `idx_tasks_user_id` - Fast user task filtering
- `idx_tasks_completed` - Status-based filtering
- `idx_tasks_user_completed` - Composite index for combined filters
- `idx_tasks_created_at` - Chronological sorting

**Connection Pooling**:
- Neon pooler: Max 100 connections
- SQLModel engine: pool_size=5, max_overflow=10
- Connection recycling: 3600 seconds (1 hour)

### Security Requirements

**Authentication**:
- ✅ JWT signature verification on every request
- ✅ Token expiration validation
- ✅ Audience and issuer validation
- ✅ Extract user_id from `sub` claim only

**User Isolation**:
- ✅ All queries filter by authenticated user_id
- ✅ Ownership verification before read/update/delete
- ✅ Return 403 for ownership violations
- ✅ Never accept user_id from request body/params

**Error Handling**:
- ✅ Generic error messages (no sensitive info)
- ✅ Proper HTTP status codes (401, 403, 404, 400, 500)
- ✅ No stack traces in production responses

---

## Constitution Check

### Principle I: No Manual Coding ✅
- Implementation achieved through specifications and Claude Code agents
- All code generated from specs in `specs/003-fastapi-backend/`

### Principle II: Spec-Driven Development ✅
- Database schema specified in [schema.md](database/schema.md)
- Authentication specified in [authentication.md](features/authentication.md)
- API contracts specified in [rest-endpoints.md](api/rest-endpoints.md)
- CRUD operations specified in [task-crud.md](features/task-crud.md)
- All specs include user stories and acceptance criteria

### Principle III: Agentic Workflow ✅
- Following complete cycle: Specify → Plan (current) → Tasks → Implement
- Next step: `/sp.tasks` to generate atomic tasks
- Implementation via specialized agents (fastapi-backend-engineer)

### Principle IV: Clean Architecture ✅
- **Structure**: Clear separation (models, schemas, auth, routers, database)
- **Type Safety**: Pydantic models, SQLModel types, full type hints
- **Security**: JWT verification, user isolation, environment variables
- **Quality**: Error handling, proper status codes, comprehensive validation

### Principle V: User Isolation ✅
- Every task has `user_id` foreign key (NOT NULL)
- All queries filter by authenticated user's ID from JWT
- API returns 403 for unauthorized access attempts
- Ownership verified before read/update/delete operations

### Principle VI: Incremental Delivery ✅
- Plan structured in phases (Foundation → Database → Auth → Routes → Testing)
- Each phase delivers independently testable functionality
- Phase 1 delivers basic API structure
- Phase 2 adds database models
- Phase 3 adds authentication
- Phase 4 completes CRUD endpoints
- Phase 5 polishes and tests

### Principle VII: Documentation ✅
- All architectural decisions documented in this plan
- PHR will be created after plan completion
- ADR suggested for JWT verification approach

### Technology Stack Compliance ✅
- ✅ FastAPI 0.100+ (backend framework)
- ✅ SQLModel 0.0.14+ (ORM)
- ✅ Neon PostgreSQL (database)
- ✅ Better Auth integration (JWT tokens)
- ✅ Shared `BETTER_AUTH_SECRET` for JWT verification

### Security & Architecture Standards ✅
- ✅ JWT in Authorization header: `Bearer <token>`
- ✅ Backend verifies JWT signature
- ✅ `user_id` extracted from verified token
- ✅ All queries filtered by `user_id`
- ✅ Proper error responses (401, 403, 404)
- ✅ All required endpoints defined (POST, GET, PATCH, DELETE /api/tasks)

**Constitution Gate**: ✅ PASSED - All principles satisfied

---

## Phase 0: Research & Design

**Status**: Complete (specifications already exist)

All research and design completed through specification process:

### ✅ Database Design
- **Source**: [schema.md](database/schema.md)
- **Decisions**: SQLModel Task model, indexes, Neon PostgreSQL
- **Rationale**: Type safety, FastAPI integration, serverless compatibility

### ✅ Authentication Strategy
- **Source**: [authentication.md](features/authentication.md)
- **Decisions**: Stateless JWT, PyJWT library, FastAPI dependencies
- **Rationale**: Scalable, integrates with Better Auth, follows REST principles

### ✅ API Design
- **Source**: [rest-endpoints.md](api/rest-endpoints.md)
- **Decisions**: RESTful endpoints, Pydantic validation, proper HTTP methods
- **Rationale**: Standard conventions, auto-documentation, type safety

### ✅ CRUD Implementation
- **Source**: [task-crud.md](features/task-crud.md)
- **Decisions**: User isolation at query level, ownership verification, idempotent toggle
- **Rationale**: Security-first, prevents data leakage, predictable behavior

**Phase 0 Output**: All specifications complete, no research needed

---

## Phase 1: Project Foundation

**Goal**: Set up backend project structure, dependencies, and configuration

**Prerequisites**: None

### Task 1.1: Initialize Backend Directory Structure

**Objective**: Create organized directory structure for FastAPI backend

**Actions**:
```bash
mkdir -p backend/app/routers
mkdir -p backend/alembic/versions
mkdir -p backend/tests
touch backend/app/__init__.py
touch backend/app/routers/__init__.py
touch backend/tests/__init__.py
```

**Files Created**:
- `backend/` - Root backend directory
- `backend/app/` - Application code
- `backend/app/routers/` - API route handlers
- `backend/alembic/` - Database migrations
- `backend/tests/` - Test suite

**Acceptance Criteria**:
- ✅ All directories exist
- ✅ `__init__.py` files present for Python packages
- ✅ Structure matches plan file structure

---

### Task 1.2: Configure UV and Install Dependencies

**Objective**: Set up UV package manager and install all required dependencies

**Actions**:
1. Create `backend/pyproject.toml`:
```toml
[project]
name = "todo-backend"
version = "0.1.0"
description = "FastAPI backend for Todo application"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "sqlmodel>=0.0.14",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "psycopg2-binary>=2.9.0",
    "pyjwt>=2.8.0",
    "python-dotenv>=1.0.0",
    "alembic>=1.12.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.24.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

2. Install dependencies:
```bash
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

**Dependencies Installed**:
- `fastapi` - REST API framework
- `uvicorn` - ASGI server
- `sqlmodel` - ORM with Pydantic integration
- `pydantic-settings` - Environment variable management
- `psycopg2-binary` - PostgreSQL driver
- `pyjwt` - JWT token verification
- `python-dotenv` - .env file loading
- `alembic` - Database migrations
- `pytest`, `httpx` - Testing (dev)

**Acceptance Criteria**:
- ✅ `pyproject.toml` created with all dependencies
- ✅ Virtual environment created
- ✅ All dependencies installed successfully
- ✅ `uv.lock` file generated

---

### Task 1.3: Create Environment Configuration

**Objective**: Set up environment variables and configuration management

**Actions**:
1. Create `backend/.env.example`:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Authentication
BETTER_AUTH_SECRET=your-shared-secret-here

# JWT Configuration
JWT_ALGORITHM=HS256
JWT_AUDIENCE=http://localhost:3000
JWT_ISSUER=better-auth

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

2. Create `backend/app/config.py`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str

    # Authentication
    better_auth_secret: str
    jwt_algorithm: str = "HS256"
    jwt_audience: str = "http://localhost:3000"
    jwt_issuer: str = "better-auth"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# Global settings instance
settings = Settings()
```

**Files Created**:
- `backend/.env.example` - Template for environment variables
- `backend/app/config.py` - Pydantic settings class

**Acceptance Criteria**:
- ✅ `.env.example` contains all required variables
- ✅ `config.py` uses Pydantic Settings for type-safe config
- ✅ Settings can be imported: `from app.config import settings`
- ✅ `.env` added to `.gitignore`

---

### Task 1.4: Set Up Database Connection

**Objective**: Configure SQLModel database engine and session management

**Reference**: [schema.md](database/schema.md) - Database connection configuration

**Actions**:
Create `backend/app/database.py`:
```python
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings
from typing import Generator

# Create SQLModel engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=False,  # Set True for SQL query logging in development
    pool_size=5,  # Max 5 persistent connections
    max_overflow=10,  # Max 10 additional connections if pool exhausted
    pool_pre_ping=True,  # Verify connections before use (detect stale connections)
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "sslmode": "require",  # Neon PostgreSQL requires SSL
    }
)

def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Usage:
        @router.get("/tasks")
        async def list_tasks(session: Session = Depends(get_session)):
            # Use session here

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """
    Create all database tables.

    Note: In production, use Alembic migrations instead.
    This is useful for local development and testing.
    """
    SQLModel.metadata.create_all(engine)
```

**Database Configuration**:
- **Connection Pooling**: 5 persistent connections, up to 10 overflow
- **Connection Recycling**: Connections recycled after 1 hour
- **Pre-ping**: Verifies connections before use (prevents stale connection errors)
- **SSL**: Required for Neon PostgreSQL

**Acceptance Criteria**:
- ✅ `database.py` created with engine and session factory
- ✅ Connection pooling configured per schema.md specifications
- ✅ `get_session()` dependency ready for FastAPI routes
- ✅ SSL enabled for Neon PostgreSQL

---

### Task 1.5: Create Main FastAPI Application

**Objective**: Set up FastAPI application with CORS middleware

**Actions**:
Create `backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_db_and_tables

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="FastAPI backend for Todo application with JWT authentication",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers including Authorization
)

@app.on_event("startup")
def on_startup():
    """Create database tables on application startup."""
    create_db_and_tables()

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Todo API is running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check for monitoring."""
    return {"status": "healthy"}

# Import and include routers (will be added in later phases)
# from app.routers import tasks
# app.include_router(tasks.router)
```

**CORS Configuration**:
- **Origins**: Frontend URL (`http://localhost:3000`)
- **Credentials**: Enabled (allows cookies and Authorization header)
- **Methods**: All HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **Headers**: All headers (required for Authorization header)

**Acceptance Criteria**:
- ✅ FastAPI app created with title and description
- ✅ CORS middleware configured for frontend origin
- ✅ Health check endpoints (`/` and `/health`) implemented
- ✅ Database table creation on startup
- ✅ OpenAPI docs available at `/docs` and `/redoc`

---

### Task 1.6: Verify Foundation Setup

**Objective**: Test that the basic FastAPI server starts successfully

**Actions**:
1. Create `backend/.env` file (copy from `.env.example` and fill in values)
2. Start the development server:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Test endpoints:
```bash
# Health check
curl http://localhost:8000/health

# OpenAPI docs
open http://localhost:8000/docs
```

**Expected Results**:
- Server starts without errors
- Health check returns `{"status": "healthy"}`
- OpenAPI documentation accessible at `/docs`

**Acceptance Criteria**:
- ✅ Server starts successfully on port 8000
- ✅ Health check endpoint responds
- ✅ OpenAPI documentation loads
- ✅ No import errors or missing dependencies

---

**Phase 1 Summary**:
- ✅ Backend directory structure created
- ✅ UV dependencies installed
- ✅ Environment configuration set up
- ✅ Database connection configured
- ✅ FastAPI app with CORS created
- ✅ Server verified running

**Phase 1 Deliverable**: Working FastAPI server with health checks and OpenAPI docs

---

## Phase 2: Database Models

**Goal**: Implement SQLModel Task class and database migrations

**Prerequisites**: Phase 1 complete

### Task 2.1: Create SQLModel Task Model

**Objective**: Implement Task database model with all fields and validations

**Reference**: [schema.md](database/schema.md) - Task model specification

**Actions**:
Create `backend/app/models.py`:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.

    Security: Every task MUST be associated with a user_id.
    All queries MUST filter by authenticated user's ID.
    """
    __tablename__ = "tasks"

    # Primary key
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-generated task ID"
    )

    # Foreign key to Better Auth users table
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
        description="Owner's user ID from Better Auth"
    )

    # Task content
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required, 1-200 characters)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional, max 1000 characters)"
    )

    # Status
    completed: bool = Field(
        default=False,
        index=True,
        description="Completion status (default: false)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task last update timestamp (UTC)"
    )

    class Config:
        """SQLModel configuration."""
        # Add composite index for common query pattern
        indexes = [
            ("user_id", "completed"),  # For filtered queries
        ]
```

**Model Features**:
- **Primary Key**: Auto-incrementing `id`
- **Foreign Key**: `user_id` references Better Auth users table
- **Validation**: Title (1-200 chars), Description (max 1000 chars)
- **Indexes**: `user_id`, `completed`, composite `(user_id, completed)`
- **Timestamps**: Auto-populated `created_at` and `updated_at`

**Acceptance Criteria**:
- ✅ Task model inherits from `SQLModel` with `table=True`
- ✅ All fields match schema.md specification
- ✅ Field validation using Pydantic Field()
- ✅ Indexes defined for performance
- ✅ Foreign key constraint on user_id
- ✅ Timestamps with UTC default

---

### Task 2.2: Create Pydantic Request/Response Schemas

**Objective**: Define Pydantic models for API validation

**Reference**: [rest-endpoints.md](api/rest-endpoints.md) - Pydantic models

**Actions**:
Create `backend/app/schemas.py`:
```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Request Schemas

class TaskCreate(BaseModel):
    """
    Request schema for creating a new task.

    Validation:
    - title: Required, 1-200 characters
    - description: Optional, max 1000 characters

    Note: user_id is NOT accepted from request (set from JWT)
    """
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title",
        examples=["Complete backend API implementation"]
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional task description",
        examples=["Implement all REST endpoints with FastAPI and SQLModel"]
    )

class TaskUpdate(BaseModel):
    """
    Request schema for updating an existing task.

    Validation:
    - title: Required, 1-200 characters
    - description: Optional, max 1000 characters

    Note: completed status is NOT updated here (use PATCH /complete endpoint)
    """
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

# Response Schemas

class TaskResponse(BaseModel):
    """
    Response schema for task data.

    Frontend Compatibility:
    - Uses 'is_completed' alias for 'completed' field
    - Frontend expects 'is_completed' but database stores 'completed'
    """
    id: int
    user_id: str
    title: str
    description: Optional[str]
    is_completed: bool = Field(alias="completed")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode (SQLModel -> Pydantic)
        populate_by_name=True  # Allow both 'completed' and 'is_completed'
    )

class TaskListResponse(BaseModel):
    """Response schema for task list with metadata."""
    tasks: list[TaskResponse]
    total: int
    status_filter: str
    sort_by: str

class DeleteResponse(BaseModel):
    """Response schema for delete operations."""
    message: str
    deleted_task_id: int
```

**Schema Features**:
- **Request Validation**: Pydantic Field() with min/max length
- **Response Mapping**: TaskResponse converts SQLModel to JSON
- **Frontend Compatibility**: `is_completed` alias for `completed`
- **ORM Mode**: `from_attributes=True` enables SQLModel conversion

**Acceptance Criteria**:
- ✅ TaskCreate and TaskUpdate for request validation
- ✅ TaskResponse with is_completed alias
- ✅ TaskListResponse with metadata
- ✅ DeleteResponse for delete confirmations
- ✅ All schemas match rest-endpoints.md specification

---

### Task 2.3: Initialize Alembic for Migrations

**Objective**: Set up Alembic for database schema migrations

**Actions**:
1. Initialize Alembic:
```bash
cd backend
alembic init alembic
```

2. Configure `backend/alembic/env.py`:
```python
from logging.config import fileConfig
from sqlmodel import SQLModel
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import app config and models
from app.config import settings
from app.models import Task  # Import all models

# Alembic Config object
config = context.config

# Set database URL from settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata from SQLModel
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

3. Create initial migration:
```bash
alembic revision --autogenerate -m "Initial schema: tasks table"
```

4. Apply migration:
```bash
alembic upgrade head
```

**Migration Features**:
- Auto-generates migrations from SQLModel metadata
- Connects to Neon PostgreSQL via DATABASE_URL
- Creates tasks table with all indexes and constraints

**Acceptance Criteria**:
- ✅ Alembic initialized in `backend/alembic/`
- ✅ `env.py` configured with SQLModel metadata
- ✅ Initial migration created
- ✅ Migration applied successfully to database
- ✅ Tasks table exists with all columns and indexes

---

**Phase 2 Summary**:
- ✅ Task SQLModel created with validation
- ✅ Pydantic request/response schemas defined
- ✅ Alembic migrations configured
- ✅ Database schema deployed

**Phase 2 Deliverable**: Database with tasks table ready for CRUD operations

---

## Phase 3: JWT Authentication

**Goal**: Implement JWT token verification and FastAPI authentication dependencies

**Prerequisites**: Phase 2 complete

### Task 3.1: Implement JWT Verification

**Objective**: Create JWT token verification function with PyJWT

**Reference**: [authentication.md](features/authentication.md) - JWT verification implementation

**Actions**:
Create `backend/app/auth.py`:
```python
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.config import settings

# HTTP Bearer scheme for extracting JWT from Authorization header
bearer_scheme = HTTPBearer()

class TokenData(BaseModel):
    """Decoded JWT token data."""
    user_id: str
    email: str

def verify_jwt_token(token: str) -> TokenData:
    """
    Verify JWT token signature and extract user information.

    Security Checks:
    1. Signature verification (using BETTER_AUTH_SECRET)
    2. Expiration validation
    3. Audience validation (frontend URL)
    4. Issuer validation (better-auth)

    Args:
        token: JWT token string from Authorization header

    Returns:
        TokenData: Decoded token with user_id and email

    Raises:
        HTTPException(401): If token is invalid, expired, or malformed

    Better Auth JWT Format:
    {
        "sub": "user_2mK8jX9pL3nQ5vR",  # user_id
        "email": "user@example.com",
        "name": "John Doe",
        "exp": 1672531200,
        "aud": "http://localhost:3000",
        "iss": "better-auth"
    }
    """
    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            settings.better_auth_secret,  # Shared secret with frontend
            algorithms=[settings.jwt_algorithm],  # HS256
            audience=settings.jwt_audience,  # http://localhost:3000
            issuer=settings.jwt_issuer,  # better-auth
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )

        # Extract user information
        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return TokenData(user_id=user_id, email=email)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> TokenData:
    """
    FastAPI dependency to extract and verify current user from JWT.

    Usage:
        @router.get("/tasks")
        async def list_tasks(
            current_user: TokenData = Depends(get_current_user)
        ):
            user_id = current_user.user_id
            # Use user_id to filter tasks

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        TokenData: Verified user information

    Raises:
        HTTPException(401): If token is missing or invalid
    """
    token = credentials.credentials
    return verify_jwt_token(token)

async def get_current_user_id(
    current_user: TokenData = Depends(get_current_user)
) -> str:
    """
    Convenience dependency to get just the user_id.

    Usage:
        @router.post("/tasks")
        async def create_task(
            task_data: TaskCreate,
            user_id: str = Depends(get_current_user_id)
        ):
            # user_id is guaranteed to be from verified JWT

    Args:
        current_user: Verified user from get_current_user dependency

    Returns:
        str: Authenticated user's ID
    """
    return current_user.user_id
```

**Authentication Features**:
- **JWT Verification**: Signature, expiration, audience, issuer
- **Token Extraction**: From `Authorization: Bearer <token>` header
- **FastAPI Dependencies**: `get_current_user()` and `get_current_user_id()`
- **Error Handling**: 401 for invalid/expired tokens
- **Security**: Never trusts user_id from request body

**Acceptance Criteria**:
- ✅ `verify_jwt_token()` verifies all JWT claims
- ✅ `get_current_user()` dependency extracts user from token
- ✅ `get_current_user_id()` convenience dependency
- ✅ HTTPBearer scheme configured
- ✅ Returns 401 for missing/invalid/expired tokens
- ✅ All security checks match authentication.md

---

### Task 3.2: Test Authentication Dependencies

**Objective**: Create tests for JWT verification and authentication

**Actions**:
Create `backend/tests/test_auth.py`:
```python
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.auth import verify_jwt_token, TokenData
from app.config import settings

def create_test_token(user_id: str = "test_user_123", expired: bool = False) -> str:
    """Helper to create test JWT tokens."""
    exp = datetime.utcnow() - timedelta(hours=1) if expired else datetime.utcnow() + timedelta(hours=1)

    payload = {
        "sub": user_id,
        "email": "test@example.com",
        "name": "Test User",
        "exp": exp,
        "aud": settings.jwt_audience,
        "iss": settings.jwt_issuer,
    }

    return jwt.encode(payload, settings.better_auth_secret, algorithm=settings.jwt_algorithm)

def test_verify_valid_token():
    """Test JWT verification with valid token."""
    token = create_test_token()
    token_data = verify_jwt_token(token)

    assert isinstance(token_data, TokenData)
    assert token_data.user_id == "test_user_123"
    assert token_data.email == "test@example.com"

def test_verify_expired_token():
    """Test JWT verification with expired token."""
    token = create_test_token(expired=True)

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(token)

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()

def test_verify_invalid_signature():
    """Test JWT verification with wrong secret."""
    payload = {
        "sub": "test_user_123",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "aud": settings.jwt_audience,
        "iss": settings.jwt_issuer,
    }

    # Sign with wrong secret
    token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(token)

    assert exc_info.value.status_code == 401

def test_verify_missing_user_id():
    """Test JWT verification with missing 'sub' claim."""
    payload = {
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "aud": settings.jwt_audience,
        "iss": settings.jwt_issuer,
    }

    token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(token)

    assert exc_info.value.status_code == 401
    assert "missing user ID" in exc_info.value.detail
```

**Test Coverage**:
- ✅ Valid token verification
- ✅ Expired token rejection
- ✅ Invalid signature rejection
- ✅ Missing user_id claim rejection

**Acceptance Criteria**:
- ✅ All authentication tests pass
- ✅ Valid tokens accepted
- ✅ Invalid/expired tokens rejected with 401
- ✅ Error messages user-friendly

---

**Phase 3 Summary**:
- ✅ JWT verification implemented with PyJWT
- ✅ FastAPI authentication dependencies created
- ✅ Authentication tests passing

**Phase 3 Deliverable**: Secure JWT authentication ready for protecting routes

---

## Phase 4: Task CRUD Endpoints

**Goal**: Implement all 6 task CRUD endpoints with user isolation

**Prerequisites**: Phase 3 complete

### Task 4.1: Implement Create Task Endpoint

**Objective**: POST /api/tasks - Create new task for authenticated user

**Reference**: [task-crud.md](features/task-crud.md) - Create Task Operation

**Actions**:
Create `backend/app/routers/tasks.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from datetime import datetime
from typing import Literal

from app.database import get_session
from app.auth import get_current_user_id
from app.models import Task
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    DeleteResponse
)

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["tasks"])

@router.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    Security:
    - user_id is ALWAYS set from JWT (current_user_id)
    - Never accept user_id from request body

    Args:
        task_data: Task title and optional description
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        TaskResponse: Created task with auto-generated ID

    Raises:
        400: Validation error (title too long, etc.)
        401: Missing or invalid JWT token
    """
    # Create new task with authenticated user_id
    new_task = Task(
        user_id=current_user_id,  # Security: From JWT, never from request
        title=task_data.title,
        description=task_data.description,
        completed=False,  # New tasks default to incomplete
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Insert into database
    session.add(new_task)
    session.commit()
    session.refresh(new_task)  # Get auto-generated ID

    return TaskResponse.model_validate(new_task)
```

**Endpoint Features**:
- **Method**: POST
- **Path**: `/api/tasks`
- **Auth**: Required (JWT token)
- **Request**: TaskCreate (title, optional description)
- **Response**: 201 Created with task object
- **Security**: user_id from JWT, never from request

**Acceptance Criteria**:
- ✅ POST /api/tasks creates task
- ✅ user_id set from JWT, not request body
- ✅ Returns 201 Created with task object
- ✅ Returns 401 for missing/invalid token
- ✅ Returns 400 for validation errors
- ✅ Title validated (1-200 chars)
- ✅ Description validated (max 1000 chars)

---

### Task 4.2: Implement List Tasks Endpoint

**Objective**: GET /api/tasks - List tasks with filtering and sorting

**Reference**: [task-crud.md](features/task-crud.md) - List Tasks Operation

**Actions**:
Add to `backend/app/routers/tasks.py`:
```python
@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    status_filter: Literal["all", "pending", "completed"] = Query(
        default="all",
        alias="status",
        description="Filter by completion status"
    ),
    sort: Literal["created", "title", "updated"] = Query(
        default="created",
        description="Sort order"
    ),
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskListResponse:
    """
    List all tasks for the authenticated user with filtering and sorting.

    Security:
    - Queries are ALWAYS filtered by current_user_id from JWT
    - User cannot see other users' tasks

    Performance:
    - Uses index on (user_id, completed) for filtered queries
    - Uses index on created_at for created sort

    Args:
        status_filter: "all" (default) | "pending" | "completed"
        sort: "created" (default, newest first) | "title" (A-Z) | "updated"
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        TaskListResponse: Tasks array, total count, applied filters

    Raises:
        400: Invalid query parameters
        401: Missing or invalid JWT token
    """
    # Base query: Filter by authenticated user
    query = select(Task).where(Task.user_id == current_user_id)

    # Apply status filter
    if status_filter == "pending":
        query = query.where(Task.completed == False)
    elif status_filter == "completed":
        query = query.where(Task.completed == True)
    # status_filter == "all": no additional filter

    # Apply sorting
    if sort == "created":
        query = query.order_by(Task.created_at.desc())  # Newest first
    elif sort == "title":
        query = query.order_by(Task.title.asc())  # Alphabetical A-Z
    elif sort == "updated":
        query = query.order_by(Task.updated_at.desc())  # Most recently updated

    # Execute query
    tasks = session.exec(query).all()

    # Build response
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
        status_filter=status_filter,
        sort_by=sort
    )
```

**Endpoint Features**:
- **Method**: GET
- **Path**: `/api/tasks?status=pending&sort=created`
- **Auth**: Required (JWT token)
- **Query Params**: status (all/pending/completed), sort (created/title/updated)
- **Response**: 200 OK with tasks array and metadata
- **Security**: Filters by authenticated user_id

**Acceptance Criteria**:
- ✅ GET /api/tasks lists tasks for authenticated user
- ✅ status=all returns all tasks
- ✅ status=pending returns incomplete tasks
- ✅ status=completed returns complete tasks
- ✅ sort=created sorts by created_at descending
- ✅ sort=title sorts alphabetically
- ✅ sort=updated sorts by updated_at descending
- ✅ Returns empty array when user has no tasks
- ✅ Returns 401 for missing/invalid token

---

### Task 4.3: Implement Get Single Task Endpoint

**Objective**: GET /api/tasks/{id} - Get task with ownership verification

**Reference**: [task-crud.md](features/task-crud.md) - Get Single Task Operation

**Actions**:
Add to `backend/app/routers/tasks.py`:
```python
@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Get a single task by ID.

    Security:
    - Verifies task belongs to authenticated user
    - Returns 403 if task owned by different user

    Args:
        task_id: Task ID from path parameter
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        TaskResponse: Task details

    Raises:
        404: Task doesn't exist
        403: Task belongs to another user
        401: Missing or invalid JWT token
    """
    # Query by ID
    task = session.get(Task, task_id)

    # Check existence
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Security: Verify ownership BEFORE returning data
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    return TaskResponse.model_validate(task)
```

**Endpoint Features**:
- **Method**: GET
- **Path**: `/api/tasks/{id}`
- **Auth**: Required (JWT token)
- **Response**: 200 OK with task details
- **Security**: Ownership verification before returning data

**Acceptance Criteria**:
- ✅ GET /api/tasks/{id} returns task when owned by user
- ✅ Returns 404 when task doesn't exist
- ✅ Returns 403 when task owned by different user
- ✅ Returns 401 for missing/invalid token
- ✅ Ownership verified before returning data

---

### Task 4.4: Implement Update Task Endpoint

**Objective**: PUT /api/tasks/{id} - Update task title/description

**Reference**: [task-crud.md](features/task-crud.md) - Update Task Operation

**Actions**:
Add to `backend/app/routers/tasks.py`:
```python
@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Update task title and description.

    Security:
    - Verifies task belongs to authenticated user before updating
    - user_id cannot be changed (immutable)

    Updates:
    - title: Required, 1-200 chars
    - description: Optional, max 1000 chars
    - updated_at: Automatically set to current UTC time

    Does NOT Update:
    - completed: Use PATCH /tasks/{id}/complete endpoint
    - created_at: Immutable
    - user_id: Immutable

    Args:
        task_id: Task ID from path parameter
        task_data: Updated title and description
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        TaskResponse: Updated task

    Raises:
        404: Task doesn't exist
        403: Task belongs to another user
        400: Validation error (title too long, etc.)
        401: Missing or invalid JWT token
    """
    # Query by ID
    task = session.get(Task, task_id)

    # Check existence
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Security: Verify ownership before allowing update
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task"
        )

    # Update fields
    task.title = task_data.title
    task.description = task_data.description
    task.updated_at = datetime.utcnow()

    # Commit changes
    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)
```

**Endpoint Features**:
- **Method**: PUT
- **Path**: `/api/tasks/{id}`
- **Auth**: Required (JWT token)
- **Request**: TaskUpdate (title, optional description)
- **Response**: 200 OK with updated task
- **Security**: Ownership verification before update

**Acceptance Criteria**:
- ✅ PUT /api/tasks/{id} updates task when owned by user
- ✅ Updates title and description
- ✅ updated_at timestamp refreshed
- ✅ created_at unchanged
- ✅ completed status NOT modified
- ✅ Returns 404 when task doesn't exist
- ✅ Returns 403 when task owned by different user
- ✅ Returns 401 for missing/invalid token
- ✅ Returns 400 for validation errors

---

### Task 4.5: Implement Delete Task Endpoint

**Objective**: DELETE /api/tasks/{id} - Delete task permanently

**Reference**: [task-crud.md](features/task-crud.md) - Delete Task Operation

**Actions**:
Add to `backend/app/routers/tasks.py`:
```python
@router.delete("/tasks/{task_id}", response_model=DeleteResponse)
async def delete_task(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> DeleteResponse:
    """
    Delete a task permanently.

    Security:
    - Verifies task belongs to authenticated user before deletion
    - Cannot be undone

    Args:
        task_id: Task ID from path parameter
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        DeleteResponse: Success message with deleted task ID

    Raises:
        404: Task doesn't exist
        403: Task belongs to another user
        401: Missing or invalid JWT token
    """
    # Query by ID
    task = session.get(Task, task_id)

    # Check existence
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Security: Verify ownership before allowing deletion
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    # Delete from database
    session.delete(task)
    session.commit()

    return DeleteResponse(
        message="Task deleted successfully",
        deleted_task_id=task_id
    )
```

**Endpoint Features**:
- **Method**: DELETE
- **Path**: `/api/tasks/{id}`
- **Auth**: Required (JWT token)
- **Response**: 200 OK with success message
- **Security**: Ownership verification before deletion

**Acceptance Criteria**:
- ✅ DELETE /api/tasks/{id} deletes task when owned by user
- ✅ Returns success message with deleted task ID
- ✅ Task permanently removed from database
- ✅ Subsequent GET returns 404
- ✅ Returns 404 when task doesn't exist
- ✅ Returns 403 when task owned by different user
- ✅ Returns 401 for missing/invalid token

---

### Task 4.6: Implement Toggle Completion Endpoint

**Objective**: PATCH /api/tasks/{id}/complete - Toggle completion status

**Reference**: [task-crud.md](features/task-crud.md) - Toggle Task Completion

**Actions**:
Add to `backend/app/routers/tasks.py`:
```python
@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Toggle task completion status (true ↔ false).

    Security:
    - Verifies task belongs to authenticated user before toggling

    Behavior:
    - false → true (mark as complete)
    - true → false (mark as incomplete)
    - Idempotent: Can be called multiple times to toggle back and forth

    Updates:
    - completed: Toggles boolean value
    - updated_at: Set to current UTC time

    Does NOT Update:
    - title, description: Unchanged
    - created_at: Immutable

    Args:
        task_id: Task ID from path parameter
        current_user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        TaskResponse: Updated task with new completed status

    Raises:
        404: Task doesn't exist
        403: Task belongs to another user
        401: Missing or invalid JWT token
    """
    # Query by ID
    task = session.get(Task, task_id)

    # Check existence
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Security: Verify ownership before allowing status change
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task"
        )

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    # Commit changes
    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)
```

**Endpoint Features**:
- **Method**: PATCH
- **Path**: `/api/tasks/{id}/complete`
- **Auth**: Required (JWT token)
- **Response**: 200 OK with updated task
- **Behavior**: Idempotent toggle (can call multiple times)

**Acceptance Criteria**:
- ✅ PATCH /api/tasks/{id}/complete toggles status
- ✅ false → true when currently incomplete
- ✅ true → false when currently complete
- ✅ updated_at timestamp refreshed
- ✅ Title and description unchanged
- ✅ Idempotent (can toggle multiple times)
- ✅ Returns 404 when task doesn't exist
- ✅ Returns 403 when task owned by different user
- ✅ Returns 401 for missing/invalid token

---

### Task 4.7: Register Task Router in Main App

**Objective**: Include task router in FastAPI application

**Actions**:
Update `backend/app/main.py`:
```python
# ... existing imports ...
from app.routers import tasks

# ... existing app setup ...

# Include task router
app.include_router(tasks.router)

# ... rest of main.py ...
```

**Acceptance Criteria**:
- ✅ Task router registered with `/api` prefix
- ✅ All 6 endpoints accessible
- ✅ OpenAPI docs show all task endpoints
- ✅ CORS applies to all task routes

---

**Phase 4 Summary**:
- ✅ All 6 CRUD endpoints implemented
- ✅ User isolation enforced on all routes
- ✅ Ownership verification before sensitive operations
- ✅ Proper error handling (401, 403, 404, 400)

**Phase 4 Deliverable**: Complete REST API with JWT-protected task CRUD endpoints

---

## Phase 5: Testing and Polish

**Goal**: Test integration, security, and prepare for frontend integration

**Prerequisites**: Phase 4 complete

### Task 5.1: Create Integration Tests

**Objective**: Test complete task lifecycle workflows

**Actions**:
Create `backend/tests/conftest.py`:
```python
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.config import settings

# Test database (in-memory SQLite)
@pytest.fixture(name="session")
def session_fixture():
    """Create test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with test database."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def create_test_token(user_id: str = "test_user_123") -> str:
    """Create valid JWT token for testing."""
    payload = {
        "sub": user_id,
        "email": "test@example.com",
        "name": "Test User",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "aud": settings.jwt_audience,
        "iss": settings.jwt_issuer,
    }
    return jwt.encode(payload, settings.better_auth_secret, algorithm=settings.jwt_algorithm)

@pytest.fixture(name="auth_headers")
def auth_headers_fixture():
    """Create Authorization headers with valid JWT."""
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(name="auth_headers_user2")
def auth_headers_user2_fixture():
    """Create Authorization headers for second test user."""
    token = create_test_token(user_id="test_user_456")
    return {"Authorization": f"Bearer {token}"}
```

Create `backend/tests/test_tasks.py`:
```python
import pytest
from fastapi.testclient import TestClient

def test_create_task_success(client: TestClient, auth_headers: dict):
    """Test creating a task with valid data."""
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Test task", "description": "Test description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["is_completed"] is False
    assert "id" in data

def test_create_task_without_auth(client: TestClient):
    """Test creating a task without authentication fails."""
    response = client.post(
        "/api/tasks",
        json={"title": "Test task"}
    )
    assert response.status_code == 401

def test_list_tasks_user_isolation(
    client: TestClient,
    auth_headers: dict,
    auth_headers_user2: dict
):
    """Test that users only see their own tasks."""
    # User 1 creates task
    client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "User 1 task"}
    )

    # User 2 creates task
    client.post(
        "/api/tasks",
        headers=auth_headers_user2,
        json={"title": "User 2 task"}
    )

    # User 1 lists tasks - should only see their own
    response = client.get("/api/tasks", headers=auth_headers)
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "User 1 task"

def test_get_task_ownership_violation(
    client: TestClient,
    auth_headers: dict,
    auth_headers_user2: dict
):
    """Test that users cannot access other users' tasks."""
    # User 1 creates task
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "User 1 task"}
    )
    task_id = response.json()["id"]

    # User 2 tries to access User 1's task
    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers_user2)
    assert response.status_code == 403

def test_complete_task_lifecycle(client: TestClient, auth_headers: dict):
    """Test complete CRUD lifecycle."""
    # Create
    create_response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Lifecycle test"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Read
    get_response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 200

    # Update
    update_response = client.put(
        f"/api/tasks/{task_id}",
        headers=auth_headers,
        json={"title": "Updated title", "description": "Updated description"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated title"

    # Toggle completion
    toggle_response = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert toggle_response.status_code == 200
    assert toggle_response.json()["is_completed"] is True

    # Delete
    delete_response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    # Verify deletion
    get_deleted = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_deleted.status_code == 404

def test_task_filtering(client: TestClient, auth_headers: dict):
    """Test task filtering by status."""
    # Create pending task
    client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Pending task"}
    )

    # Create completed task
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Completed task"}
    )
    task_id = response.json()["id"]
    client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)

    # Filter pending
    pending_response = client.get("/api/tasks?status=pending", headers=auth_headers)
    assert pending_response.json()["total"] == 1

    # Filter completed
    completed_response = client.get("/api/tasks?status=completed", headers=auth_headers)
    assert completed_response.json()["total"] == 1

    # All tasks
    all_response = client.get("/api/tasks?status=all", headers=auth_headers)
    assert all_response.json()["total"] == 2
```

**Test Coverage**:
- ✅ Create, read, update, delete, toggle operations
- ✅ User isolation (users can't access each other's tasks)
- ✅ Authentication (401 without token)
- ✅ Authorization (403 for wrong user)
- ✅ Filtering by status
- ✅ Complete lifecycle workflow

**Acceptance Criteria**:
- ✅ All integration tests pass
- ✅ User isolation verified
- ✅ Error cases tested (401, 403, 404)
- ✅ Complete CRUD workflow tested

---

### Task 5.2: Test Frontend Integration

**Objective**: Verify backend works with existing Next.js frontend

**Actions**:
1. Ensure `.env` has correct values:
```env
DATABASE_URL=<your-neon-postgresql-url>
BETTER_AUTH_SECRET=<same-secret-as-frontend>
CORS_ORIGINS=http://localhost:3000
```

2. Start backend server:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Start frontend server (from previous phase):
```bash
cd frontend
npm run dev
```

4. Test integration:
   - Open `http://localhost:3000`
   - Log in with Better Auth
   - Create a task → should POST to `http://localhost:8000/api/tasks`
   - View tasks → should GET from `http://localhost:8000/api/tasks`
   - Toggle completion → should PATCH to `http://localhost:8000/api/tasks/{id}/complete`
   - Delete task → should DELETE to `http://localhost:8000/api/tasks/{id}`

5. Verify CORS:
   - Check browser console for CORS errors (should be none)
   - Verify Authorization header sent with all requests

**Integration Checklist**:
- ✅ Frontend can make authenticated requests to backend
- ✅ JWT token sent in Authorization header
- ✅ Backend verifies JWT signature
- ✅ CORS allows requests from localhost:3000
- ✅ All CRUD operations work end-to-end
- ✅ User isolation works (can't see other users' tasks)

**Acceptance Criteria**:
- ✅ Frontend successfully communicates with backend
- ✅ No CORS errors in browser console
- ✅ All task operations work (create, list, update, delete, toggle)
- ✅ Authentication required for all operations
- ✅ User can only see their own tasks

---

### Task 5.3: Security Verification

**Objective**: Verify all security requirements are met

**Security Checklist**:

**Authentication**:
- ✅ All endpoints require valid JWT token
- ✅ JWT signature verified using `BETTER_AUTH_SECRET`
- ✅ Expired tokens rejected with 401
- ✅ Invalid tokens rejected with 401
- ✅ Missing tokens rejected with 401

**User Isolation**:
- ✅ All queries filter by authenticated user_id from JWT
- ✅ user_id never accepted from request body or query params
- ✅ Ownership verified before GET/PUT/DELETE/PATCH operations
- ✅ Users cannot access other users' tasks (403 returned)

**Error Handling**:
- ✅ Generic error messages (no sensitive info leaked)
- ✅ Proper HTTP status codes (200, 201, 400, 401, 403, 404)
- ✅ No stack traces in production responses
- ✅ WWW-Authenticate header in 401 responses

**Environment Variables**:
- ✅ BETTER_AUTH_SECRET stored in .env (not committed)
- ✅ DATABASE_URL stored in .env (not committed)
- ✅ .env.example provided as template

**HTTPS**:
- ⚠️ Development: HTTP acceptable on localhost
- ⚠️ Production: HTTPS required (document in deployment guide)

**Acceptance Criteria**:
- ✅ All security checklist items verified
- ✅ No hardcoded secrets in code
- ✅ User isolation tested with multiple users
- ✅ Error responses don't leak sensitive info

---

### Task 5.4: Performance Verification

**Objective**: Verify database indexes are used correctly

**Actions**:
1. Connect to Neon PostgreSQL and run EXPLAIN ANALYZE:

```sql
-- Query 1: List all tasks for user (uses idx_tasks_user_id)
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test_user_123'
ORDER BY created_at DESC;

-- Query 2: List pending tasks for user (uses idx_tasks_user_completed)
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test_user_123' AND completed = false
ORDER BY created_at DESC;

-- Query 3: Get single task (uses primary key)
EXPLAIN ANALYZE
SELECT * FROM tasks WHERE id = 42;
```

2. Verify index usage in query plans:
   - Look for "Index Scan" (not "Seq Scan")
   - Verify idx_tasks_user_id used for user filtering
   - Verify idx_tasks_user_completed used for filtered queries
   - Verify primary key used for single task lookup

**Performance Checklist**:
- ✅ Indexes created during migration
- ✅ Queries use indexes (no full table scans)
- ✅ Connection pooling configured (pool_size=5, max_overflow=10)
- ✅ Connections recycled after 1 hour

**Acceptance Criteria**:
- ✅ All queries use appropriate indexes
- ✅ No sequential scans on large tables
- ✅ Connection pooling working correctly

---

### Task 5.5: Documentation and Cleanup

**Objective**: Document backend setup and prepare for deployment

**Actions**:
1. Create `backend/README.md`:
```markdown
# Todo Backend - FastAPI

FastAPI backend for Todo application with JWT authentication.

## Quick Start

### Prerequisites
- Python 3.10+
- UV package manager
- Neon PostgreSQL database
- Better Auth secret (shared with frontend)

### Installation

1. Install dependencies:
\`\`\`bash
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
\`\`\`

2. Configure environment:
\`\`\`bash
cp .env.example .env
# Edit .env with your values
\`\`\`

3. Run migrations:
\`\`\`bash
alembic upgrade head
\`\`\`

4. Start server:
\`\`\`bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

5. Open API docs: http://localhost:8000/docs

## API Endpoints

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

- `POST /api/tasks` - Create task
- `GET /api/tasks` - List tasks (with filtering/sorting)
- `GET /api/tasks/{id}` - Get single task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle completion

## Testing

\`\`\`bash
pytest
\`\`\`

## Environment Variables

See `.env.example` for all required variables.

Required:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Shared secret with frontend

## Security

- All endpoints require JWT authentication
- User isolation enforced at database query level
- Ownership verified before read/update/delete operations
- HTTPS required in production
\`\`\`

2. Update root `README.md` to document backend setup

3. Verify `.gitignore` includes:
```
backend/.env
backend/.venv
backend/__pycache__
backend/uv.lock
```

**Acceptance Criteria**:
- ✅ Backend README.md created with setup instructions
- ✅ Root README.md updated
- ✅ .gitignore configured
- ✅ No secrets committed to git

---

**Phase 5 Summary**:
- ✅ Integration tests created and passing
- ✅ Frontend integration verified
- ✅ Security requirements verified
- ✅ Performance verified (indexes working)
- ✅ Documentation complete

**Phase 5 Deliverable**: Production-ready backend with complete test coverage and documentation

---

## Final Verification Checklist

### Functionality
- ✅ All 6 CRUD endpoints implemented and working
- ✅ Filtering by status (all/pending/completed)
- ✅ Sorting by created/title/updated
- ✅ JWT authentication on all routes
- ✅ User isolation enforced

### Security
- ✅ JWT signature verification
- ✅ Token expiration validation
- ✅ Ownership verification before operations
- ✅ No user_id from request body
- ✅ Generic error messages
- ✅ Secrets in environment variables

### Performance
- ✅ Database indexes created
- ✅ Connection pooling configured
- ✅ Queries use indexes (verified with EXPLAIN)

### Integration
- ✅ CORS configured for frontend
- ✅ Frontend can make authenticated requests
- ✅ All operations work end-to-end
- ✅ Better Auth JWT tokens verified

### Testing
- ✅ Authentication tests pass
- ✅ Integration tests pass
- ✅ User isolation tests pass
- ✅ Error cases tested

### Documentation
- ✅ Backend README.md complete
- ✅ API endpoints documented
- ✅ Environment variables documented
- ✅ Setup instructions clear

---

## Complexity Tracking

### Justified Complexity

**1. FastAPI Dependency Injection**
- **Complexity**: Using `Depends()` for authentication and database sessions
- **Justification**: Reduces code duplication, enforces auth automatically, improves testability
- **Alternatives Considered**: Manual JWT extraction per route (rejected: repetitive, error-prone)

**2. SQLModel (SQLAlchemy + Pydantic)**
- **Complexity**: Hybrid ORM/validation library
- **Justification**: Type safety, integrates with FastAPI, reduces boilerplate
- **Alternatives Considered**: Raw SQLAlchemy (rejected: more verbose), separate ORM and validation (rejected: duplicated models)

**3. Alembic Migrations**
- **Complexity**: Database migration tool with revision files
- **Justification**: Production requirement, enables safe schema changes, version control for database
- **Alternatives Considered**: SQLModel.metadata.create_all() (rejected: no migration history, not production-safe)

### No Premature Optimization

- ✅ No caching added (wait for performance issues)
- ✅ No background tasks (CRUD operations are synchronous)
- ✅ No pagination (user isolation limits data size, add if needed)
- ✅ No rate limiting (add if abuse detected)

---

## Implementation Tasks Summary

**Total Tasks**: 18 tasks across 5 phases

**Phase 1 - Foundation** (6 tasks):
1. Initialize directory structure
2. Configure UV and install dependencies
3. Create environment configuration
4. Set up database connection
5. Create main FastAPI application
6. Verify foundation setup

**Phase 2 - Database** (3 tasks):
1. Create SQLModel Task model
2. Create Pydantic schemas
3. Initialize Alembic migrations

**Phase 3 - Authentication** (2 tasks):
1. Implement JWT verification
2. Test authentication dependencies

**Phase 4 - CRUD Endpoints** (7 tasks):
1. Implement create task endpoint
2. Implement list tasks endpoint
3. Implement get single task endpoint
4. Implement update task endpoint
5. Implement delete task endpoint
6. Implement toggle completion endpoint
7. Register task router in main app

**Phase 5 - Testing** (5 tasks):
1. Create integration tests
2. Test frontend integration
3. Security verification
4. Performance verification
5. Documentation and cleanup

---

## Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to create detailed task list from this plan
2. **Implement**: Execute tasks using specialized agents (`fastapi-backend-engineer`)
3. **Test**: Verify integration with frontend at each milestone
4. **Deploy**: Prepare for production deployment (separate deployment plan)

---

## Architectural Decision Record Suggestion

📋 **Architectural decision detected**: JWT verification approach with FastAPI dependency injection

Document this decision? Run `/sp.adr "JWT Authentication with FastAPI Dependencies"`

**Key Decision Points**:
- Stateless JWT vs session-based auth
- User isolation at query level vs application level
- FastAPI dependencies vs manual auth per route
- SQLModel vs raw SQLAlchemy

---

**Plan Status**: ✅ COMPLETE
**Constitution Check**: ✅ PASSED
**Ready for**: `/sp.tasks` to generate implementation tasks

**Created**: 2026-01-05
**Last Updated**: 2026-01-05
**Branch**: `003-fastapi-backend`
