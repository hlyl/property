"""Backwards compatibility shim for calcdist module.

This module provides backwards compatibility by delegating to the new
property_tracker.utils.distance module with lazy-loading.

DEPRECATED: Use property_tracker.utils.distance.DistanceCalculator instead.
"""

from property_tracker.utils.distance import get_calculator

# Get the shared calculator instance
_calculator = get_calculator()


def calc_dist_short(poi: tuple[float, float]) -> float:
    """Calculate distance from a point to the nearest coastline.

    DEPRECATED: Use DistanceCalculator.calculate_coast_distance() instead.

    Args:
        poi: Tuple of (latitude, longitude)

    Returns:
        Distance to coastline in kilometers
    """
    lat, lon = poi
    return _calculator.calculate_coast_distance(lat, lon)


def calc_dist_water(tree, poi: tuple[float, float]) -> float:
    """Calculate distance from a point to the nearest water feature.

    DEPRECATED: Use DistanceCalculator.calculate_water_distance() instead.

    Args:
        tree: Unused (kept for backwards compatibility)
        poi: Tuple of (latitude, longitude)

    Returns:
        Distance to nearest water feature in kilometers
    """
    lat, lon = poi
    return _calculator.calculate_water_distance(lat, lon)


def create_rivertree():
    """Create a spatial index tree (DEPRECATED).

    This function is no longer needed as the new DistanceCalculator
    handles spatial indexing internally.

    Returns:
        None (placeholder for backwards compatibility)
    """
    return None
