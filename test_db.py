import dao
import json
import main
from main import propertyparser
from sqlmodel import Field, SQLModel, create_engine, Session, select  #
from pydantic import condecimal

test_data = [
    ("MILAN", "lom", "MI"),
]

print("We are in the test")
assert 1 == 1


def test_1():
    print("We are in the test")
    for name, region, province in test_data:
        print("We are in the test function.")
        print(name)
        with open("json_mock_file.json") as test_file:
            web_result = propertyparser(json.load(test_file), name)
            print(web_result)
