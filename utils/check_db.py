"""Quick script to check database contents."""

import pandas as pd
from sqlmodel import Session, create_engine

engine = create_engine("sqlite:///test.db")

with Session(engine) as session:
    # Check total properties
    df = pd.read_sql("SELECT COUNT(*) as total FROM property WHERE sold = 0", con=session.connection())
    print(f"Total unsold properties: {df['total'].iloc[0]}")

    # Check by review status
    df_status = pd.read_sql("SELECT review_status, COUNT(*) as count FROM property WHERE sold = 0 GROUP BY review_status", con=session.connection())
    print("\nBy review status:")
    print(df_status.to_string(index=False))

    # Check sample properties
    df_sample = pd.read_sql("SELECT id, region, price, review_status FROM property WHERE sold = 0 LIMIT 5", con=session.connection())
    print("\nSample properties:")
    print(df_sample.to_string(index=False))
