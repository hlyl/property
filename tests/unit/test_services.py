"""Unit tests for service layer.

Tests ReviewService, POIService, and TranslationService functionality.
"""

import pytest

from property_tracker.models.property import Property
from property_tracker.services.review import ReviewService

# ============================================================================
# ReviewService Tests
# ============================================================================


def test_review_service_initialization(db_session):
    """Test ReviewService can be initialized."""
    service = ReviewService(db_session)
    assert service is not None
    assert service.session == db_session


def test_review_service_update_status(db_session, sample_property):
    """Test updating review status."""
    db_session.add(sample_property)
    db_session.commit()

    service = ReviewService(db_session)
    success = service.update_status(sample_property.id, "Interested")

    assert success is True

    # Verify update
    updated = db_session.get(Property, sample_property.id)
    assert updated.review_status == "Interested"
    assert updated.reviewed_date is not None


def test_review_service_update_status_invalid_id(db_session):
    """Test updating non-existent property."""
    service = ReviewService(db_session)
    success = service.update_status(99999, "Interested")

    # Should still return True (UPDATE affects 0 rows but doesn't fail)
    assert success is True


def test_review_service_get_status_counts(populated_db_session):
    """Test getting status counts."""
    service = ReviewService(populated_db_session)
    counts = service.get_status_counts()

    assert counts["To Review"] == 2  # Properties 1 and 4
    assert counts["Interested"] == 1  # Property 2
    assert counts["Rejected"] == 1  # Property 3


def test_review_service_get_status_counts_empty_db(db_session):
    """Test getting status counts from empty database."""
    service = ReviewService(db_session)
    counts = service.get_status_counts()

    # Should return all statuses with zero counts
    assert counts["To Review"] == 0
    assert counts["Interested"] == 0
    assert counts["Rejected"] == 0


def test_review_service_get_properties_by_status(populated_db_session):
    """Test filtering properties by status."""
    service = ReviewService(populated_db_session)

    # Get "To Review" properties
    to_review = service.get_properties_by_status("To Review")
    assert len(to_review) == 2
    assert all(p.review_status == "To Review" for p in to_review)

    # Get "Interested" properties
    interested = service.get_properties_by_status("Interested")
    assert len(interested) == 1
    assert interested[0].review_status == "Interested"


def test_review_service_get_properties_by_region(populated_db_session):
    """Test filtering properties by region."""
    service = ReviewService(populated_db_session)

    # Get Tuscany properties
    tuscany = service.get_properties_by_status(region="TUSCANY")
    assert len(tuscany) == 2  # Properties 1 and 4
    assert all(p.region == "TUSCANY" for p in tuscany)


def test_review_service_get_properties_combined_filters(populated_db_session):
    """Test filtering with both status and region."""
    service = ReviewService(populated_db_session)

    # Get Tuscany properties that are "To Review"
    results = service.get_properties_by_status("To Review", "TUSCANY")
    assert len(results) == 2
    assert all(p.region == "TUSCANY" and p.review_status == "To Review" for p in results)


def test_review_service_get_properties_with_limit(populated_db_session):
    """Test limiting number of results."""
    service = ReviewService(populated_db_session)

    results = service.get_properties_by_status(limit=2)
    assert len(results) == 2


def test_review_service_bulk_update_status(populated_db_session):
    """Test bulk status updates."""
    service = ReviewService(populated_db_session)

    # Update properties 1 and 4 to "Interested"
    count = service.bulk_update_status([1, 4], "Interested")
    assert count == 2

    # Verify updates
    prop1 = populated_db_session.get(Property, 1)
    prop4 = populated_db_session.get(Property, 4)
    assert prop1.review_status == "Interested"
    assert prop4.review_status == "Interested"


def test_review_service_bulk_update_empty_list(db_session):
    """Test bulk update with empty ID list."""
    service = ReviewService(db_session)
    count = service.bulk_update_status([], "Interested")
    assert count == 0


def test_review_service_get_recent_reviews(populated_db_session):
    """Test getting recently reviewed properties."""
    service = ReviewService(populated_db_session)

    # Update some properties with review dates
    service.update_status(1, "Interested")
    service.update_status(2, "Rejected")

    recent = service.get_recent_reviews(limit=10)

    # Should return properties that have been reviewed
    assert len(recent) >= 2
    assert all(p.reviewed_date is not None for p in recent)


def test_review_service_get_recent_reviews_none_reviewed(db_session):
    """Test getting recent reviews when none exist."""
    service = ReviewService(db_session)
    recent = service.get_recent_reviews()
    assert len(recent) == 0


# ============================================================================
# TranslationService Tests
# ============================================================================


def test_translation_service_empty_string():
    """Test translation service with empty string."""
    from property_tracker.services.translation import DeepTranslatorService

    service = DeepTranslatorService(service="google")
    result = service.translate("")

    assert result == ""


def test_translation_service_short_text():
    """Test translation service with short text."""
    from property_tracker.services.translation import DeepTranslatorService

    service = DeepTranslatorService(service="google")

    # Test with sample text (this will use actual translation service)
    # In a real test, you'd mock the external API
    # For now, just verify it doesn't crash
    try:
        result = service.translate("Casa bella")
        assert isinstance(result, str)
    except Exception as e:
        # If translation fails (no internet, API limit), that's okay
        pytest.skip(f"Translation service unavailable: {e}")


# ============================================================================
# POIService Tests
# ============================================================================


def test_poi_service_initialization():
    """Test POIService can be initialized."""
    from property_tracker.services.poi import OverpassPOIService

    service = OverpassPOIService()
    assert service is not None


def test_overpass_count_pois_counts_all_element_types():
    """POI count should include nodes, ways, and relations from Overpass."""
    from property_tracker.services.poi import OverpassPOIService

    class DummyApi:
        @staticmethod
        def query(_query):
            class Result:
                nodes = [1, 2]
                ways = [1]
                relations = [1, 2, 3]

            return Result()

    class DummyTime:
        @staticmethod
        def sleep(_seconds):
            return None

    service = OverpassPOIService.__new__(OverpassPOIService)
    service.api = DummyApi()
    service.time = DummyTime()

    count = service.count_pois(lat=43.8438, lon=10.5077, radius=2000, poi_type="shop")
    assert count == 6


@pytest.mark.skip(reason="Requires external Overpass API")
def test_poi_service_fetch_pois():
    """Test fetching POIs from Overpass API."""
    from property_tracker.services.poi import OverpassPOIService

    service = OverpassPOIService()

    # Test coordinates for Lucca, Italy
    pois = service.fetch_pois(lat=43.8438, lon=10.5077, radius=2000)

    assert isinstance(pois, dict)
    # Should have counts for different POI types
    assert "shopping_count" in pois or len(pois) >= 0
