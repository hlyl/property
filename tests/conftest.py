"""Pytest configuration and shared fixtures.

This module provides test configuration and reusable fixtures
for the Property Tracker test suite.
"""

import pytest
import os
import json
from pathlib import Path
from sqlmodel import create_engine, Session, SQLModel
from property_tracker.models.property import Property
from property_tracker.config.settings import TEST_DATABASE_PATH


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database once before all tests.

    This fixture automatically runs before any tests and ensures
    the test database file exists with proper schema.
    """
    # Remove old test database if it exists
    if os.path.exists(TEST_DATABASE_PATH):
        os.remove(TEST_DATABASE_PATH)

    yield

    # Optional: Clean up after all tests complete
    # Commented out to allow inspection of test data
    # if os.path.exists(TEST_DATABASE_PATH):
    #     os.remove(TEST_DATABASE_PATH)


@pytest.fixture(scope="function", autouse=True)
def clean_database_per_test():
    """Clean database before each test function.

    Drops and recreates all tables to ensure test isolation.
    """
    engine = create_engine(f"sqlite:///{TEST_DATABASE_PATH}", echo=False)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    engine.dispose()
    yield


@pytest.fixture(scope="session")
def test_db_path():
    """Provide test database path.

    Returns:
        Path to test database file
    """
    return TEST_DATABASE_PATH


@pytest.fixture(scope="function")
def db_engine(test_db_path):
    """Create in-memory test database engine.

    Creates a fresh database engine for each test function,
    ensuring test isolation.

    Args:
        test_db_path: Path to test database

    Yields:
        SQLAlchemy Engine instance
    """
    engine = create_engine(f"sqlite:///{test_db_path}", echo=False)
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Provide database session for tests.

    Creates a session with automatic rollback after each test
    to maintain database isolation.

    Args:
        db_engine: Database engine fixture

    Yields:
        SQLModel Session instance
    """
    session = Session(db_engine)
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_property():
    """Provide sample Property object for testing.

    Returns:
        Property instance with typical field values
    """
    return Property(
        id=12345,
        region="TUSCANY",
        province="LU",
        city="Lucca",
        category="Residenziale",
        price=250000,
        price_m=2500,
        rooms="3",
        bathrooms="2",
        surface="100",
        latitude="43.8438",
        longitude="10.5077",
        dist_coast="15.5",
        dist_water="2.3",
        sold=0,
        review_status="To Review",
        favorite=0,
        viewed=0,
        hidden=0,
        caption="Beautiful apartment in Tuscany",
        discription="Spacious 3-bedroom apartment",
        discription_dk="Rummelig 3-værelses lejlighed",
        photo_list="[]",
        shopping_count=5,
        pub_count=3,
        baker_count=2,
        food_count=4
    )


@pytest.fixture
def sample_properties_list():
    """Provide list of sample properties with different statuses.

    Returns:
        List of Property instances with varied review statuses
    """
    return [
        Property(
            id=1,
            region="TUSCANY",
            province="LU",
            category="Residenziale",
            price=200000,
            review_status="To Review",
            sold=0,
            discription="Property 1",
            discription_dk="Ejendom 1",
            photo_list="[]"
        ),
        Property(
            id=2,
            region="LOMBARDY",
            province="MI",
            category="Residenziale",
            price=350000,
            review_status="Interested",
            sold=0,
            discription="Property 2",
            discription_dk="Ejendom 2",
            photo_list="[]"
        ),
        Property(
            id=3,
            region="VENETO",
            province="VE",
            category="Residenziale",
            price=180000,
            review_status="Rejected",
            sold=0,
            discription="Property 3",
            discription_dk="Ejendom 3",
            photo_list="[]"
        ),
        Property(
            id=4,
            region="TUSCANY",
            province="FI",
            category="Residenziale",
            price=450000,
            review_status="To Review",
            sold=0,
            discription="Property 4",
            discription_dk="Ejendom 4",
            photo_list="[]"
        ),
    ]


@pytest.fixture
def mock_api_response():
    """Load mock API response from fixtures.

    Returns:
        Dictionary with mock Immobiliare.it API response
    """
    fixture_path = Path(__file__).parent / "fixtures" / "mock_api_responses.json"

    if fixture_path.exists():
        with open(fixture_path) as f:
            return json.load(f)

    # Return minimal mock if file doesn't exist
    return {
        "results": [
            {
                "id": "94471966",
                "region": "TUSCANY",
                "province": "LU",
                "price": 250000,
                "rooms": 3,
                "bathrooms": 2,
                "surface": 100,
                "latitude": 43.8438,
                "longitude": 10.5077
            }
        ]
    }


@pytest.fixture
def populated_db_session(db_session, sample_properties_list):
    """Provide database session with pre-populated test data.

    Args:
        db_session: Database session fixture
        sample_properties_list: List of sample properties

    Yields:
        Session with populated data
    """
    # Add all sample properties to database
    for prop in sample_properties_list:
        db_session.add(prop)
    db_session.flush()  # Make data visible to queries without committing

    yield db_session


@pytest.fixture
def coordinates_italy():
    """Provide valid Italian coordinates for distance testing.

    Returns:
        Dictionary with location names and coordinates
    """
    return {
        "lucca": {"lat": 43.8438, "lon": 10.5077},  # Inland Tuscany
        "viareggio": {"lat": 43.8667, "lon": 10.2500},  # Coastal Tuscany
        "florence": {"lat": 43.7696, "lon": 11.2558},  # Central Tuscany
        "rome": {"lat": 41.9028, "lon": 12.4964},  # Central Italy
        "venice": {"lat": 45.4408, "lon": 12.3155}  # Northeast coast
    }
