from sqlmodel import Session, create_engine, func, select

from property_tracker.models.property import Property

engine = create_engine("sqlite:///database.db")
session = Session(engine)

# Check review status counts
stmt = select(Property.review_status, func.count(Property.id)).where(Property.sold == 0).group_by(Property.review_status)
results = session.exec(stmt).all()
print("Review status counts:")
for status, count in results:
    print(f"  {status or 'NULL'}: {count}")

# Check total
total = session.exec(select(func.count(Property.id)).where(Property.sold == 0)).one()
print(f"\nTotal unsold: {total}")

session.close()
