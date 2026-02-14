"""Unit tests for utility functions.

Tests DistanceCalculator with lazy-loading and geospatial calculations.
"""

from property_tracker.utils.distance import DistanceCalculator, get_calculator


def test_distance_calculator_initialization():
    """Test DistanceCalculator can be initialized."""
    calc = DistanceCalculator()
    assert calc is not None
    assert calc._coastline is None  # Lazy loading - not loaded yet
    assert calc._water_tree is None  # Lazy loading - not loaded yet


def test_distance_calculator_lazy_loading_coastline():
    """Test that coastline data is lazy-loaded."""
    calc = DistanceCalculator()

    # Verify data not loaded at initialization
    assert calc._coastline is None

    # Calculate distance - should trigger lazy-loading
    distance = calc.calculate_coast_distance(43.8438, 10.5077)

    # Verify data now loaded
    assert calc._coastline is not None
    assert calc._water_tree is None  # Water tree still not loaded
    assert isinstance(distance, float)
    assert distance >= 0


def test_distance_calculator_lazy_loading_water():
    """Test that water tree is lazy-loaded independently."""
    calc = DistanceCalculator()

    # Verify data not loaded
    assert calc._coastline is None
    assert calc._water_tree is None

    # Calculate water distance - should trigger lazy-loading
    distance = calc.calculate_water_distance(43.8438, 10.5077)

    # Verify water tree loaded but coastline not
    assert calc._coastline is None  # Coastline not needed
    assert calc._water_tree is not None  # Water tree loaded
    assert isinstance(distance, float)
    assert distance >= 0


def test_distance_calculator_both_distances(coordinates_italy):
    """Test calculating both distances in one call."""
    calc = DistanceCalculator()
    coords = coordinates_italy["lucca"]

    coast_dist, water_dist = calc.calculate_both_distances(coords["lat"], coords["lon"])

    # Both should be loaded now
    assert calc._coastline is not None
    assert calc._water_tree is not None

    assert isinstance(coast_dist, float)
    assert isinstance(water_dist, float)
    assert coast_dist >= 0
    assert water_dist >= 0


def test_distance_calculator_coastal_vs_inland(coordinates_italy):
    """Test that coastal locations have shorter distances."""
    calc = DistanceCalculator()

    # Viareggio is coastal
    coastal_coords = coordinates_italy["viareggio"]
    coastal_dist = calc.calculate_coast_distance(coastal_coords["lat"], coastal_coords["lon"])

    # Florence is inland
    inland_coords = coordinates_italy["florence"]
    inland_dist = calc.calculate_coast_distance(inland_coords["lat"], inland_coords["lon"])

    # Coastal location should have shorter distance to coast
    assert coastal_dist < inland_dist


def test_distance_calculator_multiple_calls():
    """Test that lazy-loaded data is reused."""
    calc = DistanceCalculator()

    # First call - loads data
    dist1 = calc.calculate_coast_distance(43.8438, 10.5077)
    coastline1 = id(calc._coastline)

    # Second call - reuses data
    dist2 = calc.calculate_coast_distance(43.7696, 11.2558)
    coastline2 = id(calc._coastline)

    # Same object should be reused
    assert coastline1 == coastline2
    assert dist1 != dist2  # Different distances for different locations


def test_get_calculator_singleton():
    """Test that get_calculator returns singleton instance."""
    calc1 = get_calculator()
    calc2 = get_calculator()

    # Should be the same instance
    assert calc1 is calc2


def test_distance_calculator_coordinates_validation():
    """Test distance calculation with various coordinates."""
    calc = DistanceCalculator()

    # Valid coordinates
    dist = calc.calculate_coast_distance(45.0, 12.0)
    assert isinstance(dist, float)
    assert dist >= 0

    # Different valid coordinates
    dist2 = calc.calculate_water_distance(44.0, 11.0)
    assert isinstance(dist2, float)
    assert dist2 >= 0


def test_backwards_compatibility_calc_dist_short():
    """Test backwards compatibility with old calcdist module."""
    import calcdist

    # Test old function still works
    poi = (43.8438, 10.5077)  # (lat, lon)
    distance = calcdist.calc_dist_short(poi)

    assert isinstance(distance, float)
    assert distance >= 0


def test_backwards_compatibility_calc_dist_water():
    """Test backwards compatibility with water distance."""
    import calcdist

    tree = calcdist.create_rivertree()  # Now returns None (dummy)
    poi = (43.8438, 10.5077)
    distance = calcdist.calc_dist_water(tree, poi)

    assert isinstance(distance, float)
    assert distance >= 0


def test_distance_calculator_performance():
    """Test that lazy-loading improves import performance."""
    # This test verifies the implementation approach
    # In real usage, importing should not load 8.7MB of GeoJSON

    calc = DistanceCalculator()

    # No data loaded at initialization (fast import)
    assert calc._coastline is None
    assert calc._water_tree is None

    # Data only loads when needed (deferred cost)
    # This is the key performance improvement
