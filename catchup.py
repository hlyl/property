import requests
from sqlmodel import Field, SQLModel, create_engine, Session, select
from typing import Optional


class Property(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    region: str
    is_new: Optional[int] = None
    price: Optional[int] = None
    price_drop: Optional[str] = None
    bathrooms: Optional[str] = None
    caption: Optional[str] = None
    category: str
    discription: str
    discription_dk: str
    floor: Optional[str] = None
    rooms: Optional[str] = None
    surface: Optional[str] = None
    price_m: Optional[int] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    marker: Optional[str] = None
    photo_list: str
    dist_coast: Optional[str] = None
    dist_water: Optional[str] = None
    shopping_count: Optional[int] = None
    pub_count: Optional[int] = None
    baker_count: Optional[int] = None
    food_count: Optional[int] = None
    sold: int = 0
    observed: Optional[str] = None
    reviewed: Optional[int] = 0


def create_db(db_name):
    engine = create_engine(f"sqlite:///{db_name}")
    SQLModel.metadata.create_all(engine)
    return engine


def update_property_status(session: Session):
    base_url = "https://www.immobiliare.it/en/annunci/"
    suffix = "/?imm_source=homepage"
    unavailable_text = "The page you are looking for is not present on our site or is no longer available."

    properties = session.exec(select(Property).where(Property.sold == 0)).all()
    total_properties = len(properties)
    processed_count = 0
    specific_id = 106412105

    for property in properties:
        # if property.id != specific_id:
        #    continue
        url = f"{base_url}{property.id}{suffix}"
        response = requests.get(url)

        if unavailable_text in response.text:
            property.sold = 1
            session.add(property)
            session.commit()
            print(f"Property {property.id} marked as sold.")

        processed_count += 1
        print(f"Processed {processed_count} out of {total_properties} properties.")


if __name__ == "__main__":
    db_name = "radius_database.db"
    engine = create_db(db_name)

    with Session(engine) as session:
        update_property_status(session)
