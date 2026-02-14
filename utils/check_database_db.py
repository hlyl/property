"""Check database.db properties."""
import pandas as pd
from sqlmodel import Session, create_engine

engine = create_engine("sqlite:///database.db")

with Session(engine) as session:
    # Check total properties
    df = pd.read_sql("SELECT COUNT(*) as total FROM property", con=session.connection())
    print(f"database.db - Total properties: {df['total'].iloc[0]}")

    # Check by sold status
    df_sold = pd.read_sql(
        "SELECT sold, COUNT(*) as count FROM property GROUP BY sold",
        con=session.connection()
    )
    print("\nBy sold status:")
    print(df_sold.to_string(index=False))

    # Check review status for unsold properties
    df_review = pd.read_sql(
        "SELECT review_status, COUNT(*) as count FROM property WHERE sold = 0 GROUP BY review_status",
        con=session.connection()
    )
    print("\nUnsold properties by review status:")
    print(df_review.to_string(index=False))
