"""Property data model.

This module contains the Property model for Italian real estate listings
with review tracking and geospatial enrichment.
"""

from typing import Optional
from sqlmodel import Field, SQLModel


class Property(SQLModel, table=True):
    """Property listing model with review tracking and POI enrichment.

    Represents a real estate property from Immobiliare.it with additional
    enrichment data including distance calculations, POI counts, and translations.
    """

    __tablename__ = "property"
    __table_args__ = {'extend_existing': True}

    # Core identification
    id: Optional[int] = Field(default=None, primary_key=True)
    region: str
    province: Optional[str] = None
    city: Optional[str] = None
    category: str

    # Pricing information
    price: Optional[int] = None
    price_m: Optional[int] = None  # Price per square meter
    price_drop: Optional[str] = None

    # Property details
    bathrooms: Optional[str] = None
    rooms: Optional[str] = None
    surface: Optional[str] = None
    floor: Optional[str] = None
    is_new: Optional[int] = None

    # Description and media
    caption: Optional[str] = None
    discription: str  # Note: typo from original schema
    discription_dk: str  # Danish translation
    photo_list: str

    # Geospatial data
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    marker: Optional[str] = None
    dist_coast: Optional[str] = None  # Distance to coast in km
    dist_water: Optional[str] = None  # Distance to water in km

    # POI counts (Points of Interest)
    shopping_count: Optional[int] = None
    pub_count: Optional[int] = None
    baker_count: Optional[int] = None
    food_count: Optional[int] = None

    # Status tracking
    sold: int = 0  # 0 = unsold, 1 = sold
    observed: Optional[str] = None  # First observation date

    # Review tracking fields
    review_status: str = Field(default="To Review")  # "To Review" | "Rejected" | "Interested"
    reviewed_date: Optional[str] = None  # ISO datetime when status changed

    # Interaction fields (user engagement)
    favorite: Optional[int] = Field(default=0)  # 0 = not favorite, 1 = favorite
    viewed: Optional[int] = Field(default=0)  # 0 = not viewed, 1 = viewed
    hidden: Optional[int] = Field(default=0)  # 0 = visible, 1 = hidden
    notes: Optional[str] = Field(default=None)  # User notes about property
