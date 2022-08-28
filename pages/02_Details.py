import streamlit as st

df = st.session_state["df"]

chart_price_m = df[df.columns[13]]

st.write(chart_price_m)

sort_price = chart_price_m.sort_values("price_m")
st.line_chart(chart_price_m)
