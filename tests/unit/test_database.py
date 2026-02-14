"""Unit tests for database layer.

Tests database connection management, engine creation, and context managers.
"""

import os

from sqlmodel import Session, SQLModel

from property_tracker.database.connection import create_database_tables, get_engine, get_session, reset_engine
from property_tracker.models.property import Property


def test_get_engine_creates_engine():
    """Test that get_engine creates an engine."""
    engine = get_engine(use_test_db=True)
    assert engine is not None
    assert str(engine.url).endswith("test.db")


def test_get_engine_singleton():
    """Test that get_engine returns singleton instance."""
    reset_engine()  # Clear any cached engine

    engine1 = get_engine(use_test_db=True)
    engine2 = get_engine(use_test_db=True)

    # Should be the same instance (singleton pattern)
    assert engine1 is engine2


def test_reset_engine():
    """Test that reset_engine clears the singleton."""
    engine1 = get_engine(use_test_db=True)

    reset_engine()

    engine2 = get_engine(use_test_db=True)

    # Should be different instances after reset
    assert engine1 is not engine2


def test_get_session_context_manager():
    """Test get_session context manager."""
    with get_session(use_test_db=True) as session:
        assert session is not None

        # Add a property
        prop = Property(
            id=999,
            region="TEST",
            province="TS",
            category="Residenziale",
            price=100000,
            discription="Test",
            discription_dk="Test",
            photo_list="[]"
        )
        session.add(prop)
        # Session should auto-commit on successful exit

    # Verify it was saved
    with get_session(use_test_db=True) as session:
        saved = session.get(Property, 999)
        assert saved is not None
        assert saved.region == "TEST"


def test_get_session_rollback_on_exception():
    """Test that session rolls back on exception."""
    property_id = 888

    try:
        with get_session(use_test_db=True) as session:
            prop = Property(
                id=property_id,
                region="ROLLBACK_TEST",
                province="RT",
                category="Residenziale",
                price=150000,
                discription="Should rollback",
                discription_dk="Skal rulles tilbage",
                photo_list="[]"
            )
            session.add(prop)

            # Force an exception
            raise ValueError("Test exception")

    except ValueError:
        pass  # Expected

    # Verify property was NOT saved (rollback occurred)
    with get_session(use_test_db=True) as session:
        not_saved = session.get(Property, property_id)
        assert not_saved is None


def test_create_database_tables():
    """Test creating database tables."""
    reset_engine()
    engine = get_engine(use_test_db=True)

    create_database_tables(engine)

    # Verify table exists by querying
    with get_session(use_test_db=True) as session:
        # Should not raise an error
        result = session.exec(Property.__table__.select())
        assert result is not None


def test_create_database_tables_default_engine(test_db_path):
    """Test creating tables with default engine."""
    # Clean up test database file
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    reset_engine()

    # Get fresh engine and create tables manually
    engine = get_engine(use_test_db=True)
    SQLModel.metadata.create_all(engine)

    # Verify tables created
    with get_session(use_test_db=True) as session:
        result = session.exec(Property.__table__.select())
        assert result is not None


def test_session_isolation(test_db_path, sample_property):
    """Test that sessions are isolated."""
    # Clean up test database file
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    reset_engine()
    engine = get_engine(use_test_db=True)
    SQLModel.metadata.create_all(engine)

    # Get the ID before the session is closed
    prop_id = sample_property.id

    session = Session(engine)
    # Add property in test session
    session.add(sample_property)
    session.commit()
    session.close()

    # Create new session
    with get_session(use_test_db=True) as new_session:
        # Should be able to retrieve the property using the ID
        prop = new_session.get(Property, prop_id)
        assert prop is not None


def test_concurrent_sessions():
    """Test multiple concurrent sessions."""
    with get_session(use_test_db=True) as session1, get_session(use_test_db=True) as session2:
        # Both sessions should be valid
        assert session1 is not None
        assert session2 is not None

        # They should be different session instances
        assert session1 is not session2


def test_session_commit_on_success(test_db_path):
    """Test that changes are committed on successful exit."""
    # Clean up test database file
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    reset_engine()
    engine = get_engine(use_test_db=True)
    SQLModel.metadata.create_all(engine)

    prop_id = 777

    with get_session(use_test_db=True) as session:
        prop = Property(
            id=prop_id,
            region="COMMIT_TEST",
            province="CT",
            category="Residenziale",
            price=200000,
            discription="Should commit",
            discription_dk="Skal committe",
            photo_list="[]"
        )
        session.add(prop)
        # Exit context - should auto-commit

    # Verify it persisted
    with get_session(use_test_db=True) as session:
        saved = session.get(Property, prop_id)
        assert saved is not None
        assert saved.region == "COMMIT_TEST"


def test_engine_connection_string():
    """Test that engine has correct connection string."""
    reset_engine()
    engine = get_engine(use_test_db=True)

    url_str = str(engine.url)
    assert "sqlite:///" in url_str
    assert "test.db" in url_str


def test_engine_disposal():
    """Test that engine can be properly disposed."""
    reset_engine()
    engine = get_engine(use_test_db=True)

    # Dispose should not raise error
    engine.dispose()

    # After reset, new engine should be created
    reset_engine()
    new_engine = get_engine(use_test_db=True)
    assert new_engine is not None
