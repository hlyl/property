import streamlit as st
import pandas as pd
from IPython.core.display import display, HTML

df = st.session_state["df"]

chart_price_m = df[df.columns[13]]
sort = chart_price_m.sort_values(ascending=True, ignore_index=True)
st.line_chart(sort)

rslt = st.session_state["rslt"]

st.write(rslt.to_html(escape=False, index=False), unsafe_allow_html=True)
