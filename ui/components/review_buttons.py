"""Reusable review action buttons component.

Provides standardized review buttons for property review operations
across all Streamlit pages.
"""

import streamlit as st
from sqlmodel import Session, create_engine

from property_tracker.config.settings import get_database_url
from property_tracker.services.review import ReviewService


def render_review_buttons(property_id: int, current_status: str, key_prefix: str = "", use_container_width: bool = True) -> None:
    """Render review action buttons for a property.

    Creates a three-column layout with Interested, Reject, and Reset buttons.
    Automatically handles status updates and UI refresh.

    Args:
        property_id: ID of the property to review
        current_status: Current review status of the property
        key_prefix: Prefix for button keys to ensure uniqueness
        use_container_width: Whether buttons should fill container width

    Example:
        ```python
        render_review_buttons(
            property_id=12345,
            current_status="To Review",
            key_prefix="map"
        )
        ```
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Mark as Interested", key=f"{key_prefix}_int_{property_id}", use_container_width=use_container_width):
            _update_status(property_id, "Interested")

    with col2:
        if st.button("❌ Reject", key=f"{key_prefix}_rej_{property_id}", use_container_width=use_container_width):
            _update_status(property_id, "Rejected")

    with col3:
        if current_status != "To Review":
            if st.button("🔄 Reset to Review", key=f"{key_prefix}_reset_{property_id}", use_container_width=use_container_width):
                _update_status(property_id, "To Review")
        else:
            # Placeholder to maintain layout
            st.empty()


def _update_status(property_id: int, new_status: str) -> None:
    """Update property status and refresh UI.

    Internal helper function that handles the database update and
    triggers UI refresh.

    Args:
        property_id: ID of the property to update
        new_status: New review status
    """
    try:
        # Create engine and session
        engine = create_engine(get_database_url())

        with Session(engine) as session:
            service = ReviewService(session)
            success = service.update_status(property_id, new_status)

            if success:
                st.success(f"Property {property_id} marked as {new_status}!")

                # Clear cache to force data reload
                st.cache_data.clear()

                # Clear session state DataFrame if it exists
                if "df" in st.session_state:
                    del st.session_state["df"]

                # Rerun to refresh UI
                st.rerun()
            else:
                st.error(f"Failed to update property {property_id}")

    except Exception as e:
        st.error(f"Error updating property: {e}")


def render_status_badge(status: str) -> None:
    """Render a colored status badge.

    Args:
        status: Review status to display
    """
    status_colors = {"To Review": "🟠", "Interested": "🟢", "Rejected": "🔴"}

    emoji = status_colors.get(status, "⚪")
    st.markdown(f"{emoji} **{status}**")
