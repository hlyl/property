import time  # to simulate a real time data, time loop
import sqlite3
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development

# ---------------SETTINGS----------------------------
page_title = "Main property page"
page_icon = ":house_with_garden:"
database = "database.db"
regions = [
    "LUCCA",
    "PISA",
    "LEGHORN",
    "VENICE",
    "TREVISO",
    "PORDENONE",
    "PADUA",
    "ROViGO",
    "BOLOGNA",
    "MILAN",
]
layout = "wide"
conn = sqlite3.connect(database)
# --------------------------------------------------
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.header(page_title + " " + page_icon)
df = pd.read_sql("select * from property where sold is 0", con=conn)
df = df.fillna(0)
print(df.isna())
df["id"] = df["id"].astype(int)
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["dist_coast"] = df["dist_coast"].astype(float)
df["dist_water"] = df["dist_water"].astype(float)
df.replace(to_replace="", value="0")
st.session_state["df"] = df

overview = df[
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
        "discription_dk",
    ]
].sort_values(by="price_m")

rslt = overview[
    (overview["shopping_count"] > 0)
    & (overview["pub_count"] > 0)
    & (overview["baker_count"] > 0)
    & (overview["food_count"] > 0)
    & (overview["dist_coast"] < 50)
].sort_values(by="price_m")

base_url = "https://www.immobiliare.it/annunci/"

st.markdown("### All Properties:")
st.dataframe(overview)
st.dataframe(rslt)
