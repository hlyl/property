"""Unit tests for data models.

Tests the Property model including defaults, field validation,
and database operations.
"""

from property_tracker.models.property import Property


def test_property_defaults():
    """Test Property model default values."""
    prop = Property(
        id=1,
        region="TEST",
        province="TS",
        category="Residenziale",
        price=100000,
        discription="Test property",
        discription_dk="Test ejendom",
        photo_list="[]",
    )

    # Test default values
    assert prop.review_status == "To Review"
    assert prop.sold == 0
    assert prop.favorite == 0
    assert prop.viewed == 0
    assert prop.hidden == 0
    assert prop.notes is None
    assert prop.reviewed_date is None


def test_property_creation_with_all_fields(sample_property):
    """Test creating Property with all fields."""
    assert sample_property.id == 12345
    assert sample_property.region == "TUSCANY"
    assert sample_property.province == "LU"
    assert sample_property.price == 250000
    assert sample_property.price_m == 2500
    assert sample_property.rooms == "3"
    assert sample_property.bathrooms == "2"
    assert sample_property.latitude == "43.8438"
    assert sample_property.longitude == "10.5077"


def test_property_table_name():
    """Test that Property maps to correct table name."""
    assert Property.__tablename__ == "property"


def test_property_review_status_field():
    """Test review status field behavior."""
    prop = Property(
        id=100,
        region="LOMBARDY",
        province="MI",
        category="Residenziale",
        price=200000,
        review_status="Interested",
        discription="Test",
        discription_dk="Test",
        photo_list="[]",
    )

    assert prop.review_status == "Interested"


def test_property_interaction_fields():
    """Test interaction tracking fields."""
    prop = Property(
        id=200,
        region="VENETO",
        province="VE",
        category="Residenziale",
        price=300000,
        favorite=1,
        viewed=1,
        hidden=0,
        notes="Great location!",
        discription="Test",
        discription_dk="Test",
        photo_list="[]",
    )

    assert prop.favorite == 1
    assert prop.viewed == 1
    assert prop.hidden == 0
    assert prop.notes == "Great location!"


def test_property_optional_fields():
    """Test that optional fields can be None."""
    prop = Property(
        id=300,
        region="LAZIO",
        province="RM",
        category="Residenziale",
        price=400000,
        city=None,
        bathrooms=None,
        rooms=None,
        surface=None,
        latitude=None,
        longitude=None,
        discription="Test",
        discription_dk="Test",
        photo_list="[]",
    )

    assert prop.city is None
    assert prop.bathrooms is None
    assert prop.rooms is None
    assert prop.surface is None
    assert prop.latitude is None
    assert prop.longitude is None


def test_property_database_insert(db_session, sample_property):
    """Test inserting Property into database."""
    db_session.add(sample_property)
    db_session.commit()

    # Retrieve and verify
    retrieved = db_session.get(Property, sample_property.id)
    assert retrieved is not None
    assert retrieved.id == sample_property.id
    assert retrieved.region == sample_property.region
    assert retrieved.price == sample_property.price


def test_property_database_update(db_session, sample_property):
    """Test updating Property in database."""
    db_session.add(sample_property)
    db_session.commit()

    # Update review status
    sample_property.review_status = "Interested"
    sample_property.reviewed_date = "2026-02-13T19:00:00"
    db_session.commit()

    # Retrieve and verify
    retrieved = db_session.get(Property, sample_property.id)
    assert retrieved.review_status == "Interested"
    assert retrieved.reviewed_date == "2026-02-13T19:00:00"


def test_property_database_delete(db_session, sample_property):
    """Test deleting Property from database."""
    db_session.add(sample_property)
    db_session.commit()

    # Delete
    db_session.delete(sample_property)
    db_session.commit()

    # Verify deletion
    retrieved = db_session.get(Property, sample_property.id)
    assert retrieved is None


def test_property_model_dump(sample_property):
    """Test Property model serialization."""
    data = sample_property.model_dump()

    assert isinstance(data, dict)
    assert data["id"] == 12345
    assert data["region"] == "TUSCANY"
    assert data["review_status"] == "To Review"


def test_property_with_sold_flag():
    """Test Property with sold flag set."""
    prop = Property(
        id=400,
        region="SICILY",
        province="PA",
        category="Residenziale",
        price=150000,
        sold=1,  # Marked as sold
        discription="Sold property",
        discription_dk="Solgt ejendom",
        photo_list="[]",
    )

    assert prop.sold == 1
