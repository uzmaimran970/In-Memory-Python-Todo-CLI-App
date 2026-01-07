"""Pytest fixtures for testing."""
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
