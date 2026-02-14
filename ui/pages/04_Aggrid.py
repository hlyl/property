"""Grid View Page - Property Data Table

Displays properties in an interactive table view.
"""

import pandas as pd
import streamlit as st
from sqlmodel import Session, create_engine

from property_tracker.config.settings import get_database_url

# Load data from session state or database
if "df" not in st.session_state:
    engine = create_engine(get_database_url())
    with Session(engine) as session:
        query = "SELECT * FROM property WHERE sold = 0"
        df = pd.read_sql(query, con=session.connection())
        st.session_state["df"] = df
else:
    df = st.session_state["df"]

if df is None or df.empty:
    st.warning("No data loaded. Please check your database.")
else:
    st.title("📊 Property Grid View")
    st.markdown(f"Showing {len(df)} properties")

    # Display interactive dataframe with full width
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=700
    )
