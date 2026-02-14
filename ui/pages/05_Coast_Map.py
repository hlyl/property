# noqa: N999
"""Coast Distance Map - Interactive Folium Map

Displays an interactive map showing properties and their distance to the Italian coast.
"""

import json
import os
import sys
from pathlib import Path

import folium
import pandas as pd
import pyproj
import shapely
import streamlit as st
from shapely.geometry import Point
from shapely.ops import nearest_points
from sqlmodel import Session, create_engine
from streamlit_folium import st_folium

from property_tracker.config.settings import COASTLINE_PATH, get_database_url
from property_tracker.services.review import ReviewService

# Add parent directory to path for component imports
sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(page_title="Coast Distance Map", page_icon="🗺️", layout="wide")

st.title("🗺️ Interactive Coast Distance Map")
st.markdown("This map shows property locations and calculates distance to the Italian coast using Folium.")

# Database connection
engine = create_engine(get_database_url())


# Check if geojson file exists
geojson_path = str(COASTLINE_PATH)
if not os.path.exists(geojson_path):
    st.error(f"GeoJSON file not found: {geojson_path}")
    st.info("Please ensure ITA_coastline.json exists in data/boundaries/ directory.")
    st.stop()


def update_property_status(property_id: int, new_status: str):
    """Update property review status and refresh the UI."""
    with Session(engine) as session:
        service = ReviewService(session)
        success = service.update_status(property_id, new_status)
        if success:
            st.success(f"Property {property_id} marked as {new_status}!")
            st.cache_data.clear()
            if "df" in st.session_state:
                del st.session_state["df"]
            st.rerun()
        else:
            st.error(f"Failed to update property {property_id}")


# Load data from session state or database
if "df" not in st.session_state:
    with Session(engine) as session:
        query = "SELECT * FROM property WHERE sold = 0"
        df = pd.read_sql(query, con=session.connection())
        st.session_state["df"] = df
else:
    df = st.session_state["df"]

if df is None or df.empty:
    st.warning("No property data loaded. Please check your database.")
    st.stop()

# Set up coordinate systems
wgs_proj = pyproj.CRS("EPSG:4326")
utm_proj = pyproj.CRS("EPSG:32633")
project = pyproj.Transformer.from_crs(wgs_proj, utm_proj, always_xy=True).transform


# Load Italian coastline
@st.cache_data
def load_coastline():
    """Load and parse Italian coastline from GeoJSON."""
    with open(geojson_path) as f:
        your_json_file = json.load(f)

    # Parse the polygon coordinates
    coords = your_json_file["features"][0]["geometry"]["coordinates"][0]
    polygon_str = "POLYGON ((" + ", ".join([f"{c[0]} {c[1]}" for c in coords]) + "))"
    shape = shapely.wkt.loads(polygon_str)

    return your_json_file, shape


try:
    coastline_geojson, coastline_shape = load_coastline()
except Exception as e:
    st.error(f"Error loading coastline data: {e}")
    st.stop()

# Sidebar controls
st.sidebar.header("Map Controls")

# Filter properties by review status
review_filter = st.sidebar.multiselect("Review Status", ["To Review", "Interested", "Rejected"], default=["To Review", "Interested"])

# Filter dataframe
filtered_df = df[df["review_status"].isin(review_filter)] if "review_status" in df.columns and review_filter else df.copy()

# Select a property to highlight
property_ids = filtered_df["id"].tolist()
selected_property = st.sidebar.selectbox(
    "Select Property to Highlight", options=["None"] + property_ids, format_func=lambda x: f"Property {x}" if x != "None" else "None"
)

