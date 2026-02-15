"""Property data model.

This module contains the Property model for Italian real estate listings
with review tracking and geospatial enrichment.
"""

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class Property(SQLModel, table=True):
    """Property listing model with review tracking and POI enrichment.

    Represents a real estate property from Immobiliare.it with additional
    enrichment data including distance calculations, POI counts, and translations.
    """

    __tablename__ = "property"
    __table_args__ = {"extend_existing": True}

    # Core identification
    id: int | None = Field(default=None, primary_key=True)
    region: str
    province: str | None = None
    city: str | None = None
    category: str

    # Pricing information
    price: int | None = None
    price_m: int | None = None  # Price per square meter
    price_drop: str | None = None

    # Property details
    bathrooms: str | None = None
    rooms: str | None = None
    surface: str | None = None
    floor: str | None = None
    is_new: int | None = None

    # Description and media
    caption: str | None = None
    discription: str  # Note: typo from original schema
    discription_dk: str  # Danish translation
    photo_list: str

    # Geospatial data
    latitude: str | None = None
    longitude: str | None = None
    marker: str | None = None
    dist_coast: str | None = None  # Distance to coast in km
    dist_water: str | None = None  # Distance to water in km

    # POI counts (Points of Interest)
    shopping_count: int | None = None
    pub_count: int | None = None
    baker_count: int | None = None
    food_count: int | None = None

    # Status tracking
    sold: int = 0  # 0 = unsold, 1 = sold
    observed: str | None = None  # First observation date

    # Review tracking fields
    review_status: str = Field(default="To Review")  # "To Review" | "Rejected" | "Interested"
    reviewed_date: str | None = None  # ISO datetime when status changed

    # Interaction fields (user engagement)
    favorite: int | None = Field(default=0)  # 0 = not favorite, 1 = favorite
    viewed: int | None = Field(default=0)  # 0 = not viewed, 1 = viewed
    hidden: int | None = Field(default=0)  # 0 = visible, 1 = hidden
    notes: str | None = Field(default=None)  # User notes about property

    @field_validator("price", "price_m", mode="before")
    @classmethod
    def _coerce_price_fields_to_int(cls, value):
        if value is None or value == "":
            return None
        try:
            return int(round(float(value)))
        except (TypeError, ValueError):
            return None
