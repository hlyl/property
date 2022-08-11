import dao
from main import propertyparser
from sqlmodel import Field, SQLModel, create_engine, Session, select  #
from pydantic import condecimal


sqlite_file_name = "test.db"  #
sqlite_url = f"sqlite:///{sqlite_file_name}"  #
engine = create_engine(sqlite_url, echo=True)  #


def create_db_and_tables():  #
    SQLModel.metadata.create_all(engine)  #


if __name__ == "__main__":  #
    dao.create_db_and_tables()

test_data = [
    ("MILAN", "lom", "MI"),
]

for name, region, province in test_data:
    test_file = open("json_mock_file.json")
    web_result = propertyparser(test_file, name)
    id_list = []
