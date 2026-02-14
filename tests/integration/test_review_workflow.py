"""Integration tests for review workflow.

Tests complete review workflow including database operations,
status updates, and multi-step processes.
"""

import pytest
from sqlmodel import select
from property_tracker.models.property import Property
from property_tracker.services.review import ReviewService
from property_tracker.database.connection import get_session


def test_full_review_workflow(db_engine):
    """Test complete review workflow from creation to status changes."""
    # Create property
    with get_session(use_test_db=True) as session:
        prop = Property(
            id=777,
            region="Tuscany",
            province="LU",
            category="Residenziale",
            price=200000,
            review_status="To Review",
            sold=0,
            discription="Integration test property",
            discription_dk="Integration test ejendom",
            photo_list="[]"
        )
        session.add(prop)
        session.commit()

    # Review it (mark as Interested)
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        success = service.update_status(777, "Interested")
        assert success

    # Verify status changed
    with get_session(use_test_db=True) as session:
        prop = session.get(Property, 777)
        assert prop.review_status == "Interested"
        assert prop.reviewed_date is not None

    # Change to Rejected
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        service.update_status(777, "Rejected")

    # Verify final status
    with get_session(use_test_db=True) as session:
        prop = session.get(Property, 777)
        assert prop.review_status == "Rejected"


def test_bulk_review_operations(db_engine):
    """Test bulk status updates with multiple properties."""
    # Create 10 properties
    with get_session(use_test_db=True) as session:
        props = [
            Property(
                id=i,
                region=f"REGION_{i}",
                province="TS",
                category="Residenziale",
                price=100000 * i,
                sold=0,
                discription=f"Property {i}",
                discription_dk=f"Ejendom {i}",
                photo_list="[]"
            )
            for i in range(1, 11)
        ]
        session.add_all(props)
        session.commit()

    # Bulk update first 5 to "Interested"
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        count = service.bulk_update_status([1, 2, 3, 4, 5], "Interested")
        assert count == 5

    # Verify updates
    with get_session(use_test_db=True) as session:
        interested = session.exec(
            select(Property).where(Property.review_status == "Interested")
        ).all()
        assert len(interested) == 5

        # Verify specific IDs
        interested_ids = {p.id for p in interested}
        assert interested_ids == {1, 2, 3, 4, 5}


def test_review_status_counts_workflow(db_engine):
    """Test status count tracking through workflow."""
    # Create properties with different statuses
    with get_session(use_test_db=True) as session:
        props = [
            Property(id=100, region="A", province="A", category="R", price=100, review_status="To Review", sold=0, discription="A", discription_dk="A", photo_list="[]"),
            Property(id=101, region="B", province="B", category="R", price=200, review_status="To Review", sold=0, discription="B", discription_dk="B", photo_list="[]"),
            Property(id=102, region="C", province="C", category="R", price=300, review_status="Interested", sold=0, discription="C", discription_dk="C", photo_list="[]"),
        ]
        session.add_all(props)
        session.commit()

    # Check initial counts
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        counts = service.get_status_counts()
        assert counts["To Review"] == 2
        assert counts["Interested"] == 1
        assert counts["Rejected"] == 0

    # Update one property
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        service.update_status(100, "Rejected")

    # Check updated counts
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        counts = service.get_status_counts()
        assert counts["To Review"] == 1
        assert counts["Interested"] == 1
        assert counts["Rejected"] == 1


