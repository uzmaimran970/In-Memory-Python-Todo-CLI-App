# Manual Steps Required

## Remaining Tasks (5 of 25)

### T007: Verify Server Starts Successfully ✅ Ready to Test

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected:**
- Server starts on http://localhost:8000
- Visit http://localhost:8000/health → `{"status": "healthy"}`
- Visit http://localhost:8000/docs → OpenAPI documentation loads

### T010: Initialize Alembic and Create Migration ⚠️ Database Setup Required

**IMPORTANT:** Before running migrations, you need a valid Neon PostgreSQL database.

```bash
cd backend

# Initialize Alembic (if not already done)
alembic init alembic

# Update alembic/env.py to import models and use database URL from config
# Then create and apply migration:
alembic revision --autogenerate -m "Initial schema: tasks table"
alembic upgrade head
```

**Note:** This requires:
1. Valid `DATABASE_URL` in `.env`
2. The Neon database to be accessible
3. Alembic configuration in `alembic/env.py`

### T022: Run Full Test Suite ✅ Ready to Test

```bash
cd backend
pytest -v
```

**Expected:** All tests pass (user isolation, CRUD operations, etc.)

### T023: Verify Frontend Integration 🔄 Requires Frontend & Database

**Prerequisites:**
1. Frontend running on http://localhost:3000
2. Backend running on http://localhost:8000
3. Valid `BETTER_AUTH_SECRET` matching frontend
4. Database migrations applied

**Steps:**
1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Login with Better Auth
4. Test CRUD operations in UI

### T024: Security Verification Checklist ✅ Ready to Review

Review implementation against security requirements:
- [x] JWT signature verification implemented
- [x] All endpoints require authentication
- [x] User ID from JWT only (never from request)
- [x] Ownership verification before operations
- [x] Generic error messages (no sensitive data leaks)
- [x] Secrets in .env (not hardcoded)

## Critical Configuration

### 1. Update `.env` file

Replace placeholders in `backend/.env`:
- `BETTER_AUTH_SECRET` - **Must match frontend secret exactly**
- `DATABASE_URL` - Already set to your Neon database

### 2. Get BETTER_AUTH_SECRET from Frontend

Check `frontend/.env.local` or `frontend/.env` for:
```
BETTER_AUTH_SECRET=<the-actual-secret>
```

Copy that exact value to `backend/.env`.

## Quick Start (After Configuration)

```bash
# Terminal 1: Start Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start Frontend (if ready)
cd frontend
npm run dev

# Terminal 3: Run Tests
cd backend
pytest -v
```

## Implementation Status

**Completed (20/25):**
- ✅ Phase 1: Project Setup (T001-T003)
- ✅ Phase 2: Foundation Layer (T004-T006)
- ✅ Phase 3: Database Models (T008-T009)
- ✅ Phase 4: JWT Authentication (T011)
- ✅ Phase 5: All 6 CRUD Endpoints (T013-T019)
- ✅ Phase 6: Test Infrastructure (T020-T021)
- ✅ Phase 7: Documentation (T025)

**Pending (5/25):**
- ⏳ T007: Verify server starts (manual test)
- ⏳ T010: Alembic migration (requires database)
- ⏳ T022: Run test suite (manual test)
- ⏳ T023: Frontend integration (requires frontend)
- ⏳ T024: Security checklist (review)

## Files Created

### Core Application
- `backend/app/main.py` - FastAPI application
- `backend/app/config.py` - Pydantic Settings
- `backend/app/database.py` - SQLModel connection
- `backend/app/models.py` - Task database model
- `backend/app/schemas.py` - Pydantic schemas
- `backend/app/auth.py` - JWT verification
- `backend/app/routers/tasks.py` - All 6 CRUD endpoints

### Configuration
- `backend/pyproject.toml` - Dependencies
- `backend/.env` - Environment variables
- `backend/.env.example` - Template
- `backend/.gitignore` - Git ignore rules

### Testing
- `backend/tests/conftest.py` - Pytest fixtures
- `backend/tests/test_tasks.py` - Integration tests

### Documentation
- `backend/README.md` - Complete setup guide
- `backend/MANUAL_STEPS.md` - This file

## Next Steps

1. **Configure secrets:** Update `BETTER_AUTH_SECRET` in `.env`
2. **Test locally:** Run `uvicorn app.main:app --reload`
3. **Setup database:** Run Alembic migrations (when database ready)
4. **Run tests:** Execute `pytest -v`
5. **Integrate:** Connect with frontend
