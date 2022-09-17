from st_aggrid import AgGrid
import streamlit as st  # 🎈 data web app development

df = st.session_state["df"]

AgGrid(df, fit_columns_on_grid_load=True)
