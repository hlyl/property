from typing import Optional
from xmlrpc.client import Boolean
from sqlmodel import Field, SQLModel, create_engine, Session  #


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


# sqlite_file_name = "database.db"  #
# sqlite_url = f"sqlite:///{sqlite_file_name}"  #
# engine = create_engine(sqlite_url, echo=False)  #


# class Dao(object):
#    def __init__(self, db_name):
#        self.db_name = db_name
#        engine = create_engine(f"sqlite:///{db_name}")
#        SQLModel.metadata.create_all(engine)
#        session = Session(engine)


def create_db(db_name):
    engine = create_engine(f"sqlite:///{db_name}")
    SQLModel.metadata.create_all(engine)
    return engine


# def create_db_and_tables():  #
#    SQLModel.metadata.create_all(engine)  #
