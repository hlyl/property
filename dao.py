"""Database access layer - backwards compatibility module.

This module re-exports the Property model from property_tracker for backwards compatibility.
New code should import directly from property_tracker.models.property.
"""

from sqlalchemy import Engine
from sqlmodel import create_engine

from property_tracker.models.property import Property

__all__ = ['Property', 'create_db']


def create_db(db_name: str) -> Engine:
    """Create a SQLite database and initialize the schema.

    Args:
        db_name: Name of the database file (e.g., 'database.db')

    Returns:
        SQLAlchemy Engine instance for the database
    """
    from sqlmodel import SQLModel
    engine = create_engine(f"sqlite:///{db_name}")
    SQLModel.metadata.create_all(engine)
    return engine

