"""Geospatial distance calculations with lazy-loading.

This module provides distance calculations to coastlines and water bodies
using GeoJSON data. Data files are loaded lazily only when first needed,
avoiding the 8.7MB import-time overhead of the original implementation.
"""

import json
from typing import Any

import pyproj
from pyproj import Transformer
from shapely import wkt
from shapely.geometry import LineString
from shapely.ops import nearest_points, transform
from shapely.strtree import STRtree

from property_tracker.config.settings import COASTLINE_PATH, WATERLINES_PATH


class DistanceCalculator:
    """Calculate distances to Italian coastlines and water bodies.

    This class implements lazy-loading of large GeoJSON files to avoid
    import-time overhead. Files are only loaded when first needed.

    Performance:
        - Coastline data: ~714KB (loaded on first use)
        - Water lines data: ~8MB (loaded on first use)
        - Total savings: ~8.7MB not loaded at import time
    """

    def __init__(self):
        """Initialize the distance calculator with lazy-loading.

        GeoJSON files are NOT loaded here - they're loaded on first use.
        """
        # Lazy-loaded data (None until first use)
        self._coastline: Any | None = None
        self._water_lines: list[Any] | None = None  # Store the actual geometries
        self._water_tree: STRtree | None = None  # Store the spatial index

        # Coordinate transformers
        self._wgs_proj = pyproj.CRS("EPSG:4326")  # WGS84 (lat/lon)
        self._utm_proj = pyproj.CRS("EPSG:32633")  # UTM Zone 33N (meters)
        self._transformer = Transformer.from_crs(self._wgs_proj, self._utm_proj, always_xy=True)

    def _load_coastline(self) -> None:
        """Lazy-load Italian coastline geometry from GeoJSON.

        This method is called automatically on first distance calculation.
        The coastline data is cached after first load.
        """
        if self._coastline is not None:
            return  # Already loaded

        with open(COASTLINE_PATH) as f:
            geojson_data = json.load(f)

        # Extract coordinates from the first feature
        coords = geojson_data["features"][0]["geometry"]["coordinates"][0]

        # Convert to WKT POLYGON format
        coords_str = ", ".join(f"{lon} {lat}" for lon, lat in coords)
        wkt_polygon = f"POLYGON (({coords_str}))"

        # Load as Shapely geometry
        self._coastline = wkt.loads(wkt_polygon)

    def _load_water_tree(self) -> None:
        """Lazy-load Italian water lines as spatial index tree.

        This method is called automatically on first water distance calculation.
        The spatial tree is cached after first load.
        """
        if self._water_tree is not None:
            return  # Already loaded

        with open(WATERLINES_PATH) as f:
            geojson_data = json.load(f)

        # Extract all water line geometries and project to UTM
        water_lines = []
        for feature in geojson_data["features"]:
            coords = feature["geometry"]["coordinates"]
            line_geom = LineString(coords)
            # Project to UTM for accurate distance calculations
            projected_line = transform(self._transformer.transform, line_geom)
            water_lines.append(projected_line)

        # Store the geometries list and build spatial index
        self._water_lines = water_lines
        self._water_tree = STRtree(water_lines)

    def calculate_coast_distance(self, lat: float, lon: float) -> float:
        """Calculate distance from a point to the nearest coastline.

        Args:
            lat: Latitude in decimal degrees (WGS84)
            lon: Longitude in decimal degrees (WGS84)

        Returns:
            Distance to nearest coastline in kilometers

        Note:
           On first call, this will load ~714KB of coastline data.
            Subsequent calls use the cached data.
        """
        # Lazy-load coastline data on first use
        self._load_coastline()
        assert self._coastline is not None  # Type narrowing for mypy

        # Create point from coordinates
        point_wkt = f"POINT ({lon} {lat})"
        point = wkt.loads(point_wkt)

        # Find nearest point on coastline boundary
        p_coast, p_query = nearest_points(self._coastline.boundary, point)

        # Project both points to UTM for accurate distance calculation
        p_coast_utm = transform(self._transformer.transform, p_coast)
        p_query_utm = transform(self._transformer.transform, p_query)

        # Calculate distance in meters, convert to kilometers
        distance_m: float = p_coast_utm.distance(p_query_utm)
        return distance_m / 1000.0

    def calculate_water_distance(self, lat: float, lon: float) -> float:
        """Calculate distance from a point to the nearest water body.

        Args:
            lat: Latitude in decimal degrees (WGS84)
            lon: Longitude in decimal degrees (WGS84)

        Returns:
            Distance to nearest water feature in kilometers

        Note:
            On first call, this will load ~8MB of water line data.
            Subsequent calls use the cached spatial tree.
        """
        # Lazy-load water tree on first use
        self._load_water_tree()
        assert self._water_tree is not None  # Type narrowing for mypy
        assert self._water_lines is not None  # Type narrowing for mypy

        # Create point from coordinates
        point_wkt = f"POINT ({lon} {lat})"
        point = wkt.loads(point_wkt)

        # Project point to UTM for accurate distance calculation
        point_utm = transform(self._transformer.transform, point)

        # Find nearest water feature using spatial index (returns index)
        nearest_idx = self._water_tree.nearest(point_utm)
        nearest_water = self._water_lines[nearest_idx]

        # Calculate distance in meters, convert to kilometers
        distance_m: float = point_utm.distance(nearest_water)
        return distance_m / 1000.0

    def calculate_both_distances(self, lat: float, lon: float) -> tuple[float, float]:
        """Calculate both coast and water distances in one call.

        Args:
            lat: Latitude in decimal degrees (WGS84)
            lon: Longitude in decimal degrees (WGS84)

        Returns:
            Tuple of (coast_distance_km, water_distance_km)

        Note:
            This is more efficient than calling both methods separately
            if you need both distances.
        """
        coast_dist = self.calculate_coast_distance(lat, lon)
        water_dist = self.calculate_water_distance(lat, lon)
        return coast_dist, water_dist


# Module-level convenience instance (lazy-loaded)
_default_calculator: DistanceCalculator | None = None


def get_calculator() -> DistanceCalculator:
    """Get the default DistanceCalculator instance (singleton).

    Returns:
        Shared DistanceCalculator instance

    Note:
        This creates a module-level singleton to avoid reloading
        GeoJSON data across multiple imports.
    """
    global _default_calculator

    if _default_calculator is None:
        _default_calculator = DistanceCalculator()

    return _default_calculator
