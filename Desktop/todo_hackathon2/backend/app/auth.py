"""JWT authentication and verification."""
import jwt
from datetime import datetime, timedelta
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


def create_jwt_token(user_id: str, email: str = "") -> str:
    """
    Create a JWT token for authenticated user.

    Args:
        user_id: User's unique identifier
        email: User's email address (optional)

    Returns:
        str: Encoded JWT token

    Token Format (compatible with Better Auth):
    {
        "sub": "user_id",
        "email": "user@example.com",
        "exp": expiration_timestamp,
        "aud": "http://localhost:3000",
        "iss": "better-auth"
    }
    """
    # Token expires in 7 days
    expiration = datetime.utcnow() + timedelta(days=7)

    payload = {
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "exp": expiration,
        "aud": settings.jwt_audience,  # http://localhost:3000
        "iss": settings.jwt_issuer,  # better-auth
    }

    token = jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm=settings.jwt_algorithm
    )

    return token


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
