from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session
from sqlalchemy import Engine


class Property(SQLModel, table=True):  #
    __table_args__ = {'extend_existing': True}

    id: Optional[int] = Field(default=None, primary_key=True)  #
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
    review_status: str = Field(default="To Review")  # "To Review" | "Rejected" | "Interested"
    reviewed_date: Optional[str] = None  # ISO datetime when status changed
    favorite: Optional[int] = Field(default=0)
    viewed: Optional[int] = Field(default=0)
    hidden: Optional[int] = Field(default=0)
    notes: Optional[str] = Field(default=None)


def create_db(db_name: str) -> Engine:
    """Create a SQLite database and initialize the schema.

    Args:
        db_name: Name of the database file (e.g., 'database.db')

    Returns:
        SQLAlchemy Engine instance for the database
    """
    engine = create_engine(f"sqlite:///{db_name}")
    SQLModel.metadata.create_all(engine)
    return engine
