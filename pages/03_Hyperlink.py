import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


def _max_width_():
    max_width_str = f"max-width: 1400px"

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


_max_width_()


st.title("Overview of the property")


df = st.session_state["df"]

df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
lat_lon = df.dropna(subset=["longitude", "latitude"])

num_rows = lat_lon.count()[0]


def map_plot(df):
    # Change the zoom level according to the shape of df
    size = df["price"]
    if size <= 25000:
        zoom = 3
    elif size > 40000:
        zoom = 5
    else:
        zoom = 4
    # Get time for the moment
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Construct the figure
    fig = px.scatter_mapbox(
        df,
        hover_data=["price", "price_m"],
        lat="latitude",
        lon="longitude",
        color="price",
        size="size",
        color_continuous_scale=px.colors.cyclical.IceFire,
        zoom=zoom,
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(title_text=f"Overview of propety - {now}", title_x=0.5)

    return fig


st.map(lat_lon)
st.write("Number of Rows in DataFrame :", num_rows)


st.plotly_chart(map_plot(df))
