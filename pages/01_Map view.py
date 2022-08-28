import streamlit as st

df = st.session_state["df"]

st.header("This is  the descritpion of the df")
st.write(df.describe())
