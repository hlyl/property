"""Database connection management.

This module provides centralized database engine creation and session
management using SQLModel and SQLAlchemy.
"""

from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import Engine


# Global engine instance (singleton pattern)
_engine: Engine | None = None


def get_engine(use_test_db: bool = False) -> Engine:
    """Get or create database engine (singleton).

    Args:
        use_test_db: If True, use test database; otherwise use production database

    Returns:
        SQLAlchemy Engine instance

    Note:
        This function uses a module-level singleton to ensure only one engine
        is created per application instance.
    """
    global _engine

    if _engine is None:
        # Import here to avoid circular dependency
        from property_tracker.config.settings import get_database_url

        database_url = get_database_url(use_test_db=use_test_db)
        _engine = create_engine(database_url, echo=False)

    return _engine


@contextmanager
def get_session(use_test_db: bool = False) -> Generator[Session, None, None]:
    """Context manager for database sessions.

    Provides automatic commit/rollback and session cleanup.

    Args:
        use_test_db: If True, use test database; otherwise use production database

    Yields:
        SQLModel Session instance

    Example:
        ```python
        with get_session() as session:
            property = session.get(Property, property_id)
            property.review_status = "Interested"
            session.commit()
        # Session automatically closed
        ```

    Note:
        - Commits on successful completion
        - Rolls back on exception
        - Always closes session in finally block
    """
    engine = get_engine(use_test_db=use_test_db)
    session = Session(engine)

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_database_tables(engine: Engine | None = None) -> None:
    """Create all database tables defined in SQLModel metadata.

    Args:
        engine: Optional engine to use; if None, uses default engine

    Note:
        This should be called once during application initialization
        or when setting up a new database.
    """
    if engine is None:
        engine = get_engine()

    SQLModel.metadata.create_all(engine)


def reset_engine() -> None:
    """Reset the global engine instance.

    This is primarily useful for testing to ensure a fresh engine
    between test runs.

    Warning:
        This will dispose of the current engine, closing all connections.
    """
    global _engine

    if _engine is not None:
        _engine.dispose()
        _engine = None