# Display stats
st.sidebar.markdown("---")
st.sidebar.metric("Properties on Map", len(filtered_df))
if selected_property != "None" and selected_property in filtered_df["id"].values:
    selected_row = filtered_df[filtered_df["id"] == selected_property].iloc[0]
    st.sidebar.markdown("**Selected Property:**")
    st.sidebar.write(f"- Region: {selected_row['region']}")
    st.sidebar.write(f"- Price: €{int(selected_row['price']):,}")

    # Add price per m² with null handling
    price_m_display = f"€{int(selected_row['price_m']):,}/m²" if pd.notna(selected_row.get("price_m")) else "N/A"
    st.sidebar.write(f"- Price/m²: {price_m_display}")

    # Add surface area - handle both numeric and string values
    surface_val = selected_row.get("surface")
    # If it's already a string with units, use it directly; if numeric, format it with units
    surface_display = (surface_val if isinstance(surface_val, str) else f"{int(surface_val)} m²") if pd.notna(surface_val) else "N/A"
    st.sidebar.write(f"- Surface: {surface_display}")

    # Add rooms
    rooms_display = selected_row.get("rooms") if pd.notna(selected_row.get("rooms")) else "N/A"
    st.sidebar.write(f"- Rooms: {rooms_display}")

    # Add bathrooms
    bathrooms_display = selected_row.get("bathrooms") if pd.notna(selected_row.get("bathrooms")) else "N/A"
    st.sidebar.write(f"- Bathrooms: {bathrooms_display}")

    st.sidebar.write(f"- Coast Distance: {selected_row['dist_coast']} km")

    # Display current status
    current_status = selected_row.get("review_status", "To Review")
    st.sidebar.write(f"- **Status:** {current_status}")

    # Action buttons
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Update Status:**")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("✅ Interested", key=f"interested_{selected_property}", width="stretch"):
            update_property_status(selected_property, "Interested")

    with col2:
        if st.button("❌ Reject", key=f"reject_{selected_property}", width="stretch"):
            update_property_status(selected_property, "Rejected")

    # Reset to "To Review" button
    if current_status != "To Review" and st.sidebar.button("🔄 Reset to Review", key=f"reset_{selected_property}", width="stretch"):
        update_property_status(selected_property, "To Review")

    # View listing button
    st.sidebar.markdown("---")
    property_url = f"https://www.immobiliare.it/annunci/{selected_property}/"
    st.sidebar.link_button("🔗 View Listing", property_url, width="stretch")

# Create the map
st.markdown("---")

# Determine map center
if selected_property != "None" and selected_property in filtered_df["id"].values:
    # Center on selected property
    selected_row = filtered_df[filtered_df["id"] == selected_property].iloc[0]

    # Check if selected property has valid coordinates
    if pd.notna(selected_row["latitude"]) and pd.notna(selected_row["longitude"]):
        center_lat = float(selected_row["latitude"])
        center_lon = float(selected_row["longitude"])
        zoom = 10
    else:
        # Fall back to Italy center if selected property has no coordinates
        center_lat = 43.0
        center_lon = 12.0
        zoom = 6
else:
    # Center on Italy
    center_lat = 43.0
    center_lon = 12.0
    zoom = 6

# Initialize Folium map
m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="OpenStreetMap")

# Add Italian coastline
geo_j = folium.GeoJson(coastline_geojson, style_function=lambda x: {"fillColor": "lightblue", "color": "blue", "weight": 2, "fillOpacity": 0.3})
geo_j.add_to(m)

# Add property markers
for _idx, row in filtered_df.iterrows():
    lat = row.get("latitude")
    lon = row.get("longitude")

    # Skip if missing or NaN
    if pd.isna(lat) or pd.isna(lon):
        continue

    # Convert to float if they're strings
    try:
        lat = float(lat)
        lon = float(lon)
    except (ValueError, TypeError):
        continue

    # Determine marker color based on review status
    status = row.get("review_status", "To Review")
    if status == "Interested":
        color = "green"
    elif status == "Rejected":
        color = "red"
    else:
        color = "orange"

    # Highlight selected property
    if selected_property != "None" and row["id"] == selected_property:
        color = "purple"
        radius = 12
        fill_opacity = 1.0
    else:
        radius = 6
        fill_opacity = 0.7

    # Create popup content
    price_m_display = f"€{int(row['price_m']):,}" if pd.notna(row["price_m"]) else "N/A"
    rooms_display = row["rooms"] if pd.notna(row["rooms"]) else "N/A"

    popup_html = f"""
    <div style="font-family: Arial; min-width: 200px;">
        <h4>Property {row["id"]}</h4>
        <b>Region:</b> {row["region"]}<br>
        <b>Price:</b> €{int(row["price"]):,}<br>
        <b>Price/m²:</b> {price_m_display}<br>
        <b>Rooms:</b> {rooms_display}<br>
        <b>Coast Distance:</b> {row["dist_coast"]} km<br>
        <b>Status:</b> {status}<br>
        <a href="https://www.immobiliare.it/annunci/{row["id"]}/" target="_blank">View Listing</a>
    </div>
    """

    # Add marker
    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fillColor=color,
        fillOpacity=fill_opacity,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"Property {row['id']} - {row['region']}",
    ).add_to(m)

