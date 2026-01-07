# Todo Backend - FastAPI

FastAPI backend for Todo application with JWT authentication and PostgreSQL.

## Quick Start

### Prerequisites

- Python 3.10+
- UV package manager (or pip)
- Neon PostgreSQL database
- Better Auth secret (shared with frontend)

### Installation

1. **Install dependencies:**
```bash
cd backend
uv venv
uv pip install fastapi uvicorn[standard] sqlmodel pydantic pydantic-settings psycopg2-binary pyjwt python-dotenv alembic pytest pytest-asyncio httpx
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your actual values
```

Required environment variables:
- `DATABASE_URL` - Your Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Must match the frontend secret

3. **Start server:**
```bash
# From backend directory
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Open API docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### Task Operations

- `POST /api/tasks` - Create new task
- `GET /api/tasks` - List tasks (with filtering: `?status=pending&sort=created`)
- `GET /api/tasks/{id}` - Get single task
- `PUT /api/tasks/{id}` - Update task title/description
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle completion status

### Health Checks

- `GET /` - API information
- `GET /health` - Health check

## Testing

```bash
pytest
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Pydantic Settings
│   ├── database.py      # SQLModel database connection
│   ├── models.py        # Database models (Task)
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # JWT verification
│   └── routers/
│       ├── __init__.py
│       └── tasks.py     # Task CRUD endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Test fixtures
│   └── test_tasks.py    # Integration tests
├── pyproject.toml       # Project dependencies
├── .env.example         # Environment variable template
├── .env                 # Environment variables (gitignored)
└── README.md            # This file
```

## Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `DATABASE_URL` - PostgreSQL connection string (from Neon)
- `BETTER_AUTH_SECRET` - Shared secret with frontend for JWT verification

**Optional:**
- `JWT_ALGORITHM` - Default: HS256
- `JWT_AUDIENCE` - Default: http://localhost:3000
- `JWT_ISSUER` - Default: better-auth
- `CORS_ORIGINS` - Default: http://localhost:3000
- `HOST` - Default: 0.0.0.0
- `PORT` - Default: 8000
- `RELOAD` - Default: true

## Security

- All endpoints require valid JWT authentication
- User isolation enforced at database query level
- Ownership verified before read/update/delete operations
- HTTPS required in production

## CORS

Configured to allow requests from `http://localhost:3000` (frontend).
Update `CORS_ORIGINS` in `.env` for production.

## Database

Uses Neon Serverless PostgreSQL with SQLModel ORM.

**Connection pooling:**
- Pool size: 5
- Max overflow: 10
- Connection recycling: 3600 seconds (1 hour)
- SSL mode: required

## Development

```bash
# Start dev server with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest -v

# Check API docs
open http://localhost:8000/docs
```

## Production Deployment

1. Set `RELOAD=false` in production environment
2. Use production HTTPS-enabled server
3. Set appropriate `CORS_ORIGINS` for your frontend domain
4. Ensure `BETTER_AUTH_SECRET` is securely stored
5. Use proper logging and monitoring

## Troubleshooting

**Database connection errors:**
- Verify `DATABASE_URL` is correct
- Ensure Neon PostgreSQL allows SSL connections
- Check network connectivity

**JWT verification fails:**
- Verify `BETTER_AUTH_SECRET` matches frontend
- Check token expiration
- Ensure JWT audience and issuer match configuration

**CORS errors:**
- Verify `CORS_ORIGINS` includes your frontend URL
- Check Authorization header is being sent

## Documentation

- API Specifications: `specs/003-fastapi-backend/`
- Database Schema: `specs/003-fastapi-backend/database/schema.md`
- Authentication: `specs/003-fastapi-backend/features/authentication.md`
- REST Endpoints: `specs/003-fastapi-backend/api/rest-endpoints.md`

## License

MIT
