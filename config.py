"""Configuration module for loading environment variables.

This module provides centralized configuration management for the application.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "database.db")
TEST_DATABASE_PATH = os.getenv("TEST_DATABASE_PATH", "test.db")
DB_SELECTOR = os.getenv("DB_SELECTOR", "test").strip().lower()

# Application Settings
PRODUCTION = os.getenv("PRODUCTION", "true").lower() == "true"
LOG_FILE = os.getenv("LOG_FILE", "logging.txt")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Feature Flags
USE_GOOGLE_PLACES = os.getenv("USE_GOOGLE_PLACES", "false").lower() == "true"
USE_GOOGLE_TRANSLATE = os.getenv("USE_GOOGLE_TRANSLATE", "false").lower() == "true"

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# POI Search Configuration
POI_SEARCH_RADIUS = int(os.getenv("POI_SEARCH_RADIUS", "2000"))
POI_SEARCH_PROVIDER = os.getenv("POI_SEARCH_PROVIDER", "overpass")

# Translation Configuration
TRANSLATION_BATCH_SIZE = int(os.getenv("TRANSLATION_BATCH_SIZE", "50"))
TRANSLATION_SOURCE_LANG = os.getenv("TRANSLATION_SOURCE_LANG", "it")
TRANSLATION_TARGET_LANG = os.getenv("TRANSLATION_TARGET_LANG", "da")


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


def get_database_url(use_test_db: Optional[bool] = None):
    """Get the database URL for SQLAlchemy/SQLModel.

    Args:
        use_test_db: Optional override; if omitted, read from DB_SELECTOR env var

    Returns:
        str: SQLite database URL
    """
    if use_test_db is None:
        use_test_db = use_test_database()

    db_path = TEST_DATABASE_PATH if use_test_db else DATABASE_PATH
    return f"sqlite:///{db_path}"