# If property selected, draw line to nearest coast point
if selected_property != "None" and selected_property in filtered_df["id"].values:
    selected_row = filtered_df[filtered_df["id"] == selected_property].iloc[0]

    # Check if selected property has valid coordinates
    if pd.notna(selected_row["latitude"]) and pd.notna(selected_row["longitude"]):
        pt = Point(float(selected_row["longitude"]), float(selected_row["latitude"]))
        p1, p2 = nearest_points(coastline_shape.boundary, pt)

        # Add line to nearest coast point
        folium.PolyLine(
            locations=[[float(selected_row["latitude"]), float(selected_row["longitude"])], [p1.y, p1.x]],
            color="red",
            weight=3,
            opacity=0.7,
            dash_array="10, 5",
        ).add_to(m)

        # Add marker at nearest coast point
        folium.CircleMarker(
            location=[p1.y, p1.x],
            radius=8,
            color="darkblue",
            fill=True,
            fillColor="darkblue",
            fillOpacity=1.0,
            popup="Nearest Coast Point",
            tooltip="Nearest Coast Point",
        ).add_to(m)

# Add legend
legend_html = """
<div style="position: fixed;
            bottom: 50px; right: 50px;
            border:2px solid grey; z-index:9999;
            background-color:white;
            padding: 10px;
            font-size: 14px;
            ">
<p style="margin:0"><b>Property Status:</b></p>
<p style="margin:0"><i class="fa fa-circle" style="color:orange"></i> To Review</p>
<p style="margin:0"><i class="fa fa-circle" style="color:green"></i> Interested</p>
<p style="margin:0"><i class="fa fa-circle" style="color:red"></i> Rejected</p>
<p style="margin:0"><i class="fa fa-circle" style="color:purple"></i> Selected</p>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Display the map and capture clicks
map_data = st_folium(m, width=1400, height=700, key="coast_map")

# Display click debugging (temporary)
if map_data:
    st.write("Debug - Map data:", map_data)

# Add quick review buttons below map when a marker is clicked
if map_data and map_data.get("last_object_clicked"):
    clicked_obj = map_data["last_object_clicked"]
    st.write("Debug - Clicked object:", clicked_obj)

    # Try to extract property ID from tooltip
    # Tooltip format is: "Property {id} - {region}"
    tooltip = clicked_obj.get("tooltip", "")
    st.write("Debug - Tooltip:", tooltip)

    try:
        # Extract property ID from tooltip
        if "Property " in tooltip:
            property_id_str = tooltip.split("Property ")[1].split(" - ")[0]
            clicked_property_id = int(property_id_str)

            # Find the property in filtered_df
            if clicked_property_id in filtered_df["id"].values:
                review_row = filtered_df[filtered_df["id"] == clicked_property_id].iloc[0]

                # Display quick review section
                st.markdown("---")
                st.subheader("🎯 Quick Review - Click to Update Status")

                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    price_str = f"€{int(review_row['price']):,}" if pd.notna(review_row["price"]) else "N/A"
                    st.markdown(f"**Property {review_row['id']}** - {review_row['region']} - {price_str}")
                    st.caption(f"🏖️ Coast: {review_row['dist_coast']} km | Status: {review_row.get('review_status', 'To Review')}")

                with col2:
                    if st.button("✅ Interested", key="map_interested", width="stretch"):
                        update_property_status(clicked_property_id, "Interested")

                with col3:
                    if st.button("❌ Reject", key="map_reject", width="stretch"):
                        update_property_status(clicked_property_id, "Rejected")

                with col4:
                    property_url = f"https://www.immobiliare.it/annunci/{review_row['id']}/"
                    st.link_button("🔗 View", property_url, width="stretch")
    except (ValueError, IndexError, KeyError) as e:
        # If we can't parse the property ID, show error
        st.error(f"Error parsing property: {e}")
        st.info("💡 Click on a property marker on the map to review it quickly!")
else:
    # Show hint when nothing is clicked
    st.info("💡 Click on a property marker (colored dot) on the map above to review it quickly!")

# Display property table below map
st.markdown("---")
st.subheader(f"Properties on Map ({len(filtered_df)} total)")

# Show table with key information
display_cols = ["id", "region", "price", "price_m", "rooms", "dist_coast", "review_status"]
available_cols = [col for col in display_cols if col in filtered_df.columns]
st.dataframe(filtered_df[available_cols].sort_values(by="dist_coast"), use_container_width=True, hide_index=True)