def test_review_filtering_workflow(db_engine):
    """Test filtering properties through review workflow."""
    # Create diverse property set
    with get_session(use_test_db=True) as session:
        props = [
            Property(id=200, region="TUSCANY", province="LU", category="R", price=250000, review_status="To Review", sold=0, discription="T1", discription_dk="T1", photo_list="[]"),
            Property(id=201, region="TUSCANY", province="FI", category="R", price=350000, review_status="Interested", sold=0, discription="T2", discription_dk="T2", photo_list="[]"),
            Property(id=202, region="LOMBARDY", province="MI", category="R", price=450000, review_status="To Review", sold=0, discription="L1", discription_dk="L1", photo_list="[]"),
            Property(id=203, region="LOMBARDY", province="BG", category="R", price=200000, review_status="Rejected", sold=0, discription="L2", discription_dk="L2", photo_list="[]"),
        ]
        session.add_all(props)
        session.commit()

    # Filter by region
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        tuscany = service.get_properties_by_status(region="TUSCANY")
        assert len(tuscany) == 2
        assert all(p.region == "TUSCANY" for p in tuscany)

    # Filter by status
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        to_review = service.get_properties_by_status("To Review")
        assert len(to_review) == 2

    # Filter by both
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        tuscany_to_review = service.get_properties_by_status("To Review", "TUSCANY")
        assert len(tuscany_to_review) == 1
        assert tuscany_to_review[0].id == 200


def test_recent_reviews_workflow(db_engine):
    """Test tracking recently reviewed properties."""
    # Create and review properties over time
    with get_session(use_test_db=True) as session:
        props = [
            Property(id=300 + i, region=f"R{i}", province="TS", category="R", price=100000, sold=0, discription=f"P{i}", discription_dk=f"P{i}", photo_list="[]")
            for i in range(5)
        ]
        session.add_all(props)
        session.commit()

    # Review them one by one
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        service.update_status(300, "Interested")
        service.update_status(301, "Rejected")
        service.update_status(302, "Interested")

    # Get recent reviews
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        recent = service.get_recent_reviews(limit=10)

        # Should have 3 reviewed properties
        assert len(recent) == 3

        # All should have review dates
        assert all(p.reviewed_date is not None for p in recent)

        # Should contain the reviewed IDs
        reviewed_ids = {p.id for p in recent}
        assert {300, 301, 302}.issubset(reviewed_ids)


def test_pagination_workflow(db_engine):
    """Test pagination in property listings."""
    # Create many properties
    with get_session(use_test_db=True) as session:
        props = [
            Property(
                id=400 + i,
                region="TEST",
                province="TS",
                category="R",
                price=100000 + i * 10000,
                review_status="To Review",
                sold=0,
                discription=f"Prop {i}",
                discription_dk=f"Ejendom {i}",
                photo_list="[]"
            )
            for i in range(50)
        ]
        session.add_all(props)
        session.commit()

    # Test pagination with limit
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)

        page1 = service.get_properties_by_status("To Review", limit=20)
        assert len(page1) == 20

        page2 = service.get_properties_by_status("To Review", limit=10)
        assert len(page2) == 10


def test_property_lifecycle_integration(db_engine):
    """Test complete property lifecycle: create, review, update, query."""
    prop_id = 500

    # Create
    with get_session(use_test_db=True) as session:
        prop = Property(
            id=prop_id,
            region="LIFECYCLE_TEST",
            province="LT",
            category="Residenziale",
            price=300000,
            sold=0,
            review_status="To Review",
            favorite=0,
            viewed=0,
            discription="Lifecycle test",
            discription_dk="Livscyklus test",
            photo_list="[]"
        )
        session.add(prop)

    # Mark as viewed
    with get_session(use_test_db=True) as session:
        prop = session.get(Property, prop_id)
        prop.viewed = 1
        session.commit()

    # Mark as favorite
    with get_session(use_test_db=True) as session:
        prop = session.get(Property, prop_id)
        prop.favorite = 1
        session.commit()

    # Review as interested
    with get_session(use_test_db=True) as session:
        service = ReviewService(session)
        service.update_status(prop_id, "Interested")

    # Add notes
    with get_session(use_test_db=True) as session:
        prop = session.get(Property, prop_id)
        prop.notes = "Great location, good price!"
        session.commit()

    # Final verification
    with get_session(use_test_db=True) as session:
        prop = session.get(Property, prop_id)
        assert prop.review_status == "Interested"
        assert prop.favorite == 1
        assert prop.viewed == 1
        assert prop.notes == "Great location, good price!"
        assert prop.reviewed_date is not None
