"""
Interactive Property Map with Click Selection
Uses native Streamlit Plotly selection (Streamlit 1.35+)
No external dependencies like streamlit-plotly-events needed!
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlmodel import create_engine, Session
from property_tracker.config.settings import get_database_url
from property_tracker.services.review import ReviewService
import json

st.set_page_config(page_title="Property Map", page_icon="🗺️", layout="wide")


def update_property_status(property_id: int, new_status: str):
    """Update property review status and refresh the UI."""
    engine = create_engine(get_database_url())
    with Session(engine) as session:
        service = ReviewService(session)
        success = service.update_status(property_id, new_status)
        if success:
            st.success(f"Property {property_id} marked as {new_status}!")
            # Clear session state to force reload from database
            if "df" in st.session_state:
                del st.session_state["df"]
            st.rerun()
        else:
            st.error(f"Failed to update property {property_id}")


def _max_width_():
    max_width_str = "max-width: 1800px"
    st.markdown(
        f"""
        <style>
        .reportview-container .main .block-container{{
            {max_width_str}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def map_plot(df):
    """Create interactive plotly map with markers"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate center of Italy for initial view
    center_lat = df["latitude"].mean() if len(df) > 0 else 42.5
    center_lon = df["longitude"].mean() if len(df) > 0 else 12.5

    fig = px.scatter_map(
        df,
        lat="latitude",
        lon="longitude",
        color="price",
        hover_name="caption",
        hover_data={
            "price": ":,.0f",
            "price_m": ":,.0f",
            "rooms": True,
            "bathrooms": True,
            "surface": True,
            "region": True,
            "id": True,
            "latitude": False,
            "longitude": False,
        },
        color_continuous_scale=px.colors.cyclical.IceFire,
        zoom=5,
        height=700,
        size_max=15,
    )

    fig.update_layout(
        map_style="open-street-map",
        title_text=f"Property Overview - {now}",
        title_x=0.5,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        map=dict(
            center=dict(lat=center_lat, lon=center_lon),
            zoom=5
        ),
    )

    # Make markers more visible
    fig.update_traces(
        marker=dict(size=12, opacity=0.8),
        selector=dict(mode="markers"),
    )

    return fig


_max_width_()
st.title("🏡 Property Explorer")

# Load data
if "df" not in st.session_state:
    engine = create_engine(get_database_url())
    with Session(engine) as session:
        query = "SELECT * FROM property WHERE sold = 0"
        df = pd.read_sql(query, con=session.connection())
        st.session_state["df"] = df
else:
    df = st.session_state["df"]

# Data preprocessing
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["price_m"] = pd.to_numeric(df["price_m"], errors="coerce")

# Filter properties with valid coordinates
lat_lon = df.dropna(subset=["longitude", "latitude"]).copy()
# Reset index to ensure point indices match dataframe indices
lat_lon = lat_lon.reset_index(drop=True)
num_rows = len(lat_lon)

# Debug info
st.write(f"📊 Total properties loaded: **{len(df)}**")
st.write(f"🗺️ Properties with coordinates: **{num_rows}**")

if num_rows == 0:
    st.error("No properties with valid coordinates found. Please check the database.")
    st.stop()

# Show coordinate ranges for debugging
with st.expander("🔍 Debug Info"):
    st.write(f"Latitude range: {lat_lon['latitude'].min():.4f} to {lat_lon['latitude'].max():.4f}")
    st.write(f"Longitude range: {lat_lon['longitude'].min():.4f} to {lat_lon['longitude'].max():.4f}")
    st.write(f"Price range: €{lat_lon['price'].min():,.0f} to €{lat_lon['price'].max():,.0f}")
    st.dataframe(lat_lon[["id", "caption", "latitude", "longitude", "price"]].head(10))

st.write(f"Click on any of the **{num_rows}** markers to view property details")
st.markdown("---")

# Create map
fig = map_plot(lat_lon)

# Display map with NATIVE Streamlit selection (works in 1.35+)
st.subheader("🗺️ Interactive Property Map")

# Use native Plotly selection - this is the key fix!
event = st.plotly_chart(
    fig,
    on_select="rerun",
    selection_mode="points",
    key="property_map",
    use_container_width=True,
)

# Handle selection from native Plotly events
selected_point_index = None

if event and event.selection and event.selection.point_indices:
    selected_point_index = event.selection.point_indices[0]

# Alternative: also check session state for persistence
if selected_point_index is not None:
    st.session_state["selected_property_index"] = selected_point_index
elif "selected_property_index" in st.session_state:
    selected_point_index = st.session_state["selected_property_index"]

# Display selected property details
if selected_point_index is not None and selected_point_index < len(lat_lon):
    selected = lat_lon.iloc[selected_point_index]
    
    st.divider()
    st.subheader(f"🏠 {selected['caption']}")
    
    # Property details
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Price", f"€{selected['price']:,.0f}")
        st.metric("Price/m²", f"€{selected['price_m']:,.0f}")
    
    with col2:
        st.metric("Rooms", selected['rooms'])
        st.metric("Bathrooms", selected['bathrooms'])
    
    with col3:
        st.metric("Surface", selected['surface'])
        st.metric("Region", selected['region'])
    
    # Description
    if selected.get('discription'):
        with st.expander("📝 Description"):
            st.write(selected['discription'])
    
    # Photos
    if selected.get('photo_list'):
        try:
            photos = json.loads(selected['photo_list'])
            if photos:
                with st.expander("📸 Photos", expanded=True):
                    cols = st.columns(min(len(photos), 4))
                    for i, photo in enumerate(photos[:4]):
                        with cols[i]:
                            st.image(photo, use_container_width=True)
        except:
            pass
    
    # Link
    st.markdown(f"🔗 [View on Immobiliare.it](https://www.immobiliare.it/en/annunci/{selected['id']}/)")

    # Review Status and Action Buttons
    st.divider()
    current_status = selected.get('review_status', 'To Review')
    st.write(f"**Review Status:** {current_status}")

    st.markdown("### Quick Actions")
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("✅ Mark as Interested", key=f"int_map_{selected['id']}", use_container_width=True):
            update_property_status(int(selected['id']), "Interested")

    with col_btn2:
        if st.button("❌ Reject", key=f"rej_map_{selected['id']}", use_container_width=True):
            update_property_status(int(selected['id']), "Rejected")

    with col_btn3:
        if current_status != "To Review":
            if st.button("🔄 Reset to Review", key=f"reset_map_{selected['id']}", use_container_width=True):
                update_property_status(int(selected['id']), "To Review")