"""POI (Point of Interest) counting services for property enrichment.

Provides two implementations:
- OverpassPOIService: Free OpenStreetMap data via Overpass API
- GooglePlacesPOIService: Google Places API (requires API key and costs $)
"""

from dataclasses import dataclass
from typing import Protocol

from loguru import logger


@dataclass
class POICounts:
    """Count of nearby points of interest for a property location."""

    bars: int
    shops: int
    bakeries: int
    restaurants: int


class POIService(Protocol):
    """Interface for POI counting services."""

    def get_all_counts(self, lat: float, lon: float, radius: int = 2000) -> POICounts:
        """Get counts of all POI types near a location.

        Args:
            lat: Latitude of the property
            lon: Longitude of the property
            radius: Search radius in meters (default: 2000)

        Returns:
            POICounts with counts for bars, shops, bakeries, and restaurants
        """
        ...


class OverpassPOIService:
    """Free OpenStreetMap POI counter using Overpass API.

    Uses OpenStreetMap data through the Overpass API to count
    nearby amenities. Completely free with no usage limits.
    """

    def __init__(self) -> None:
        """Initialize the Overpass API client."""
        import time

        import overpy

        self.api = overpy.Overpass()
        self.time = time

    # Mapping of our POI types to OpenStreetMap tag queries
    OSM_QUERIES = {
        "bar": '[out:json];node["amenity"~"bar|pub|cafe"](around:{radius},{lat},{lon});out count;',
        "shop": '[out:json];node["shop"~"supermarket|convenience|grocery"](around:{radius},{lat},{lon});out count;',
        "bakery": '[out:json];node["shop"="bakery"](around:{radius},{lat},{lon});out count;',
        "restaurant": '[out:json];node["amenity"="restaurant"](around:{radius},{lat},{lon});out count;',
    }

    def count_pois(self, lat: float, lon: float, radius: int, poi_type: str) -> int:
        """Count POIs of a specific type near a location.

        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters
            poi_type: Type of POI (bar, shop, bakery, restaurant)

        Returns:
            Count of POIs found

        Raises:
            ValueError: If poi_type is not recognized
        """
        query_template = self.OSM_QUERIES.get(poi_type)
        if not query_template:
            raise ValueError(f"Unknown POI type: {poi_type}")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add delay to avoid rate limiting (increased from 1s to 2s)
                self.time.sleep(2)
                query = query_template.format(lat=lat, lon=lon, radius=radius)
                result = self.api.query(query)
                count = len(result.nodes)
                logger.debug(f"Overpass API found {count} {poi_type}s near ({lat}, {lon})")
                return count
            except Exception as e:
                error_msg = str(e).lower()
                # Check if it's a rate limit or server load error
                if ("too many" in error_msg or "load too high" in error_msg) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 5s, 10s, 15s
                    logger.warning(f"Overpass API rate limited for {poi_type}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    self.time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Overpass API query failed for {poi_type}: {e}")
                    return 0  # Return 0 on error rather than failing

        return 0  # If all retries failed

    def get_all_counts(self, lat: float, lon: float, radius: int = 2000) -> POICounts:
        """Get counts of all POI types near a location.

        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters (default: 2000)

        Returns:
            POICounts with all POI type counts
        """
        return POICounts(
            bars=self.count_pois(lat, lon, radius, "bar"),
            shops=self.count_pois(lat, lon, radius, "shop"),
            bakeries=self.count_pois(lat, lon, radius, "bakery"),
            restaurants=self.count_pois(lat, lon, radius, "restaurant"),
        )


class GooglePlacesPOIService:
    """Google Places API POI counter (fallback option).

    Requires a Google API key and incurs costs based on usage.
    Provided as a fallback option or for comparison purposes.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize the Google Places API client.

        Args:
            api_key: Google Places API key

        Raises:
            ImportError: If googleplaces library is not installed
        """
        try:
            from googleplaces import GooglePlaces, types
        except ImportError:
            raise ImportError("googleplaces library not installed. Install with: uv sync --extra google") from None

        self.google_places = GooglePlaces(api_key)
        self.types = types
        logger.info("Google Places API initialized (will incur costs)")

    def count_pois(self, lat: float, lon: float, radius: int, poi_types: list) -> int:
        """Count POIs using Google Places API.

        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters
            poi_types: List of Google Places API type constants

        Returns:
            Count of POIs found
        """
        try:
            query = self.google_places.nearby_search(
                lat_lng={"lat": lat, "lng": lon},
                radius=radius,
                types=poi_types,
            )
            count = len(query.places)
            logger.debug(f"Google Places API found {count} POIs near ({lat}, {lon})")
            return count
        except Exception as e:
            logger.error(f"Google Places API query failed: {e}")
            return 0

    def get_all_counts(self, lat: float, lon: float, radius: int = 2000) -> POICounts:
        """Get counts of all POI types near a location.

        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters (default: 2000)

        Returns:
            POICounts with all POI type counts
        """
        return POICounts(
            bars=self.count_pois(lat, lon, radius, [self.types.TYPE_BAR, self.types.TYPE_CAFE]),
            shops=self.count_pois(
                lat,
                lon,
                radius,
                [self.types.TYPE_GROCERY_OR_SUPERMARKET, self.types.TYPE_STORE],
            ),
            bakeries=self.count_pois(lat, lon, radius, [self.types.TYPE_BAKERY]),
            restaurants=self.count_pois(lat, lon, radius, [self.types.TYPE_RESTAURANT, self.types.TYPE_FOOD]),
        )


def get_poi_service(use_google: bool = False, api_key: str | None = None) -> POIService:
    """Factory function to get the appropriate POI service.

    Args:
        use_google: If True, use Google Places API (requires api_key)
        api_key: Google Places API key (required if use_google=True)

    Returns:
        POIService implementation (Overpass or Google)

    Raises:
        ValueError: If use_google=True but api_key is not provided
    """
    if use_google:
        if not api_key:
            raise ValueError("api_key is required when use_google=True")
        logger.info("Using Google Places API for POI counting (costs money)")
        return GooglePlacesPOIService(api_key)
    else:
        logger.info("Using Overpass API for POI counting (free)")
        return OverpassPOIService()
