"""Check all properties including sold."""
import pandas as pd
from sqlmodel import Session, create_engine

engine = create_engine("sqlite:///test.db")

with Session(engine) as session:
    # Check all properties
    df = pd.read_sql("SELECT COUNT(*) as total FROM property", con=session.connection())
    print(f"Total properties (all): {df['total'].iloc[0]}")

    # Check by sold status
    df_sold = pd.read_sql(
        "SELECT sold, COUNT(*) as count FROM property GROUP BY sold",
        con=session.connection()
    )
    print("\nBy sold status:")
    print(df_sold.to_string(index=False))

    # Check review status for all properties
    df_review = pd.read_sql(
        "SELECT review_status, sold, COUNT(*) as count FROM property GROUP BY review_status, sold",
        con=session.connection()
    )
    print("\nBy review status and sold:")
    print(df_review.to_string(index=False))
