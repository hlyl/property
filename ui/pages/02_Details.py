# noqa: N999
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

chart_price_m = df[df.columns[13]]
sort = chart_price_m.sort_values(ascending=True, ignore_index=True)
st.line_chart(sort)

# Get rslt from session state or use full df
rslt = st.session_state.get("rslt", df)

st.write(rslt.to_html(escape=False, index=False), unsafe_allow_html=True)
