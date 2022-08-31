from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session, select, update  #


class Property(SQLModel, table=True):  #
    id: Optional[int] = Field(default=None, primary_key=True)  #
    region: str
    is_new: Optional[int] = None
    price: Optional[int] = None
    price_drop: Optional[str] = None
    bathrooms: Optional[str]
    caption: Optional[str]
    category: str
    discription: str
    discription_dk: str
    floor: Optional[str]
    rooms: Optional[str]
    surface: Optional[str]
    price_m: Optional[int]
    longitude: Optional[str]
    latitude: Optional[str]
    marker: Optional[str]
    photo_list: str
    dist_coast: Optional[str]
    dist_water: Optional[str]
    shopping_count: Optional[int]
    pub_count: Optional[int]
    baker_count: Optional[int]
    food_count: Optional[int]
    sold: int = 0
    observed: Optional[str]


def create_db(db_name):
    engine = create_engine(f"sqlite:///{db_name}")
    SQLModel.metadata.create_all(engine)
    return engine


def update_sold(session):
    statement = update(Property).values(sold=0)
    session.execute(statement)
    session.commit()


if __name__ == "__main__":
    db_engine = create_db("database.db")
    with Session(db_engine) as session:
        update_sold(session)
