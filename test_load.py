import pandas as pd
from sqlmodel import Session, create_engine, select

from property_tracker.config.settings import get_database_url
from property_tracker.models.property import Property

# Replicate the load function
engine = create_engine(get_database_url())

with Session(engine) as session:
    statement = select(Property).where(Property.sold == 0)
    properties = session.exec(statement).all()
    print(f"Found {len(properties)} properties")

    df = pd.DataFrame([prop.model_dump() for prop in properties])
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {df.columns.tolist()[:5]}...")  # First 5 columns

    if len(df) > 0:
        print(f"Sample regions: {df['region'].unique()[:5]}")
    else:
        print("DataFrame is empty!")
