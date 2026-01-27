"""Database connection and session management."""
import os
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings
from typing import Generator


# Determine SSL mode based on environment
# Use 'require' for cloud databases (Neon), 'disable' for local development
def get_connect_args():
    """Get database connection arguments based on environment."""
    db_url = settings.database_url.lower()
    # If using Neon or other cloud PostgreSQL, require SSL
    if 'neon.tech' in db_url or 'sslmode=require' in db_url:
        return {"sslmode": "require"}
    # For local development, disable SSL
    return {"sslmode": "disable"}


# Create SQLModel engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=False,  # Set True for SQL query logging in development
    pool_size=5,  # Max 5 persistent connections
    max_overflow=10,  # Max 10 additional connections if pool exhausted
    pool_pre_ping=True,  # Verify connections before use (detect stale connections)
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args=get_connect_args()
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
