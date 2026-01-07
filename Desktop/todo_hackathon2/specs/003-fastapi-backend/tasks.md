# Implementation Tasks: FastAPI Backend

**Feature**: FastAPI Backend with JWT Authentication and Task CRUD
**Created**: 2026-01-05
**Branch**: `003-fastapi-backend`
**Status**: Ready for Implementation

## Overview

This document breaks down the FastAPI backend implementation into small, atomic, sequential tasks. Each task is designed to be completable in a single Claude Code prompt.

**Total Tasks**: 25 tasks across 7 phases
**Implementation Order**: Setup → Foundation → Database → Authentication → CRUD Operations → Testing → Integration

---

## Phase 1: Project Setup

**Goal**: Initialize backend project structure and dependencies

**Phase Outcome**: Working backend directory with all dependencies installed

### Tasks

- [x] T001 Create backend directory structure
  - **Action**: Create all required directories for the FastAPI backend
  - **Directories to create**:
    - `backend/app/routers/`
    - `backend/alembic/versions/`
    - `backend/tests/`
  - **Files to create** (empty `__init__.py` files):
    - `backend/app/__init__.py`
    - `backend/app/routers/__init__.py`
    - `backend/tests/__init__.py`
  - **Acceptance Criteria**:
    - All directories exist
    - All `__init__.py` files created
    - Directory structure matches plan.md specification

- [x] T002 Create pyproject.toml and install dependencies with UV
  - **Action**: Set up UV package manager configuration and install all dependencies
  - **File to create**: `backend/pyproject.toml`
  - **Dependencies**:
    - `fastapi>=0.100.0`
    - `uvicorn[standard]>=0.23.0`
    - `sqlmodel>=0.0.14`
    - `pydantic>=2.0.0`
    - `pydantic-settings>=2.0.0`
    - `psycopg2-binary>=2.9.0`
    - `pyjwt>=2.8.0`
    - `python-dotenv>=1.0.0`
    - `alembic>=1.12.0`
    - Dev dependencies: `pytest>=7.4.0`, `pytest-asyncio>=0.21.0`, `httpx>=0.24.0`
  - **Commands to run**:
    ```bash
    cd backend
    uv venv
    uv pip install -e ".[dev]"
    ```
  - **Acceptance Criteria**:
    - `pyproject.toml` created with all dependencies
    - Virtual environment created (`.venv/`)
    - All packages installed successfully
    - `uv.lock` file generated

