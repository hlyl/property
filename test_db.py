import dao
import json
import main
from main import propertyparser, calc_dist_cost
from sqlmodel import Field, SQLModel, create_engine, Session, select  #
from pydantic import condecimal

test_data = [
    ("MILAN", "lom", "MI"),
]


def id_test(item):
    item_id = str(item.id)
    assert item_id == "94471966"


def test_1():
    for name, region, province in test_data:
        print(name)
        with open("json_mock_file.json") as test_file:
            web_result = propertyparser(json.load(test_file), name)
            for item in web_result:
                item_id = str(item.id)
                id_test(item)
                assert item.region == "MILAN"
                assert item.category == "Residenziale"
                test_dist_cost = calc_dist_cost(item)
                assert str(test_dist_cost.dist_coast) == "94.92"


def test_main():
    test_1()
