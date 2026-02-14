"""Property Review Dashboard - Main Page

Streamlit app for reviewing and managing Italian property listings.
Provides visual overview of review progress and quick action buttons.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlmodel import Session, create_engine, select

from property_tracker.config.settings import get_database_url
from property_tracker.models.property import Property
from property_tracker.services.review import ReviewService

# ================ CONFIGURATION ================
PAGE_TITLE = "Property Review Dashboard"
PAGE_ICON = "🏠"
PROPERTIES_PER_PAGE = 20

# ================ PAGE SETUP ================
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# ================ DATABASE CONNECTION ================
@st.cache_resource
def get_engine():
    """Create and cache database engine."""
    return create_engine(get_database_url())

engine = get_engine()

# ================ DATA LOADING ================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_properties_df(status_filter=None, region_filter=None):
    """Load properties as DataFrame with optional filters.

    Uses SQLModel's safe query builder to prevent SQL injection.
    """
    with Session(engine) as session:
        # Build query using SQLModel (safe from SQL injection)
        statement = select(Property).where(Property.sold == 0)

        if status_filter and status_filter != "All":
            statement = statement.where(Property.review_status == status_filter)

        if region_filter and region_filter != "All":
            statement = statement.where(Property.region == region_filter)

        # Execute query and convert to DataFrame
        properties = session.exec(statement).all()

        if len(properties) == 0:
            # Return empty DataFrame with proper column structure
            return pd.DataFrame(columns=['id', 'region', 'price', 'price_m', 'rooms',
                                        'bathrooms', 'surface', 'latitude', 'longitude',
                                        'dist_coast', 'dist_water', 'review_status',
                                        'reviewed_date', 'photo_list', 'discription'])

        df = pd.DataFrame([prop.model_dump() for prop in properties])

        # Convert numeric columns
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['dist_coast'] = pd.to_numeric(df['dist_coast'], errors='coerce')
        df['dist_water'] = pd.to_numeric(df['dist_water'], errors='coerce')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['price_m'] = pd.to_numeric(df['price_m'], errors='coerce')

        return df

def get_review_counts():
    """Get review status counts."""
    with Session(engine) as session:
        service = ReviewService(session)
        return service.get_status_counts()

# ================ MAIN APP ================
def main():
    st.title(f"{PAGE_ICON} Property Review Dashboard")
    st.markdown("---")

    # === SECTION 1: COUNT CARDS ===
    st.subheader("📊 Review Progress")
    counts = get_review_counts()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total = sum(counts.values())
        st.metric("Total Properties", total)

    with col2:
        to_review = counts.get("To Review", 0)
        st.metric("To Review", to_review, delta=None, delta_color="off")

    with col3:
        interested = counts.get("Interested", 0)
        st.metric("Interested ✅", interested, delta=None, delta_color="normal")

    with col4:
        rejected = counts.get("Rejected", 0)
        st.metric("Rejected ❌", rejected, delta=None, delta_color="inverse")

    st.markdown("---")

    # === SECTION 2: PROGRESS VISUALIZATION ===
    st.subheader("📈 Status Distribution")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Bar chart
        fig_bar = go.Figure(data=[
            go.Bar(
                x=["To Review", "Interested", "Rejected"],
                y=[counts.get("To Review", 0), counts.get("Interested", 0), counts.get("Rejected", 0)],
                marker_color=['#FFA500', '#4CAF50', '#F44336'],
                text=[counts.get("To Review", 0), counts.get("Interested", 0), counts.get("Rejected", 0)],
                textposition='auto',
            )
        ])
        fig_bar.update_layout(
            title="Review Status Counts",
            xaxis_title="Status",
            yaxis_title="Number of Properties",
            height=350
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        # Pie chart
        fig_pie = px.pie(
            values=[counts.get("To Review", 0), counts.get("Interested", 0), counts.get("Rejected", 0)],
            names=["To Review", "Interested", "Rejected"],
            color_discrete_sequence=['#FFA500', '#4CAF50', '#F44336'],
            hole=0.4
        )
        fig_pie.update_layout(
            title="Review Status Breakdown",
            height=350
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # === SECTION 3: FILTERS ===
    st.subheader("🔍 Filter Properties")

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        status_filter = st.selectbox(
            "Review Status",
            ["All", "To Review", "Interested", "Rejected"],
            index=1  # Default to "To Review"
        )

    with col_f2:
        # Load unique regions
        df_temp = load_properties_df()
        regions = ["All"] + sorted(df_temp['region'].unique().tolist())
        region_filter = st.selectbox("Region", regions)

    st.markdown("---")

    # === SECTION 4: PROPERTY TABLE ===
    df = load_properties_df(status_filter, region_filter)

    st.subheader(f"🏘️ Properties ({len(df)} found)")

    if len(df) == 0:
        st.info("No properties match your filters.")
        return

    # Store in session state for other pages
    st.session_state["df"] = df

    # Tabs for different views
    tab1, tab2 = st.tabs(["⚡ Quick Actions", "📋 Detailed View"])

    with tab1:
        render_quick_actions(df)

    with tab2:
        render_detailed_view(df)

# ================ QUICK ACTIONS TAB ================
def render_quick_actions(df):
    """Render quick action buttons for property review."""
    # Show only To Review properties, limit to first 20
    to_review_df = df[df['review_status'] == 'To Review'].head(PROPERTIES_PER_PAGE)

    if len(to_review_df) == 0:
        st.info("No properties to review! All caught up 🎉")
        return

    st.markdown(f"Showing {len(to_review_df)} properties ready for review")

    for _idx, row in to_review_df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([1, 3, 1.2, 1.2, 1])

        with col1:
            st.markdown(f"**{row['id']}**")

        with col2:
            price_str = f"€{int(row['price']):,}" if pd.notna(row['price']) else "N/A"
            rooms_str = f"{row['rooms']} rooms" if pd.notna(row['rooms']) else ""
            st.markdown(f"📍 **{row['region']}** | {price_str} | {rooms_str}")
            if pd.notna(row['dist_coast']):
                st.caption(f"🏖️ Coast: {row['dist_coast']:.1f} km")

        with col3:
            if st.button("✅ Interested", key=f"int_{row['id']}", use_container_width=True):
                update_property_status(int(row['id']), "Interested")

        with col4:
            if st.button("❌ Reject", key=f"rej_{row['id']}", use_container_width=True):
                update_property_status(int(row['id']), "Rejected")

        with col5:
            property_url = f"https://www.immobiliare.it/annunci/{row['id']}"
            st.link_button("🔗 View", property_url, use_container_width=True)

        st.divider()

# ================ DETAILED VIEW TAB ================
def render_detailed_view(df):
    """Render detailed dataframe view."""
    # Select and format columns for display
    display_df = df[[
        'id', 'region', 'price', 'price_m', 'rooms', 'bathrooms',
        'surface', 'dist_coast', 'review_status', 'reviewed_date'
    ]].copy()

    # Create property URL column
    display_df['property_url'] = display_df['id'].apply(
        lambda x: f'https://www.immobiliare.it/annunci/{x}'
    )

    # Display with custom column configuration
    st.dataframe(
        display_df,
        column_config={
            "id": st.column_config.NumberColumn("ID", format="%d"),
            "region": "Region",
            "price": st.column_config.NumberColumn("Price", format="€%d"),
            "price_m": st.column_config.NumberColumn("Price/m²", format="€%d"),
            "rooms": "Rooms",
            "bathrooms": "Bathrooms",
            "surface": "Surface",
            "dist_coast": st.column_config.NumberColumn("Coast (km)", format="%.1f"),
            "review_status": st.column_config.SelectboxColumn(
                "Status",
                options=["To Review", "Interested", "Rejected"]
            ),
            "reviewed_date": "Reviewed",
            "property_url": st.column_config.LinkColumn("View Property")
        },
        use_container_width=True,
        hide_index=True,
        height=600
    )

# ================ HELPER FUNCTIONS ================
def update_property_status(property_id: int, new_status: str):
    """Update property review status and refresh UI."""
    try:
        with Session(engine) as session:
            service = ReviewService(session)
            success = service.update_status(property_id, new_status)

            if success:
                st.success(f"Property {property_id} marked as {new_status}!")
                # Clear cache to force data reload
                st.cache_data.clear()
                # Rerun to refresh UI
                st.rerun()
            else:
                st.error(f"Failed to update property {property_id}")
    except Exception as e:
        st.error(f"Error updating property: {e}")

# ================ RUN APP ================
if __name__ == "__main__":
    main()
