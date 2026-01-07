# Authentication Specification: JWT Verification for FastAPI Backend

**Feature**: JWT Authentication and User Extraction
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-01-05
**Last Updated**: 2026-01-05

---

## Overview

This specification defines the complete authentication system for the Phase II Todo Hackathon FastAPI backend. The system uses **JWT (JSON Web Tokens)** issued by **Better Auth** on the frontend to authenticate API requests and extract user identity.

**Key Design Principles**:
- **Stateless Authentication**: No server-side sessions, tokens carry all user information
- **Security First**: Verify every token signature using shared secret
- **Zero Trust**: Treat every request as untrusted until JWT validated
- **Fail Secure**: Return 401 for invalid/missing tokens, 403 for authorization failures
- **Dependency Injection**: Use FastAPI dependencies to inject authenticated user into routes

**Authentication Flow**:
```
1. User logs in via Better Auth (frontend) → JWT issued
2. Frontend stores JWT (localStorage/cookie)
3. Frontend sends JWT in Authorization: Bearer <token>
4. Backend extracts token from header
5. Backend verifies signature using BETTER_AUTH_SECRET
6. Backend decodes token → extracts user_id
7. Backend injects user_id into route handler
8. Route handler uses user_id for data access
```

---

## Technology Stack

**JWT Library**: `PyJWT` (Python JWT implementation)
**Secret Management**: Environment variables (`.env`)
**FastAPI Integration**: Dependency injection via `Depends()`
**Error Handling**: HTTPException with proper status codes

**Dependencies**:
```txt
pyjwt[crypto]==2.8.0       # JWT encoding/decoding with cryptographic signing
python-dotenv==1.0.0       # Environment variable management
fastapi==0.109.0           # Web framework
python-multipart==0.0.6    # Form data parsing (for token extraction)
```

---

## Better Auth JWT Format

### Token Structure

Better Auth issues JWTs with the following structure:

**JWT Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**JWT Payload** (Claims):
```json
{
  "sub": "clx1234567890",      // Subject: User ID (primary identifier)
  "email": "user@example.com",  // User email
  "name": "John Doe",           // User display name (optional)
  "iat": 1704451200,            // Issued At: Unix timestamp
  "exp": 1704537600,            // Expiration: Unix timestamp (typically 24 hours)
  "aud": "http://localhost:3000", // Audience: Frontend URL
  "iss": "better-auth"          // Issuer: Better Auth
}
```

**JWT Signature**:
- Algorithm: **HS256** (HMAC with SHA-256)
- Secret: `BETTER_AUTH_SECRET` (shared between frontend Better Auth and backend)

**Complete Token Example**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbHgxMjM0NTY3ODkwIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNzA0NDUxMjAwLCJleHAiOjE3MDQ1Mzc2MDAsImF1ZCI6Imh0dHA6Ly9sb2NhbGhvc3Q6MzAwMCIsImlzcyI6ImJldHRlci1hdXRoIn0.signature
```

**Key Claims Used by Backend**:
- `sub`: User ID (used as `user_id` in database queries)
- `exp`: Token expiration (validate token is not expired)
- `email`: User email (for logging/audit)
- `name`: User display name (optional, for user info endpoints)

---

## Environment Configuration

### Required Environment Variables

**`.env` File**:
```env
# Better Auth Secret (MUST match frontend configuration)
BETTER_AUTH_SECRET=9eb4ea939ffbae7e084c9432d41fe55921f786164ba326c7a2070cf75fca58c6

# Better Auth URL (frontend URL for CORS and audience validation)
BETTER_AUTH_URL=http://localhost:3000

# Token Configuration
JWT_ALGORITHM=HS256
JWT_AUDIENCE=http://localhost:3000
JWT_ISSUER=better-auth

# Environment
ENVIRONMENT=development
```

**Security Notes**:
- ⚠️ **NEVER** commit `.env` to version control
- ⚠️ **NEVER** hardcode `BETTER_AUTH_SECRET` in source code
- ✅ **DO** use different secrets for development/staging/production
- ✅ **DO** rotate secrets periodically (every 90 days recommended)
- ✅ **DO** use strong secrets (minimum 32 characters, random)

---

## Authentication Implementation

### 1. JWT Utilities Module

**`app/auth.py`** - Core authentication logic:

```python
"""
Authentication Module - JWT Verification and User Extraction
Provides FastAPI dependencies for protected routes.
"""

