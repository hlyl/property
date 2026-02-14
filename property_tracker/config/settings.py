"""Centralized configuration management for the Property Tracker application.

This module loads environment variables from .env file and provides
configuration constants for database, API, file paths, and feature flags.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory (3 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# ==============================================================================
# Database Configuration
# ==============================================================================
DATABASE_PATH = os.getenv("DATABASE_PATH", "database.db")
TEST_DATABASE_PATH = os.getenv("TEST_DATABASE_PATH", "test.db")
DB_SELECTOR = os.getenv("DB_SELECTOR", "test").strip().lower()


def use_test_database() -> bool:
    """Return True when DB_SELECTOR points to test DB.

    Accepted test values: "test", "testing"
    Accepted production values: "prod", "production"
    Defaults to test DB for unknown values.
    """
    if DB_SELECTOR in {"prod", "production"}:
        return False
    if DB_SELECTOR in {"test", "testing"}:
        return True
    return True


def get_database_url(use_test_db: bool | None = None) -> str:
    """Get SQLAlchemy database URL.

    Args:
        use_test_db: Optional override; if omitted, read from DB_SELECTOR env var

    Returns:
        SQLite database URL string
    """
    if use_test_db is None:
        use_test_db = use_test_database()

    db_path = TEST_DATABASE_PATH if use_test_db else DATABASE_PATH
    return f"sqlite:///{db_path}"


# ==============================================================================
# Data File Paths
# ==============================================================================
DATA_DIR = PROJECT_ROOT / "data"
BOUNDARIES_DIR = DATA_DIR / "boundaries"

# Geospatial data files
COASTLINE_PATH = BOUNDARIES_DIR / "ITA_coastline.json"
WATERLINES_PATH = BOUNDARIES_DIR / "ITA_water_lines.json"

# ==============================================================================
# API Configuration
# ==============================================================================
IMMOBILIARE_BASE_URL = "https://www.immobiliare.it"

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ==============================================================================
# POI (Points of Interest) Configuration
# ==============================================================================
POI_SEARCH_RADIUS = int(os.getenv("POI_SEARCH_RADIUS", "2000"))  # meters
POI_SEARCH_PROVIDER = os.getenv("POI_SEARCH_PROVIDER", "overpass")  # "overpass" or "google"

# ==============================================================================
# Translation Configuration
# ==============================================================================
TRANSLATION_BATCH_SIZE = int(os.getenv("TRANSLATION_BATCH_SIZE", "50"))
TRANSLATION_SOURCE_LANG = os.getenv("TRANSLATION_SOURCE_LANG", "it")  # Italian
TRANSLATION_TARGET_LANG = os.getenv("TRANSLATION_TARGET_LANG", "da")  # Danish
TRANSLATION_SERVICE = os.getenv("TRANSLATION_SERVICE", "google")  # "google" or "deepl"

# ==============================================================================
# Application Settings
# ==============================================================================
PRODUCTION = os.getenv("PRODUCTION", "true").lower() == "true"
LOG_FILE = os.getenv("LOG_FILE", "logging.txt")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ==============================================================================
# Feature Flags
# ==============================================================================
USE_GOOGLE_PLACES = os.getenv("USE_GOOGLE_PLACES", "false").lower() == "true"
USE_GOOGLE_TRANSLATE = os.getenv("USE_GOOGLE_TRANSLATE", "false").lower() == "true"

# ==============================================================================
# Review Status Constants
# ==============================================================================
REVIEW_STATUS_TO_REVIEW = "To Review"
REVIEW_STATUS_INTERESTED = "Interested"
REVIEW_STATUS_REJECTED = "Rejected"
REVIEW_STATUSES = [REVIEW_STATUS_TO_REVIEW, REVIEW_STATUS_INTERESTED, REVIEW_STATUS_REJECTED]

# ==============================================================================
# Property Category Constants
# ==============================================================================
CATEGORY_RESIDENTIAL = "Residenziale"

# ==============================================================================
# Distance Thresholds (kilometers)
# ==============================================================================
MAX_COAST_DISTANCE = 50.0
MAX_WATER_DISTANCE = 10.0
