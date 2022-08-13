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

overview = df[["region", "price", "shopping_count", "pub_count"]].sort_values(
    by="price"
)
overview = overview[(overview["shopping_count"] > 0) & (overview["pub_count"] > 0)]
# near real-time / live feed simulation
st.markdown("### All Properties:")
st.dataframe(overview)

# top-level filters
region_filter = st.selectbox("Select Region", pd.unique(df["region"]))


# dataframe filter
df = df[df["region"] == region_filter]

# near real-time / live feed simulation
st.markdown("### Detailed Data View")
st.dataframe(df)