import os
from datetime import datetime, timezone
from typing import Optional, Annotated

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "http://localhost:3000")
JWT_ISSUER = os.getenv("JWT_ISSUER", "better-auth")

if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

# HTTPBearer scheme for extracting Bearer tokens
bearer_scheme = HTTPBearer(
    scheme_name="JWT Bearer Token",
    description="Enter your JWT token from Better Auth",
    auto_error=True  # Automatically raise 401 if token missing
)


class TokenData:
    """
    Structured representation of decoded JWT payload.
    Contains user information extracted from token.
    """
    def __init__(
        self,
        user_id: str,
        email: str,
        name: Optional[str] = None,
        exp: Optional[int] = None,
        iat: Optional[int] = None
    ):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.exp = exp
        self.iat = iat

    def __repr__(self):
        return f"TokenData(user_id={self.user_id}, email={self.email})"


def verify_jwt_token(token: str) -> TokenData:
    """
    Verify and decode JWT token from Better Auth.

    Args:
        token: JWT token string (without 'Bearer ' prefix)

    Returns:
        TokenData: Decoded token data with user information

    Raises:
        HTTPException(401): If token is invalid, expired, or malformed
        HTTPException(401): If required claims missing
        HTTPException(401): If signature verification fails

    Security Checks:
    1. Signature verification using BETTER_AUTH_SECRET
    2. Expiration validation (exp claim)
    3. Audience validation (aud claim)
    4. Issuer validation (iss claim)
    5. Required claims presence (sub, email)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify JWT token
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={
                "verify_signature": True,      # Verify HMAC signature
                "verify_exp": True,            # Verify expiration
                "verify_aud": True,            # Verify audience
                "verify_iss": True,            # Verify issuer
                "require": ["sub", "exp"]      # Require sub and exp claims
            }
        )

        # Extract user ID from 'sub' claim
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception

        # Extract email (should always be present from Better Auth)
        email: str = payload.get("email")
        if not email:
            raise credentials_exception

        # Extract optional fields
        name: Optional[str] = payload.get("name")
        exp: Optional[int] = payload.get("exp")
        iat: Optional[int] = payload.get("iat")

        return TokenData(
            user_id=user_id,
            email=email,
            name=name,
            exp=exp,
            iat=iat
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        # Catch-all for unexpected errors (log in production)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]
) -> TokenData:
    """
    FastAPI dependency to extract and validate current user from JWT.

    This is the PRIMARY dependency used by all protected routes.

    Usage in routes:
        @app.get("/api/protected")
        async def protected_route(
            current_user: TokenData = Depends(get_current_user)
        ):
            # current_user.user_id is guaranteed to be valid
            return {"user_id": current_user.user_id}

    Args:
        credentials: HTTP Bearer credentials (extracted by bearer_scheme)

    Returns:
        TokenData: Validated user information from JWT

    Raises:
        HTTPException(401): If token missing, invalid, or expired

    Security Guarantees:
    - If this function returns successfully, the token is valid
    - user_id is guaranteed to be from a valid, unexpired JWT
    - Signature has been cryptographically verified
    - All claims have been validated
    """
    # Extract token from Bearer scheme
    token = credentials.credentials

    # Verify and decode token
    token_data = verify_jwt_token(token)

    return token_data


async def get_current_user_id(
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> str:
    """
    Convenience dependency to get only the user_id.

    Useful when you only need the user ID for database queries.

    Usage:
        @app.get("/api/tasks")
        async def get_tasks(
            user_id: str = Depends(get_current_user_id)
        ):
            # user_id is a validated string from JWT
            tasks = query_tasks_by_user(user_id)
            return tasks

    Args:
        current_user: TokenData from get_current_user dependency

    Returns:
        str: Validated user_id from JWT

    Note:
        This is a convenience wrapper around get_current_user.
        It still performs full JWT validation.
    """
    return current_user.user_id


# Optional: Dependency for routes that need full user info
async def get_current_user_email(
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> str:
    """Get user email from validated JWT"""
    return current_user.email
```

---

## Usage in FastAPI Routes

### Protected Route Examples

**Example 1: Using `get_current_user` (Full User Info)**:
```python
from fastapi import APIRouter, Depends
from app.auth import get_current_user, TokenData

router = APIRouter(prefix="/api", tags=["tasks"])

@router.get("/tasks")
async def get_user_tasks(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all tasks for authenticated user.

    - Requires valid JWT token
    - Returns 401 if token invalid/missing
    - Automatically extracts user_id from token
    """
    # Access user information
    user_id = current_user.user_id
    user_email = current_user.email
    user_name = current_user.name

    # Query database with user_id
    tasks = query_tasks(user_id)

    return {
        "user_id": user_id,
        "email": user_email,
        "tasks": tasks
    }
