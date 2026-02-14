"""Backwards compatibility shim for calcdist module.

This module provides backwards compatibility by re-exporting functions
from utils.calcdist which delegates to property_tracker.utils.distance.

DEPRECATED: Use property_tracker.utils.distance.DistanceCalculator instead.
"""

# Re-export everything from utils.calcdist for backwards compatibility
from utils.calcdist import calc_dist_short, calc_dist_water, create_rivertree

__all__ = ['calc_dist_short', 'calc_dist_water', 'create_rivertree']
