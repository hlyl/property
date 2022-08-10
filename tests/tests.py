from import Dao

sqlite_file_name = "test.db"  #
sqlite_url = f"sqlite:///{sqlite_file_name}"  #
engine = create_engine(sqlite_url, echo=True)  #

def create_db_and_tables():  #
    SQLModel.metadata.create_all(engine)  #

test_data = [
    ("MILAN", "lom", "MI"),
]

for name, region, province in test_data:
    test_file = open("testitem.json")
    web_result = propertyparser(test_file, name)
    id_list = []