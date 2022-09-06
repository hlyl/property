import streamlit as st
import pandas as pd
from IPython.core.display import display, HTML

df = st.session_state["df"]

chart_price_m = df[df.columns[13]]
sort = chart_price_m.sort_values(ascending=True, ignore_index=True)
st.line_chart(sort)


def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = str(link)
    link = "https://www.immobiliare.it/en/annunci/" + str(link)
    return f'<a target="_blank" href="{link}">{text}</a>'


# TRAILER is the column with hyperlinks
df["id"] = df["id"].apply(make_clickable)

st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