```

**Example 2: Using `get_current_user_id` (User ID Only)**:
```python
@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new task for authenticated user.

    - Requires valid JWT
    - user_id automatically extracted from token
    - user_id is validated and guaranteed to be from valid JWT
    """
    # Create task with authenticated user_id
    new_task = Task(
        user_id=user_id,  # From JWT, not request body
        title=task_data.title,
        description=task_data.description,
        completed=False
    )

    session.add(new_task)
    session.commit()

    return new_task
```

**Example 3: Task Ownership Verification** (403 Forbidden):
```python
@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Get a specific task.

    - Requires valid JWT (401 if missing/invalid)
    - Verifies task ownership (403 if user doesn't own task)
    """
    # Query task from database
    task = session.get(Task, task_id)

    # Check task exists
    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found"
        )

    # CRITICAL: Verify task belongs to authenticated user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=403,  # Forbidden (not Unauthorized)
            detail="You do not have permission to access this task"
        )

    return task
```

**Example 4: Optional Authentication** (Public + Protected):
```python
from typing import Optional

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[TokenData]:
    """
    Optional authentication dependency.
    Returns user if token provided and valid, None otherwise.
    Does not raise 401 if token missing.
    """
    if not credentials:
        return None

    try:
        return verify_jwt_token(credentials.credentials)
    except HTTPException:
        return None

@router.get("/public-endpoint")
async def public_or_protected(
    current_user: Optional[TokenData] = Depends(get_optional_user)
):
    """
    Endpoint accessible to both authenticated and anonymous users.
    """
    if current_user:
        return {"message": f"Hello, {current_user.email}"}
    else:
        return {"message": "Hello, anonymous user"}
```

---

## Error Handling

### HTTP Status Codes

**401 Unauthorized** - Authentication Failed:
- Missing `Authorization` header
- Invalid JWT format
- Expired token
- Invalid signature
- Missing required claims
- Token verification failure

**403 Forbidden** - Authorization Failed:
- Valid token, but user not allowed to access resource
- Task ownership mismatch (user trying to access another user's task)
- Insufficient permissions

**Response Format**:
```json
{
  "detail": "Could not validate credentials"
}
```

### Error Response Examples

**Error 1: Missing Token**:
```http
GET /api/tasks HTTP/1.1
# (No Authorization header)

HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
{
  "detail": "Not authenticated"
}
```

**Error 2: Expired Token**:
```http
GET /api/tasks HTTP/1.1
Authorization: Bearer <expired_token>

HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
{
  "detail": "Token has expired. Please log in again."
}
```

**Error 3: Invalid Signature**:
```http
GET /api/tasks HTTP/1.1
Authorization: Bearer <tampered_token>

HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
{
  "detail": "Invalid token: Signature verification failed"
}
```

**Error 4: Task Ownership Violation**:
```http
GET /api/tasks/123 HTTP/1.1
Authorization: Bearer <valid_token_for_user_A>
# Task 123 belongs to user_B

HTTP/1.1 403 Forbidden
{
  "detail": "You do not have permission to access this task"
}
```

---

## Security Best Practices

### 1. Token Validation

**Always Validate**:
- ✅ Signature verification
- ✅ Expiration (`exp` claim)
- ✅ Audience (`aud` claim) - prevents token reuse on different services
- ✅ Issuer (`iss` claim) - ensures token from Better Auth
- ✅ Required claims (`sub`, `email`)

**Never Trust Client Input**:
- ❌ Never accept `user_id` from request body
- ❌ Never accept `user_id` from query parameters
- ❌ Never accept `user_id` from headers (except JWT)
- ✅ Always extract `user_id` from verified JWT token

### 2. Secret Management

**Shared Secret Security**:
```python
# ❌ NEVER DO THIS
BETTER_AUTH_SECRET = "hardcoded-secret-123"

