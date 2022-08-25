import time  # to simulate a real time data, time loop
import sqlite3
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development

database = "database.db"
conn = sqlite3.connect(database)

st.set_page_config(
    page_title="The overview of the property results",
    page_icon="✅",
    layout="wide",
)

# read df from a sql
df = pd.read_sql("select * from property where sold is 0", con=conn)

# dashboard title
st.title("Property overview / Data that have been entered in the DB")

# creating a single-element container
placeholder = st.empty()

placeholder2 = st.empty()

tolink = df[["id"]]

overview = df[
    [
        "id",
        "region",
        "price",
        "shopping_count",
        "pub_count",
        "baker_count",
        "food_count",
        "dist_coast",
    ]
].sort_values(by="price")

base_url = "https://www.immobiliare.it/annunci/"

# tolink["link"] = base_url + str(tolink["id"])

overview["link"] = base_url + overview["id"].astype(str)


def make_clickable(link):
    text = link[0]
    return f'<a target="_blank" href="{link}">{text}</a>'


overview.style.format({"link": make_clickable})

overview = overview[
    (overview["dist_coast"].astype(float) < 50.0)
    & (overview["shopping_count"] > 0)
    & (overview["pub_count"] > 0)
    & (overview["baker_count"] > 0)
    & (overview["food_count"] > 0)
]
# near real-time / live feed simulation
st.markdown("### All Properties:")
st.dataframe(overview)

st.markdown("### making Links:")
st.dataframe(tolink)

# top-level filters
region_filter = st.selectbox("Select Region", pd.unique(df["region"]))


# dataframe filter
df = df[df["region"] == region_filter]

# near real-time / live feed simulation
st.markdown("### Detailed Data View")
st.dataframe(df)
