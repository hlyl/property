# noqa: N999
import pandas as pd
import streamlit as st
from sqlmodel import Session, create_engine

from property_tracker.config.settings import get_database_url

st.set_page_config(page_title="Filter Properties", page_icon="🔍", layout="wide")

st.title("🔍 Filter Properties")

# Load data from session state or database
if "df" not in st.session_state:
    # Load from database if session state not initialized
    engine = create_engine(get_database_url())
    with Session(engine) as session:
        query = "SELECT * FROM property WHERE sold = 0"
        df = pd.read_sql(query, con=session.connection())
        st.session_state["df"] = df
else:
    df = st.session_state["df"]

# Show total properties metric at the top
st.metric("Total Properties in Database", len(df))
st.markdown("---")

overview = (
    df[
        [
            "id",
            "region",
            "price",
            "price_m",
            "shopping_count",
            "pub_count",
            "baker_count",
            "food_count",
            "dist_coast",
            "dist_water",
            "longitude",
            "latitude",
            "review_status",  # Add review_status column
        ]
    ]
    .copy()
    .sort_values(by="price_m")
)  # .copy() to avoid SettingWithCopyWarning

# Convert count columns to numeric, replacing empty/null values with 0
overview["shopping_count"] = pd.to_numeric(overview["shopping_count"], errors="coerce").fillna(0).astype(int)
overview["pub_count"] = pd.to_numeric(overview["pub_count"], errors="coerce").fillna(0).astype(int)
overview["baker_count"] = pd.to_numeric(overview["baker_count"], errors="coerce").fillna(0).astype(int)
overview["food_count"] = pd.to_numeric(overview["food_count"], errors="coerce").fillna(0).astype(int)

# Convert distance columns to numeric
overview["dist_coast"] = pd.to_numeric(overview["dist_coast"], errors="coerce").fillna(0).round(0).astype(int)
overview["dist_water"] = pd.to_numeric(overview["dist_water"], errors="coerce").fillna(-1).round(0).astype(int)


# max_dist_coast = overview["dist_coast"].max().astype(int)
# max_dist_coast = max_dist_coast.astype(int)
# max_dist_water = overview["dist_water"].max().astype(int)

col1, col2, col3 = st.columns(3)

with col1:
    shops = st.slider("Min. Shops: ", 0, 20, 0)  # Default to 0 to show all

with col2:
    pubs = st.slider("Min. Pubs: ", 0, 20, 0)  # Default to 0 to show all

with col3:
    bakers = st.slider("Min. Bakers: ", 0, 20, 0)  # Default to 0 to show all


col4, col5, col6 = st.columns(3)
with col4:
    food = st.slider("Min. Food: ", 0, 20, 0)  # Default to 0 to show all

with col5:
    coast = st.slider("Max distance to Coast: ", 0, 100, 100)  # Default to 100 to show all

with col6:
    water = st.slider("Max distance to River/lake: ", 0, 10, 10)  # Default to 10 to show all

# Add review status filter
st.markdown("---")
review_statuses = st.multiselect(
    "Review Status",
    ["To Review", "Interested", "Rejected"],
    default=["To Review", "Interested", "Rejected"],  # Show all by default
)


rslt = overview[
    (overview["shopping_count"] >= shops)
    & (overview["pub_count"] >= pubs)
    & (overview["baker_count"] >= bakers)
    & (overview["food_count"] >= food)
    & (overview["dist_coast"] <= coast)
    & (overview["dist_water"] <= water)
]

# Apply review status filter if review_status column exists
if "review_status" in rslt.columns and review_statuses:
    rslt = rslt[rslt["review_status"].isin(review_statuses)]


def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = str(link)
    link = "https://www.immobiliare.it/en/annunci/" + str(link)
    return f'<a target="_blank" href="{link}">{text}</a>'


# TRAILER is the column with hyperlinks
rslt["id"] = rslt["id"].apply(make_clickable)

# Show filtering results with metrics
st.markdown("---")
col_met1, col_met2, col_met3 = st.columns(3)
with col_met1:
    st.metric("Total Properties", len(df))
with col_met2:
    st.metric("After Filtering", len(rslt))
with col_met3:
    filter_percentage = (len(rslt) / len(df) * 100) if len(df) > 0 else 0
    st.metric("Match Rate", f"{filter_percentage:.1f}%")

st.markdown("---")

# Display the filtered results table
st.subheader("Filtered Properties")
st.write(rslt.to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")
st.subheader("📍 Property Locations Map")

# Ensure coordinates are numeric
rslt_map = rslt.copy()

# Need to convert back from clickable HTML to numeric ID for map display
# Since we modified the id column, let's work with a fresh copy before the modify
overview_for_map = overview[
    (overview["shopping_count"] >= shops)
    & (overview["pub_count"] >= pubs)
    & (overview["baker_count"] >= bakers)
    & (overview["food_count"] >= food)
    & (overview["dist_coast"] <= coast)
    & (overview["dist_water"] <= water)
]

# Apply review status filter
if "review_status" in overview_for_map.columns and review_statuses:
    overview_for_map = overview_for_map[overview_for_map["review_status"].isin(review_statuses)]

# Convert coordinates to numeric
overview_for_map["longitude"] = pd.to_numeric(overview_for_map["longitude"], errors="coerce")
overview_for_map["latitude"] = pd.to_numeric(overview_for_map["latitude"], errors="coerce")

# Drop rows with missing coordinates
lat_lon = overview_for_map.dropna(subset=["longitude", "latitude"])

# Show map metrics
col_map1, col_map2 = st.columns(2)
with col_map1:
    st.metric("Properties with Valid Coordinates", len(lat_lon))
with col_map2:
    missing_coords = len(rslt) - len(lat_lon)
    st.metric("Properties Missing Coordinates", missing_coords)

if len(lat_lon) > 0:
    st.map(lat_lon[["latitude", "longitude"]])
else:
    st.warning("No properties with valid coordinates to display on map.")

st.session_state["rslt"] = rslt