# ✅ ALWAYS DO THIS
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET must be set")
```

**Secret Requirements**:
- Minimum 32 characters (256 bits)
- Cryptographically random
- Same secret used in frontend Better Auth config
- Never logged or exposed in error messages

### 3. No Server-Side Sessions

**Stateless Design**:
- ✅ All user information in JWT
- ✅ No session storage on backend
- ✅ No user session database table
- ✅ Token carries all context

**Benefits**:
- Scalability: No session synchronization
- Simplicity: No session management
- Performance: No session lookups

### 4. Token Expiration Handling

**Frontend Responsibility**:
- Frontend detects 401 errors
- Frontend redirects to login page
- Frontend requests new token from Better Auth
- Backend does NOT refresh tokens (Better Auth handles this)

**Backend Responsibility**:
- Validate `exp` claim
- Return 401 if expired
- Include helpful error message

### 5. HTTPS in Production

**Development**:
- HTTP acceptable for localhost
- Token transmitted in Authorization header

**Production**:
- ⚠️ **MANDATORY**: Use HTTPS/TLS
- Prevents token interception
- Prevents man-in-the-middle attacks

### 6. CORS Configuration

**Allow frontend origin**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Development frontend
        "https://yourdomain.com"      # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Integration with Better Auth

### Frontend → Backend Flow

**1. User Login (Frontend)**:
```typescript
// Frontend: Better Auth login
const { data, error } = await signIn.email({
  email: "user@example.com",
  password: "password123"
});

// Better Auth stores JWT in localStorage/cookie
// JWT contains: { sub: "user_id", email, exp, ... }
```

**2. API Request (Frontend)**:
```typescript
// Frontend: API client
const token = localStorage.getItem("auth_token");

const response = await fetch("http://localhost:8000/api/tasks", {
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  }
});
```

**3. Token Verification (Backend)**:
```python
# Backend: Automatic via Depends(get_current_user)
@app.get("/api/tasks")
async def get_tasks(user_id: str = Depends(get_current_user_id)):
    # user_id is validated and extracted from JWT
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    return tasks
```

### Shared Configuration

**Both frontend and backend must use**:
- Same `BETTER_AUTH_SECRET`
- Same JWT algorithm (`HS256`)
- Compatible audience/issuer values

**Frontend `.env`**:
```env
BETTER_AUTH_SECRET=9eb4ea939ffbae7e084c9432d41fe55921f786164ba326c7a2070cf75fca58c6
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

**Backend `.env`**:
```env
BETTER_AUTH_SECRET=9eb4ea939ffbae7e084c9432d41fe55921f786164ba326c7a2070cf75fca58c6
BETTER_AUTH_URL=http://localhost:3000
JWT_ALGORITHM=HS256
```

---

## Testing

### Unit Tests

**Test 1: Valid Token Decoding**:
```python
import pytest
from app.auth import verify_jwt_token
import jwt
from datetime import datetime, timedelta, timezone

def test_valid_token():
    """Test successful token verification"""
    # Create test token
    payload = {
        "sub": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "aud": "http://localhost:3000",
        "iss": "better-auth"
    }

    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")

    # Verify token
    token_data = verify_jwt_token(token)

    assert token_data.user_id == "test_user_123"
    assert token_data.email == "test@example.com"
    assert token_data.name == "Test User"
```

**Test 2: Expired Token**:
```python
def test_expired_token():
    """Test expired token raises 401"""
    payload = {
        "sub": "test_user_123",
        "email": "test@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
        "aud": "http://localhost:3000",
        "iss": "better-auth"
    }

    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        verify_jwt_token(token)

    assert exc.value.status_code == 401
    assert "expired" in exc.value.detail.lower()
```

**Test 3: Invalid Signature**:
```python
def test_invalid_signature():
    """Test token with wrong secret raises 401"""
    payload = {
        "sub": "test_user_123",
        "email": "test@example.com",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "aud": "http://localhost:3000",
        "iss": "better-auth"
    }

    # Sign with wrong secret
    wrong_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        verify_jwt_token(wrong_token)

    assert exc.value.status_code == 401
```

**Test 4: Missing Claims**:
```python
def test_missing_sub_claim():
    """Test token without 'sub' claim raises 401"""
    payload = {
        # Missing 'sub'
        "email": "test@example.com",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "aud": "http://localhost:3000",
        "iss": "better-auth"
    }

    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        verify_jwt_token(token)

    assert exc.value.status_code == 401
```

### Integration Tests

**Test 5: Protected Endpoint Without Token**:
```python
from fastapi.testclient import TestClient

def test_protected_route_no_token(client: TestClient):
    """Test protected endpoint returns 401 without token"""
    response = client.get("/api/tasks")

    assert response.status_code == 401
    assert "detail" in response.json()
```

