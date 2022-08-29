import streamlit as st
import pandas as pd

df = st.session_state["df"]

df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df = df.dropna(subset=["longitude", "latitude"])

st.map(df)
