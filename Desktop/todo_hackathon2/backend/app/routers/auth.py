"""Authentication endpoints for user signup and login."""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import User
from app.schemas import SignupRequest, LoginRequest, AuthResponse, UserResponse
from app.auth import create_jwt_token, get_current_user_id
import bcrypt
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
async def signup(
    data: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user.

    Returns JWT token for immediate authentication.
    """
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(data.password)

    new_user = User(
        id=user_id,
        email=data.email,
        password_hash=hashed_password,
        name=data.name
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Generate JWT token
    token = create_jwt_token(user_id, new_user.email)

    return AuthResponse(
        token=token,
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name
        )
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Login existing user.

    Returns JWT token for authentication.
    """
    # Find user by email
    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    token = create_jwt_token(user.id, user.email)

    return AuthResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Get current authenticated user's information.

    Requires valid JWT token in Authorization header.
    """
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name
    )