**Test 6: Protected Endpoint With Valid Token**:
```python
def test_protected_route_with_valid_token(client: TestClient):
    """Test protected endpoint works with valid token"""
    # Create valid token
    token = create_test_token(user_id="test_user_123")

    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
```

**Test 7: Task Ownership Verification**:
```python
def test_task_access_forbidden(client: TestClient, session: Session):
    """Test user cannot access another user's task"""
    # Create task for user_A
    task_a = Task(user_id="user_a", title="Task A", completed=False)
    session.add(task_a)
    session.commit()

    # Try to access with user_B's token
    token_b = create_test_token(user_id="user_b")

    response = client.get(
        f"/api/tasks/{task_a.id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )

    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()
```

---

## Acceptance Criteria

### Token Validation

- [ ] **Valid Token**
  - Accepts tokens with valid signature
  - Accepts unexpired tokens
  - Accepts tokens with required claims (sub, email, exp)
  - Extracts user_id from 'sub' claim correctly
  - Extracts email from token correctly

- [ ] **Invalid Token Rejection**
  - Returns 401 for missing Authorization header
  - Returns 401 for malformed tokens
  - Returns 401 for expired tokens
  - Returns 401 for invalid signatures
  - Returns 401 for tokens missing required claims
  - Returns 401 for tokens with wrong audience
  - Returns 401 for tokens with wrong issuer

### Dependency Injection

- [ ] **get_current_user Dependency**
  - Injects TokenData into route handlers
  - Raises 401 if token invalid
  - Works with async route handlers
  - Can be used multiple times in same route
  - Thread-safe and request-scoped

- [ ] **get_current_user_id Dependency**
  - Returns validated user_id string
  - Raises 401 if token invalid
  - Convenience wrapper for user_id extraction

### Authorization

- [ ] **Task Ownership Verification**
  - Returns 403 when user tries to access another user's task
  - Allows access when task.user_id matches JWT user_id
  - Works for all CRUD operations (GET, PUT, DELETE)

### Error Responses

- [ ] **Error Format**
  - Returns JSON with "detail" field
  - Includes WWW-Authenticate header for 401 errors
  - Error messages are user-friendly
  - No sensitive information in error messages

### Security

- [ ] **Secret Management**
  - BETTER_AUTH_SECRET loaded from environment
  - Application fails to start if secret missing
  - Secret never logged or exposed

- [ ] **Stateless Operation**
  - No session storage
  - No session database
  - Token carries all user context

### Integration

- [ ] **Better Auth Compatibility**
  - Accepts tokens from Better Auth
  - Verifies signature with shared secret
  - Extracts user_id from 'sub' claim
  - Handles Better Auth token format

- [ ] **Frontend Integration**
  - Accepts Authorization: Bearer header format
  - CORS configured for frontend origin
  - Returns proper error codes for frontend handling

---

## Common Pitfalls and Solutions

### Pitfall 1: Accepting user_id from Request Body

**❌ WRONG**:
```python
@app.post("/api/tasks")
async def create_task(task_data: TaskCreate, user_id: str):
    # user_id from query param or body - INSECURE!
    task = Task(user_id=user_id, title=task_data.title)
    return task
```

**✅ CORRECT**:
```python
@app.post("/api/tasks")
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user_id)  # From JWT
):
    task = Task(user_id=user_id, title=task_data.title)
    return task
```

### Pitfall 2: Not Verifying Task Ownership

**❌ WRONG**:
```python
@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    session.delete(task)  # Deletes ANY user's task!
    return {"deleted": True}
```

**✅ CORRECT**:
```python
@app.delete("/api/tasks/{task_id}")
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task.user_id != user_id:
        raise HTTPException(403, "Not your task")  # Security check
    session.delete(task)
    return {"deleted": True}
```

### Pitfall 3: Hardcoding Secrets

**❌ WRONG**:
```python
BETTER_AUTH_SECRET = "my-secret-123"  # NEVER DO THIS
```

**✅ CORRECT**:
```python
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable required")
```

---

## Cross-References

- **Database Schema**: `specs/003-fastapi-backend/database/schema.md`
- **API Endpoints**: `specs/003-fastapi-backend/api/rest-endpoints.md`
- **Task CRUD Operations**: `specs/003-fastapi-backend/features/task-crud.md`
- **Integration Guide**: `specs/003-fastapi-backend/integration.md`

---

**Document Status**: Ready for Implementation (`/sp.plan`)
