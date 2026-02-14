# noqa: N999
"""
Interactive Property Map with Clickable Markers
Uses Folium for truly clickable markers that open property links
"""

import folium
import pandas as pd
import streamlit as st
from sqlmodel import Session, create_engine
from streamlit_folium import st_folium

from property_tracker.config.settings import get_database_url
from property_tracker.services.review import ReviewService

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


def create_folium_map(df):
    """Create interactive Folium map with clickable markers that open property links"""
    # Calculate center of Italy for initial view
    center_lat = df["latitude"].mean() if len(df) > 0 else 42.5
    center_lon = df["longitude"].mean() if len(df) > 0 else 12.5

    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles="OpenStreetMap"
    )

    # Add markers for each property
    for _idx, row in df.iterrows():
        # Determine marker color based on price
        price = row.get('price', 0)
        if price < 50000:
            color = 'green'
        elif price < 75000:
            color = 'blue'
        elif price < 100000:
            color = 'orange'
        else:
            color = 'red'

        # Create popup HTML with clickable link
        property_url = f"https://www.immobiliare.it/en/annunci/{row['id']}/"
        popup_html = f"""
        <div style="font-family: Arial; min-width: 250px; max-width: 300px;">
            <h4 style="margin-bottom: 10px;">{row.get('caption', 'Property')}</h4>
            <table style="width: 100%; font-size: 12px;">
                <tr><td><b>💰 Price:</b></td><td>€{int(row['price']):,}</td></tr>
                <tr><td><b>📏 Price/m²:</b></td><td>€{int(row.get('price_m', 0)):,}</td></tr>
                <tr><td><b>🛏️ Rooms:</b></td><td>{row.get('rooms', 'N/A')}</td></tr>
                <tr><td><b>🚿 Bathrooms:</b></td><td>{row.get('bathrooms', 'N/A')}</td></tr>
                <tr><td><b>📐 Surface:</b></td><td>{row.get('surface', 'N/A')}</td></tr>
                <tr><td><b>📍 Region:</b></td><td>{row.get('region', 'N/A')}</td></tr>
            </table>
            <div style="margin-top: 10px; text-align: center;">
                <a href="{property_url}" target="_blank"
                   style="background-color: #4CAF50; color: white; padding: 8px 16px;
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    🔗 Open Property
                </a>
            </div>
        </div>
        """

        # Add marker to map
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=8,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row.get('caption', 'Property')} - €{int(row['price']):,}",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)

    return m


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

st.write("**How to use:** Click on any marker to see a popup with property details and a clickable 'Open Property' button.")
st.write("**Color coding:** 🟢 Green (<€50k) | 🔵 Blue (€50-75k) | 🟠 Orange (€75-100k) | 🔴 Red (>€100k)")
st.markdown("---")

# Create map
folium_map = create_folium_map(lat_lon)

# Display map with FOLIUM (supports truly clickable links!)
st.subheader("🗺️ Interactive Property Map")

# Display Folium map
st_folium(folium_map, width=None, height=700, use_container_width=True, key="property_map")
