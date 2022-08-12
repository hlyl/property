import dao
from dao import Property, Dao
from main import propertyparser
from sqlmodel import Field, SQLModel, create_engine, Session, select  #
from pydantic import condecimal

dbtest = Dao("test.db")


test_data = [
    ("MILAN", "lom", "MI"),
]

for name, region, province in test_data:
    test_file = open("json_mock_file.json")
    web_result = propertyparser(test_file, name)
    id_list = []
