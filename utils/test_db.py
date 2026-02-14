import json
import os

import pytest

from main import calc_dist_cost, propertyparser

# Import new services for testing
from poi_service import OverpassPOIService, POICounts
from translation_service import DeepTranslatorService

test_data = [
    ("MILAN", "lom", "MI"),
]


def id_test(item):
    item_id = str(item.id)
    assert item_id == "94471966"


def test_1():
    for name, _region, _province in test_data:
        print(name)
        with open("json_mock_file.json") as test_file:
            web_result = propertyparser(json.load(test_file), name)
            for item in web_result:
                str(item.id)
                id_test(item)
                assert item.region == "MILAN"
                assert item.category == "Residenziale"
                test_dist_cost = calc_dist_cost(item)
                assert str(test_dist_cost.dist_coast) == "94.92"


@pytest.mark.skipif(
    os.getenv("SKIP_OVERPASS_TESTS") == "true",
    reason="Overpass API tests are slow (network calls)",
)
def test_overpass_poi_service():
    """Test Overpass API POI counting service."""
    service = OverpassPOIService()

    # Test location: Lucca city center (known to have amenities)
    counts = service.get_all_counts(lat=43.8438, lon=10.5077, radius=1000)

    # Verify we got POICounts dataclass
    assert isinstance(counts, POICounts)

    # Verify all counts are non-negative integers
    assert counts.bars >= 0
    assert counts.shops >= 0
    assert counts.bakeries >= 0
    assert counts.restaurants >= 0

    print(f"Overpass API test results: {counts}")


def test_translation_service():
    """Test deep-translator translation service."""
    service = DeepTranslatorService(service="google")

    # Test simple Italian to Danish translation
    italian_text = "Bella casa con giardino"
    result = service.translate(italian_text)

    # Should return some text (not empty)
    assert len(result) > 0
    assert isinstance(result, str)

    # Test with empty string
    empty_result = service.translate("")
    assert empty_result == ""

    print(f"Translation test: '{italian_text}' -> '{result}'")


def test_translation_service_chunking():
    """Test translation service handles long text by chunking."""
    service = DeepTranslatorService(service="google")

    # Create a long text (over 4500 chars)
    long_text = "Questa è una bella casa. " * 200  # ~5000 chars

    result = service.translate(long_text)

    # Should return chunked translation
    assert len(result) > 0
    assert isinstance(result, str)

    print(f"Long text translation: {len(long_text)} chars -> {len(result)} chars")


def test_main():
    test_1()

