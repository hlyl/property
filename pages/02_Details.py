import streamlit as st

df = st.session_state["df"]

chart_price_m = df[df.columns[13]]
sort = chart_price_m.sort_values(ascending=True, ignore_index=True)
st.line_chart(sort)
