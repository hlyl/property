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
layout = "centered"
conn = sqlite3.connect(database)
# --------------------------------------------------
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.header(page_title + " " + page_icon)
# df = pd.read_sql("select * from property where sold is 0", con=conn)
df = pd.read_sql("select * from property", con=conn)
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

base_url = "https://www.immobiliare.it/annunci/"

st.markdown("### All Properties:")
st.dataframe(overview)
