def test_deserialise_property():
    # Test with a valid item and region.
    item = {
        "realEstate": {
            "id": 1,
            "isNew": True,
            "price": {"value": 1000},
            "properties": [
                {
                    "category": {"name": "Test Category"},
                    "description": "Test Description",
                    "floor": {"value": 2},
                    "location": {
                        "longitude": 10.0,
                        "latitude": 20.0,
                        "marker": "Test Marker",
                    },
                    "multimedia": {"photos": [{"urls": {"small": "test.jpg"}}]},
                    "rooms": 3,
                    "surface": "50 sqm",
                    "bathrooms": 2,
                }
            ],
            "title": "Test Caption",
        },
        "description": "Test Description",
    }
    region = "Test Region"
    property_ = deserialise_property(item=item, region=region)
    assert isinstance(property_, Property)

    # Test with missing/invalid fields in the item dictionary.
    item = {
        "realEstate": {
            "id": 1,
            "properties": [
                {"category": {"name": "Test Category"}},
            ],
        },
    }
    region = "Test Region"
    with pytest.raises(KeyError):
        property_ = deserialise_property(item=item, region=region)

    # Test with None as an input value.
    item = None
    region = "Test Region"
    with pytest.raises(TypeError):
        property_ = deserialise_property(item=item, region=region)

    # Test with incorrect data types for input values.
    item = {
        "realEstate": {
            "id": 1,
            "isNew": "yes",
            "price": {"value": "1000"},
            "properties": [
                {
                    "category": {"name": "Test Category"},
                    "description": "Test Description",
                    "floor": {"value": True},
                    "location": {
                        "longitude": "10.0",
                        "latitude": "20.0",
                        "marker": "Test Marker",
                    },
                    "multimedia": {"photos": [{"urls": {"small": "test.jpg"}}]},
                    "rooms": "Three",
                    "surface": "50",
                    "bathrooms": "Two",
                }
            ],
            "title": "Test Caption",
        },
        "description": "Test Description",
    }
    region = "Test Region"
    with pytest.raises((TypeError, AttributeError)):
        property_ = deserialise_property(item=item, region=region)
