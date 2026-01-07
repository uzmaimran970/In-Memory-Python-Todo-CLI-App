"""Database connection and session management."""
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings
from typing import Generator


# Create SQLModel engine with connection pooling for Neon PostgreSQL
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
