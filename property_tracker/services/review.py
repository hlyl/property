"""Service layer for property review operations.

Provides business logic for managing property review status,
separate from database and UI concerns.
"""

from datetime import datetime

from sqlmodel import Session, func, select, update

from property_tracker.models.property import Property


class ReviewService:
    """Handles all review-related business logic."""

    def __init__(self, session: Session):
        """Initialize the review service.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def update_status(self, property_id: int, new_status: str) -> bool:
        """Update review status for a property.

        Args:
            property_id: ID of the property to update
            new_status: New status ("To Review", "Rejected", or "Interested")

        Returns:
            True if update successful, False otherwise
        """
        try:
            statement = (
                update(Property)
                .values(
                    review_status=new_status,
                    reviewed_date=datetime.now().isoformat()
                )
                .where(Property.id == property_id)
            )
            self.session.execute(statement)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error updating property {property_id}: {e}")
            self.session.rollback()
            return False

    def get_status_counts(self) -> dict[str, int]:
        """Get counts for each review status.

        Returns:
            Dictionary mapping status names to counts
            e.g., {"To Review": 1000, "Interested": 5, "Rejected": 2}
        """
        statement = select(
            Property.review_status,
            func.count(Property.id).label('count')
        ).where(Property.sold == 0).group_by(Property.review_status)

        results = self.session.exec(statement).all()
        counts = {status: count for status, count in results}

        # Ensure all statuses are present, even if count is 0
        for status in ["To Review", "Interested", "Rejected"]:
            if status not in counts:
                counts[status] = 0

        return counts

    def get_properties_by_status(
        self,
        status: str | None = None,
        region: str | None = None,
        limit: int | None = None
    ) -> list[Property]:
        """Get properties filtered by review status and region.

        Args:
            status: Filter by review status (None or "All" for all properties)
            region: Filter by region (None or "All" for all regions)
            limit: Maximum number of properties to return

        Returns:
            List of Property objects matching the filters
        """
        statement = select(Property).where(Property.sold == 0)

        if status and status != "All":
            statement = statement.where(Property.review_status == status)

        if region and region != "All":
            statement = statement.where(Property.region == region)

        if limit:
            statement = statement.limit(limit)

        return self.session.exec(statement).all()

    def bulk_update_status(self, property_ids: list[int], new_status: str) -> int:
        """Bulk update multiple properties to the same status.

        Args:
            property_ids: List of property IDs to update
            new_status: New status to apply to all properties

        Returns:
            Number of properties updated
        """
        try:
            statement = (
                update(Property)
                .values(
                    review_status=new_status,
                    reviewed_date=datetime.now().isoformat()
                )
                .where(Property.id.in_(property_ids))
            )
            result = self.session.execute(statement)
            self.session.commit()
            return result.rowcount
        except Exception as e:
            print(f"Error bulk updating properties: {e}")
            self.session.rollback()
            return 0

    def get_recent_reviews(self, limit: int = 10) -> list[Property]:
        """Get recently reviewed properties.

        Args:
            limit: Maximum number of properties to return

        Returns:
            List of recently reviewed properties, newest first
        """
        statement = (
            select(Property)
            .where(Property.sold == 0)
            .where(Property.reviewed_date.is_not(None))
            .order_by(Property.reviewed_date.desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()