- [x] T003 Create .env.example and .gitignore
  - **Action**: Set up environment variable template and git ignore rules
  - **File to create**: `backend/.env.example`
  - **Environment variables to include**:
    - `DATABASE_URL` - Neon PostgreSQL connection string
    - `BETTER_AUTH_SECRET` - Shared secret with frontend
    - `JWT_ALGORITHM=HS256`
    - `JWT_AUDIENCE=http://localhost:3000`
    - `JWT_ISSUER=better-auth`
    - `CORS_ORIGINS=http://localhost:3000`
    - `HOST=0.0.0.0`
    - `PORT=8000`
    - `RELOAD=true`
  - **Update**: `backend/.gitignore` (or create if doesn't exist)
  - **Add to .gitignore**:
    - `.env`
    - `.venv/`
    - `__pycache__/`
    - `*.pyc`
    - `uv.lock`
  - **Acceptance Criteria**:
    - `.env.example` contains all required variables with descriptions
    - `.gitignore` configured to prevent committing secrets
    - Template can be copied to `.env` for local development

---

## Phase 2: Foundation Layer

**Goal**: Set up core infrastructure (config, database connection, FastAPI app)

**Phase Outcome**: FastAPI server starts successfully with health checks

### Tasks

- [x] T004 Implement application configuration with Pydantic Settings
  - **Action**: Create type-safe configuration management using pydantic-settings
  - **File to create**: `backend/app/config.py`
  - **Reference**: plan.md - Task 1.3 (Environment Configuration)
  - **Implementation**:
    - Create `Settings` class inheriting from `BaseSettings`
    - Define all environment variables with types and defaults
    - Configure `model_config` with `env_file=".env"`
    - Create global `settings` instance
  - **Fields to include**:
    - `database_url: str` (required)
    - `better_auth_secret: str` (required)
    - `jwt_algorithm: str = "HS256"`
    - `jwt_audience: str = "http://localhost:3000"`
    - `jwt_issuer: str = "better-auth"`
    - `cors_origins: List[str] = ["http://localhost:3000"]`
    - `host: str = "0.0.0.0"`
    - `port: int = 8000`
    - `reload: bool = True`
  - **Acceptance Criteria**:
    - Settings class loads from `.env` file
    - All environment variables typed correctly
    - Global `settings` instance can be imported
    - Default values provided for optional settings

- [x] T005 Set up database connection and session management
  - **Action**: Configure SQLModel engine with connection pooling for Neon PostgreSQL
  - **File to create**: `backend/app/database.py`
  - **Reference**: plan.md - Task 1.4, schema.md (Database connection configuration)
  - **Implementation**:
    - Import `create_engine`, `Session`, `SQLModel` from sqlmodel
    - Import `settings` from `app.config`
    - Create engine with connection pooling parameters:
      - `pool_size=5`
      - `max_overflow=10`
      - `pool_pre_ping=True`
      - `pool_recycle=3600`
      - `connect_args={"sslmode": "require"}`
    - Implement `get_session()` generator function for FastAPI dependency injection
    - Implement `create_db_and_tables()` function for table creation
  - **Acceptance Criteria**:
    - Engine configured with connection pooling
    - SSL enabled for Neon PostgreSQL
    - `get_session()` dependency ready for FastAPI routes
    - `create_db_and_tables()` function available for startup

- [x] T006 Create main FastAPI application with CORS middleware
  - **Action**: Set up FastAPI app with CORS configuration and health check endpoints
  - **File to create**: `backend/app/main.py`
  - **Reference**: plan.md - Task 1.5
  - **Implementation**:
    - Create FastAPI app instance with title, description, version
    - Add CORS middleware with settings from config:
      - `allow_origins=settings.cors_origins` (["http://localhost:3000"])
      - `allow_credentials=True`
      - `allow_methods=["*"]`
      - `allow_headers=["*"]`
    - Add startup event handler to create database tables
    - Implement root endpoint `/` returning API info
    - Implement health check endpoint `/health` returning status
  - **Acceptance Criteria**:
    - FastAPI app created with OpenAPI docs at `/docs`
    - CORS configured for frontend origin (localhost:3000)
    - Health check endpoints accessible
    - Database tables created on startup
    - Server can be started with `uvicorn app.main:app --reload`

- [ ] T007 Verify foundation setup by starting server
  - **Action**: Test that the FastAPI server starts and health checks work
  - **Commands to run**:
    ```bash
    cd backend
    # Create .env file from .env.example (manual step - document in output)
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
  - **Tests to perform**:
    - Server starts without errors
    - Visit `http://localhost:8000/health` - should return `{"status": "healthy"}`
    - Visit `http://localhost:8000/docs` - OpenAPI documentation loads
    - Visit `http://localhost:8000/` - root endpoint returns API info
  - **Acceptance Criteria**:
    - Server starts successfully on port 8000
    - All health check endpoints respond correctly
    - OpenAPI documentation accessible
    - No import errors or dependency issues
    - **Note**: Server should be stopped after verification before proceeding to next phase

---

## Phase 3: Database Models

**Goal**: Implement SQLModel Task class and Pydantic schemas

**Phase Outcome**: Task model and validation schemas ready for CRUD operations

**Reference**: schema.md, rest-endpoints.md (Pydantic models section)

### Tasks

- [x] T008 Create SQLModel Task class
  - **Action**: Implement Task database model with all fields, validations, and indexes
  - **File to create**: `backend/app/models.py`
  - **Reference**: schema.md - Task model specification
  - **Implementation**:
    - Import `SQLModel`, `Field` from sqlmodel, `datetime`, `Optional`
    - Create `Task` class inheriting from `SQLModel` with `table=True`
    - Set `__tablename__ = "tasks"`
    - Define fields:
      - `id: Optional[int]` (primary key, auto-generated)
      - `user_id: str` (foreign key to users.id, indexed, NOT NULL)
      - `title: str` (min_length=1, max_length=200)
      - `description: Optional[str]` (max_length=1000)
      - `completed: bool` (default=False, indexed)
      - `created_at: datetime` (default_factory=datetime.utcnow)
      - `updated_at: datetime` (default_factory=datetime.utcnow)
    - Add Config class with composite index on `(user_id, completed)`
  - **Acceptance Criteria**:
    - Task model inherits from SQLModel with table=True
    - All fields have proper types and constraints
    - Foreign key to users table defined
    - Indexes on user_id, completed, and composite
    - Default values for completed and timestamps

- [x] T009 Create Pydantic request and response schemas
  - **Action**: Define Pydantic models for API request/response validation
  - **File to create**: `backend/app/schemas.py`
  - **Reference**: rest-endpoints.md - Pydantic Models section, task-crud.md - Implementation Details
  - **Request Schemas to create**:
    - `TaskCreate`: title (required, 1-200), description (optional, max 1000)
    - `TaskUpdate`: title (required, 1-200), description (optional, max 1000)
  - **Response Schemas to create**:
    - `TaskResponse`: id, user_id, title, description, is_completed (alias for "completed"), created_at, updated_at
      - Configure `model_config` with `from_attributes=True` and `populate_by_name=True`
    - `TaskListResponse`: tasks (list), total (int), status_filter (str), sort_by (str)
    - `DeleteResponse`: message (str), deleted_task_id (int)
  - **Acceptance Criteria**:
    - All request schemas have Field() validation
    - TaskResponse uses `is_completed` alias for frontend compatibility
    - ORM mode enabled on TaskResponse
    - All schemas match rest-endpoints.md specification

- [ ] T010 Initialize Alembic and create initial migration
  - **Action**: Set up Alembic for database migrations and create tasks table migration
  - **Files to modify**: `backend/alembic/env.py`
  - **Commands to run**:
    ```bash
    cd backend
    alembic init alembic  # If not already initialized
    # Edit alembic/env.py to use app.config.settings.database_url
    # Import Task model in env.py
    alembic revision --autogenerate -m "Initial schema: tasks table"
    alembic upgrade head
    ```
  - **Reference**: plan.md - Task 2.3
  - **Implementation in env.py**:
    - Import `settings` from `app.config`
    - Import `Task` from `app.models`
    - Import `SQLModel` from `sqlmodel`
    - Set `config.set_main_option("sqlalchemy.url", settings.database_url)`
    - Set `target_metadata = SQLModel.metadata`
  - **Acceptance Criteria**:
    - Alembic initialized in `backend/alembic/`
    - `env.py` configured with SQLModel metadata
    - Initial migration created in `alembic/versions/`
    - Migration applied successfully to Neon database
    - Tasks table exists with all columns and indexes
    - Can verify with: `alembic current` shows migration applied

---

## Phase 4: JWT Authentication

**Goal**: Implement JWT token verification and FastAPI authentication dependencies

**Phase Outcome**: All routes can require authentication using `Depends(get_current_user_id)`

**Reference**: authentication.md

### Tasks

- [x] T011 Implement JWT verification functions and dependencies
  - **Action**: Create JWT token verification with PyJWT and FastAPI dependencies
  - **File to create**: `backend/app/auth.py`
  - **Reference**: authentication.md - Complete implementation, plan.md - Task 3.1
  - **Implementation**:
    - Import `jwt` from `pyjwt`, `HTTPBearer`, `HTTPAuthorizationCredentials` from fastapi.security
    - Import `settings` from `app.config`
    - Create `HTTPBearer` instance: `bearer_scheme = HTTPBearer()`
    - Create `TokenData` Pydantic model with `user_id: str` and `email: str`
    - Implement `verify_jwt_token(token: str) -> TokenData`:
      - Use `jwt.decode()` with signature verification, expiration, audience, issuer checks
      - Extract `user_id` from `sub` claim
      - Raise HTTPException(401) for invalid/expired/missing claims
    - Implement async `get_current_user()` dependency:
      - Extract token from Bearer credentials
      - Call `verify_jwt_token()`
      - Return `TokenData`
    - Implement async `get_current_user_id()` convenience dependency:
      - Depend on `get_current_user()`
      - Return just the `user_id` string
  - **Security Checks**:
    - Verify signature using `settings.better_auth_secret`
    - Verify expiration (exp claim)
    - Verify audience (aud claim) = "http://localhost:3000"
    - Verify issuer (iss claim) = "better-auth"
    - Raise 401 with WWW-Authenticate header for all failures
  - **Acceptance Criteria**:
    - `verify_jwt_token()` validates all JWT claims
    - `get_current_user()` FastAPI dependency extracts user from token
    - `get_current_user_id()` convenience dependency returns user_id string
    - HTTPBearer scheme configured for Authorization header
    - All error cases raise HTTPException(401) with proper detail messages

- [ ] T012 [P] Create authentication tests (optional - can implement later)
  - **Action**: Write pytest tests for JWT verification
  - **File to create**: `backend/tests/test_auth.py`
  - **Reference**: plan.md - Task 3.2
  - **Tests to implement**:
    - `test_verify_valid_token()` - Valid JWT accepted
    - `test_verify_expired_token()` - Expired token rejected with 401
    - `test_verify_invalid_signature()` - Wrong secret rejected with 401
    - `test_verify_missing_user_id()` - Missing 'sub' claim rejected with 401
  - **Helper function**: `create_test_token(user_id, expired=False)` to generate test JWTs
  - **Acceptance Criteria**:
    - All authentication tests pass
    - Valid tokens accepted
    - Invalid/expired tokens rejected
    - Error messages user-friendly
  - **Note**: This task can be done in parallel with T013-T019 or after full implementation

---

## Phase 5: Task CRUD Endpoints

**Goal**: Implement all 6 REST API endpoints for task operations

**Phase Outcome**: Complete REST API with JWT-protected task CRUD endpoints

**Reference**: rest-endpoints.md, task-crud.md

### User Story 1: Create Task (Priority P1)

- [x] T013 [US1] Implement POST /api/tasks endpoint (Create Task)
  - **Action**: Create task creation endpoint with JWT authentication
  - **File to create**: `backend/app/routers/tasks.py` (new file)
  - **Reference**: task-crud.md - US-1 (Create Task Operation), rest-endpoints.md - Create endpoint
  - **Implementation**:
    - Import all required dependencies (FastAPI, SQLModel, auth, models, schemas)
    - Create router: `router = APIRouter(prefix="/api", tags=["tasks"])`
    - Implement `@router.post("/tasks", status_code=201)` endpoint:
      - Parameters: `task_data: TaskCreate`, `current_user_id: str = Depends(get_current_user_id)`, `session: Session = Depends(get_session)`
      - Create new `Task` instance with `user_id=current_user_id` (from JWT)
      - Set `completed=False`, `created_at=datetime.utcnow()`, `updated_at=datetime.utcnow()`
      - Add to session, commit, refresh
      - Return `TaskResponse.model_validate(new_task)`
  - **Security**: user_id ALWAYS from JWT, never from request body
  - **Acceptance Criteria**:
    - POST /api/tasks creates task
    - user_id set from JWT token
    - Returns 201 Created with task object
    - Returns 401 for missing/invalid token
    - Returns 400 for validation errors (title too long, etc.)
    - Title validated (1-200 chars)
    - Description validated (max 1000 chars)

### User Story 2: List My Tasks (Priority P1)

- [x] T014 [US2] Implement GET /api/tasks endpoint (List Tasks)
  - **Action**: Create task list endpoint with filtering and sorting
  - **File to modify**: `backend/app/routers/tasks.py`
  - **Reference**: task-crud.md - US-2 (List Tasks Operation), rest-endpoints.md - List endpoint
  - **Implementation**:
    - Import `Literal` from typing, `Query` from fastapi
    - Implement `@router.get("/tasks")` endpoint:
      - Parameters:
        - `status_filter: Literal["all", "pending", "completed"] = Query(default="all", alias="status")`
        - `sort: Literal["created", "title", "updated"] = Query(default="created")`
        - `current_user_id: str = Depends(get_current_user_id)`
        - `session: Session = Depends(get_session)`
      - Build query: `select(Task).where(Task.user_id == current_user_id)`
      - Apply status filter (if pending: `.where(completed=False)`, if completed: `.where(completed=True)`)
      - Apply sorting (created: `order_by(created_at.desc())`, title: `order_by(title.asc())`, updated: `order_by(updated_at.desc())`)
      - Execute query and return `TaskListResponse`
  - **Security**: Queries ALWAYS filter by current_user_id from JWT
  - **Acceptance Criteria**:
    - GET /api/tasks returns only authenticated user's tasks
    - status=all returns all tasks
    - status=pending returns incomplete tasks (completed=false)
    - status=completed returns complete tasks (completed=true)
    - sort=created orders by created_at descending (newest first)
    - sort=title orders alphabetically
    - sort=updated orders by updated_at descending
    - Returns empty array when user has no tasks
    - Returns 401 for missing/invalid token

### User Story 3: View Single Task (Priority P1)

- [x] T015 [US3] Implement GET /api/tasks/{id} endpoint (Get Single Task)
  - **Action**: Create single task retrieval endpoint with ownership verification
  - **File to modify**: `backend/app/routers/tasks.py`
  - **Reference**: task-crud.md - US-3 (Get Single Task Operation), rest-endpoints.md - Get single endpoint
  - **Implementation**:
    - Implement `@router.get("/tasks/{task_id}")` endpoint:
      - Parameters: `task_id: int`, `current_user_id: str = Depends(get_current_user_id)`, `session: Session = Depends(get_session)`
      - Query task: `task = session.get(Task, task_id)`
      - If not found: raise HTTPException(404, "Task not found")
      - **Ownership verification**: If `task.user_id != current_user_id`: raise HTTPException(403, "Not authorized to access this task")
      - Return `TaskResponse.model_validate(task)`
  - **Security**: Ownership verified BEFORE returning data
  - **Acceptance Criteria**:
    - GET /api/tasks/{id} returns task when owned by user
    - Returns 404 when task doesn't exist
    - Returns 403 when task owned by different user
    - Returns 401 for missing/invalid token
    - Ownership checked before returning data

### User Story 4: Update Task (Priority P2)

- [x] T016 [US4] Implement PUT /api/tasks/{id} endpoint (Update Task)
  - **Action**: Create task update endpoint with validation and ownership verification
  - **File to modify**: `backend/app/routers/tasks.py`
  - **Reference**: task-crud.md - US-4 (Update Task Operation), rest-endpoints.md - Update endpoint
  - **Implementation**:
    - Implement `@router.put("/tasks/{task_id}")` endpoint:
      - Parameters: `task_id: int`, `task_data: TaskUpdate`, `current_user_id: str = Depends(get_current_user_id)`, `session: Session = Depends(get_session)`
      - Query task: `task = session.get(Task, task_id)`
      - If not found: raise HTTPException(404, "Task not found")
      - **Ownership verification**: If `task.user_id != current_user_id`: raise HTTPException(403, "Not authorized to modify this task")
      - Update fields: `task.title = task_data.title`, `task.description = task_data.description`
      - Refresh timestamp: `task.updated_at = datetime.utcnow()`
      - Commit and refresh
      - Return `TaskResponse.model_validate(task)`
  - **Security**: Ownership verified BEFORE updating
  - **Immutable fields**: user_id, created_at, completed (use toggle endpoint for completed)
  - **Acceptance Criteria**:
    - PUT /api/tasks/{id} updates task when owned by user
    - Updates title and description
    - updated_at timestamp refreshed
    - created_at unchanged
    - completed status NOT modified
    - Returns 404 when task doesn't exist
    - Returns 403 when task owned by different user
    - Returns 401 for missing/invalid token
    - Returns 400 for validation errors

### User Story 5: Delete Task (Priority P2)

- [x] T017 [US5] Implement DELETE /api/tasks/{id} endpoint (Delete Task)
  - **Action**: Create task deletion endpoint with ownership verification
  - **File to modify**: `backend/app/routers/tasks.py`
  - **Reference**: task-crud.md - US-5 (Delete Task Operation), rest-endpoints.md - Delete endpoint
  - **Implementation**:
    - Implement `@router.delete("/tasks/{task_id}")` endpoint:
      - Parameters: `task_id: int`, `current_user_id: str = Depends(get_current_user_id)`, `session: Session = Depends(get_session)`
      - Query task: `task = session.get(Task, task_id)`
      - If not found: raise HTTPException(404, "Task not found")
      - **Ownership verification**: If `task.user_id != current_user_id`: raise HTTPException(403, "Not authorized to delete this task")
      - Delete: `session.delete(task)`, `session.commit()`
      - Return `DeleteResponse(message="Task deleted successfully", deleted_task_id=task_id)`
  - **Security**: Ownership verified BEFORE deleting
  - **Acceptance Criteria**:
    - DELETE /api/tasks/{id} deletes task when owned by user
    - Returns success message with deleted task ID
    - Task permanently removed from database
    - Subsequent GET returns 404
    - Returns 404 when task doesn't exist
    - Returns 403 when task owned by different user
    - Returns 401 for missing/invalid token

### User Story 6: Toggle Completion (Priority P1)

- [x] T018 [US6] Implement PATCH /api/tasks/{id}/complete endpoint (Toggle Completion)
  - **Action**: Create completion toggle endpoint (idempotent)
  - **File to modify**: `backend/app/routers/tasks.py`
  - **Reference**: task-crud.md - US-6 (Toggle Task Completion), rest-endpoints.md - Toggle endpoint
  - **Implementation**:
    - Implement `@router.patch("/tasks/{task_id}/complete")` endpoint:
      - Parameters: `task_id: int`, `current_user_id: str = Depends(get_current_user_id)`, `session: Session = Depends(get_session)`
      - Query task: `task = session.get(Task, task_id)`
      - If not found: raise HTTPException(404, "Task not found")
      - **Ownership verification**: If `task.user_id != current_user_id`: raise HTTPException(403, "Not authorized to modify this task")
      - Toggle: `task.completed = not task.completed`
      - Refresh timestamp: `task.updated_at = datetime.utcnow()`
      - Commit and refresh
      - Return `TaskResponse.model_validate(task)`
  - **Behavior**: Idempotent - can toggle multiple times (false ↔ true)
  - **Acceptance Criteria**:
    - PATCH /api/tasks/{id}/complete toggles status
    - false → true when currently incomplete
    - true → false when currently complete
    - updated_at timestamp refreshed
    - Title and description unchanged
    - Idempotent (can call multiple times)
    - Returns 404 when task doesn't exist
    - Returns 403 when task owned by different user
    - Returns 401 for missing/invalid token

### Register Router

- [x] T019 Register task router in main FastAPI application
  - **Action**: Include the tasks router in the main app to expose all endpoints
  - **File to modify**: `backend/app/main.py`
  - **Implementation**:
    - Add import: `from app.routers import tasks`
    - After CORS middleware setup, add: `app.include_router(tasks.router)`
  - **Acceptance Criteria**:
    - Task router registered with `/api` prefix
    - All 6 endpoints accessible under `/api/tasks`
    - OpenAPI docs at `/docs` show all task endpoints
    - CORS applies to all task routes
    - Can test with: `curl http://localhost:8000/docs` should show all endpoints

---

## Phase 6: Integration Testing

**Goal**: Create comprehensive tests and verify all functionality

**Phase Outcome**: Test suite passes, all endpoints verified

**Reference**: plan.md - Phase 5

### Tasks

- [x] T020 [P] Create pytest configuration and test fixtures
  - **Action**: Set up test infrastructure with in-memory database and JWT token generation
  - **File to create**: `backend/tests/conftest.py`
  - **Reference**: plan.md - Task 5.1 (Integration Tests)
  - **Implementation**:
    - Create test database fixture using in-memory SQLite
    - Create test client fixture with dependency overrides
    - Create `create_test_token(user_id)` helper function
    - Create `auth_headers` fixture returning Authorization headers with valid JWT
    - Create `auth_headers_user2` fixture for second test user
  - **Fixtures**:
    - `session` - In-memory SQLite database session
    - `client` - TestClient with test database
    - `auth_headers` - Headers with JWT for test_user_123
    - `auth_headers_user2` - Headers with JWT for test_user_456
  - **Acceptance Criteria**:
    - Test fixtures available for all tests
    - In-memory database configured
    - JWT token generation working
    - Multiple test users supported

- [x] T021 [P] Write integration tests for all CRUD operations
  - **Action**: Create comprehensive tests for task CRUD lifecycle
  - **File to create**: `backend/tests/test_tasks.py`
  - **Reference**: plan.md - Task 5.1 (Integration Tests examples)
  - **Tests to implement**:
    - `test_create_task_success()` - Create with valid data returns 201
    - `test_create_task_without_auth()` - Create without token returns 401
    - `test_list_tasks_user_isolation()` - Users only see their own tasks
    - `test_get_task_ownership_violation()` - User 2 cannot access User 1's task (403)
    - `test_complete_task_lifecycle()` - Full CRUD workflow (create → read → update → toggle → delete)
    - `test_task_filtering()` - Filter by status (all/pending/completed)
    - `test_update_task_success()` - Update title and description
    - `test_delete_task_success()` - Delete and verify 404 on subsequent GET
    - `test_toggle_completion_idempotent()` - Toggle multiple times
  - **Acceptance Criteria**:
    - All integration tests pass
    - User isolation verified (User A cannot access User B's tasks)
    - Complete CRUD lifecycle tested
    - Error cases tested (401, 403, 404)
    - Filtering and sorting tested

- [ ] T022 Run full test suite and verify all tests pass
  - **Action**: Execute pytest and ensure all tests pass
  - **Commands to run**:
    ```bash
    cd backend
    pytest -v
    ```
  - **Expected Results**:
    - All authentication tests pass (if T012 completed)
    - All integration tests pass
    - No test failures or errors
    - Test coverage includes all user stories
  - **Acceptance Criteria**:
    - `pytest` runs without errors
    - All tests pass (green)
    - No warnings about missing dependencies
    - Test report shows coverage of all endpoints

---

## Phase 7: Frontend Integration & Documentation

**Goal**: Verify backend works with Next.js frontend and document setup

**Phase Outcome**: Backend fully integrated with frontend, documentation complete

**Reference**: plan.md - Phase 5, Tasks 5.2-5.5

### Tasks

- [ ] T023 Verify backend integration with Next.js frontend
  - **Action**: Test end-to-end integration between backend and frontend
  - **Prerequisites**: Frontend server must be running on localhost:3000
  - **Steps to perform**:
    1. Ensure `.env` file exists with correct values:
       - `DATABASE_URL` - Your Neon PostgreSQL URL
       - `BETTER_AUTH_SECRET` - Same secret as frontend
       - `CORS_ORIGINS=http://localhost:3000`
    2. Start backend server:
       ```bash
       cd backend
       uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
       ```
    3. Start frontend server:
       ```bash
       cd frontend
       npm run dev
       ```
    4. Test integration:
       - Open `http://localhost:3000`
       - Log in with Better Auth
       - Create a task → Verify POST to `http://localhost:8000/api/tasks` succeeds
       - View tasks → Verify GET from `http://localhost:8000/api/tasks` returns data
       - Toggle completion → Verify PATCH works
       - Update task → Verify PUT works
       - Delete task → Verify DELETE works
    5. Check browser console for CORS errors (should be none)
    6. Verify Authorization header sent with all requests
  - **Acceptance Criteria**:
    - Frontend successfully communicates with backend
    - No CORS errors in browser console
    - All CRUD operations work end-to-end
    - JWT token sent in Authorization header
    - Backend verifies JWT signature
    - User can only see their own tasks
    - Create, list, update, delete, toggle all functional

- [ ] T024 Perform security verification checklist
  - **Action**: Verify all security requirements are met
  - **Security Checklist**:
    - **Authentication**:
      - ✅ All endpoints require valid JWT token
      - ✅ JWT signature verified using BETTER_AUTH_SECRET
      - ✅ Expired tokens rejected with 401
      - ✅ Invalid tokens rejected with 401
      - ✅ Missing tokens rejected with 401
    - **User Isolation**:
      - ✅ All queries filter by authenticated user_id from JWT
      - ✅ user_id never accepted from request body or query params
      - ✅ Ownership verified before GET/PUT/DELETE/PATCH operations
      - ✅ Users cannot access other users' tasks (403 returned)
    - **Error Handling**:
      - ✅ Generic error messages (no sensitive info leaked)
      - ✅ Proper HTTP status codes (200, 201, 400, 401, 403, 404)
      - ✅ No stack traces in production responses
      - ✅ WWW-Authenticate header in 401 responses
    - **Environment Variables**:
      - ✅ BETTER_AUTH_SECRET stored in .env (not committed)
      - ✅ DATABASE_URL stored in .env (not committed)
      - ✅ .env.example provided as template
  - **Acceptance Criteria**:
    - All security checklist items verified
    - No hardcoded secrets in code
    - User isolation tested with multiple users
    - Error responses don't leak sensitive info

- [x] T025 Create backend README.md and finalize documentation
  - **Action**: Document backend setup, API endpoints, and deployment notes
  - **File to create**: `backend/README.md`
  - **Reference**: plan.md - Task 5.5 (Documentation)
  - **Sections to include**:
    - **Overview**: Brief description of FastAPI backend
    - **Prerequisites**: Python 3.10+, UV, Neon PostgreSQL, Better Auth secret
    - **Installation**: Step-by-step setup instructions
      - Install dependencies with UV
      - Configure .env file
      - Run migrations
      - Start server
    - **API Endpoints**: List all 6 endpoints with brief description
    - **Environment Variables**: Document all required and optional variables
    - **Testing**: How to run tests with pytest
    - **Security**: Authentication requirements, user isolation notes
    - **CORS**: Frontend origin configuration
    - **Development**: How to start dev server
  - **Also update**: Root `README.md` with backend setup instructions
  - **Verify**: `.gitignore` includes `.env`, `.venv/`, `__pycache__/`
  - **Acceptance Criteria**:
    - Backend README.md complete with all setup instructions
    - Root README.md updated
    - .gitignore configured properly
    - No secrets committed to git
    - Documentation clear for new developers

---

## Task Dependencies

### Sequential Dependencies (Must Complete in Order)

**Phase 1 → Phase 2**:
- T001, T002, T003 must complete before T004, T005, T006

**Phase 2 → Phase 3**:
- T004 (config.py) required by T005 (database.py)
- T005 (database.py) required by T006 (main.py)
- T006 (main.py) must complete before T008 (models)

**Phase 3 → Phase 4**:
- T008 (models.py) required by T010 (Alembic migration)
- T009 (schemas.py) required by T013-T018 (endpoints)

**Phase 4 → Phase 5**:
- T011 (auth.py) required by T013-T018 (all endpoints use authentication)

**Phase 5 Tasks**:
- T013-T018 can be implemented in any order (all depend on T011)
- T019 must be last (registers all routes)

**Phase 6**:
- T020-T022 depend on all Phase 5 tasks completing

**Phase 7**:
- T023-T025 depend on all previous phases completing

### Parallel Opportunities

**Can be done in parallel**:
- T012 (auth tests) can be done anytime after T011 completes
- T020-T021 (test infrastructure and tests) can be written in parallel
- T013-T018 (CRUD endpoints) are independent and can be done in parallel if desired

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Essential for MVP** (Complete first):
- Phase 1: All setup tasks (T001-T003)
- Phase 2: All foundation tasks (T004-T007)
- Phase 3: Database models (T008-T010)
- Phase 4: Authentication (T011)
- Phase 5: Core CRUD (T013, T014, T015, T018, T019)
  - Create task (T013)
  - List tasks (T014)
  - Get single task (T015)
  - Toggle completion (T018)
  - Register router (T019)

**MVP Deliverable**: Working API with create, list, view, and toggle operations

### Incremental Delivery

**After MVP, add**:
- Update task (T016)
- Delete task (T017)
- Tests (T012, T020-T022)
- Frontend integration (T023)
- Security verification (T024)
- Documentation (T025)

### User Story Priority Order

1. **Priority P1** (MVP - Must Have):
   - US-1: Create Task (T013)
   - US-2: List My Tasks (T014)
   - US-3: View Single Task (T015)
   - US-6: Toggle Completion (T018)

2. **Priority P2** (Should Have):
   - US-4: Update Task (T016)
   - US-5: Delete Task (T017)

3. **Priority P3** (Nice to Have):
   - Authentication tests (T012)
   - Integration tests (T020-T022)

---

## Execution Guidelines

### Per-Task Checklist

For each task, follow this process:

1. **Before Starting**:
   - Read task description and reference specifications
   - Verify all dependencies completed
   - Understand acceptance criteria

2. **During Implementation**:
   - Create/modify exact files specified
   - Follow implementation details from references
   - Test incrementally as you code
   - Use exact imports and function names from specs

3. **After Completing**:
   - Verify all acceptance criteria met
   - Test the specific functionality
   - Mark task complete in this file: `- [x] TaskID Description`
   - Commit changes with message: "TaskID: Description"

### Testing Strategy

- **After Phase 2**: Test server starts (T007)
- **After Phase 3**: Verify models import without errors
- **After Phase 4**: Test JWT verification manually
- **After Phase 5**: Test all endpoints with curl or Postman
- **After Phase 6**: Run full pytest suite
- **After Phase 7**: Test end-to-end with frontend

### Common Issues & Solutions

**Issue**: `ModuleNotFoundError` for dependencies
- **Solution**: Ensure UV installed all packages (`uv pip install -e ".[dev]"`)

**Issue**: Database connection errors
- **Solution**: Verify `.env` has correct `DATABASE_URL` for Neon PostgreSQL

**Issue**: JWT verification fails
- **Solution**: Ensure `BETTER_AUTH_SECRET` matches frontend value

**Issue**: CORS errors in browser
- **Solution**: Verify `CORS_ORIGINS=http://localhost:3000` in `.env`

**Issue**: 401 on all requests
- **Solution**: Check Authorization header format: `Bearer <token>`

---

## Task Summary

**Total Tasks**: 25 tasks

**By Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundation): 4 tasks
- Phase 3 (Database): 3 tasks
- Phase 4 (Authentication): 2 tasks
- Phase 5 (CRUD): 7 tasks
- Phase 6 (Testing): 3 tasks
- Phase 7 (Integration): 3 tasks

**By User Story**:
- US-1 (Create Task): 1 task (T013)
- US-2 (List Tasks): 1 task (T014)
- US-3 (Get Single Task): 1 task (T015)
- US-4 (Update Task): 1 task (T016)
- US-5 (Delete Task): 1 task (T017)
- US-6 (Toggle Completion): 1 task (T018)
- Infrastructure: 18 tasks (T001-T012, T019-T025)

**Parallel Opportunities**: 5 tasks marked with [P]
- T012 (auth tests)
- T013-T018 (CRUD endpoints can be parallelized)
- T020-T021 (test fixtures and tests)

**Estimated Time**:
- Sequential execution: ~8-10 hours
- With parallelization: ~6-8 hours

---

## Success Criteria

**Backend is complete when**:
- ✅ All 25 tasks marked complete
- ✅ Server starts without errors
- ✅ All 6 CRUD endpoints working
- ✅ JWT authentication on all routes
- ✅ User isolation enforced
- ✅ All tests passing (pytest)
- ✅ Frontend integration verified
- ✅ Security checklist complete
- ✅ Documentation complete

**Ready for deployment when**:
- ✅ All above criteria met
- ✅ Environment variables documented
- ✅ Database migrations applied
- ✅ HTTPS configured (production only)
- ✅ Error handling tested
- ✅ Performance verified with indexes

---

**Tasks Status**: 20/25 Complete
**Last Updated**: 2026-01-05
**Ready to Start**: Yes - Begin with T001
