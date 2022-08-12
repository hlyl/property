import dao
import json
import main
from main import propertyparser, Property, item, db_engine
from sqlmodel import Field, SQLModel, create_engine, Session, select  #
from pydantic import condecimal

test_data = [
    ("MILAN", "lom", "MI"),
]

for name, region, province in test_data:
    print("We are in the test function.")
    print(name)
    with open("json_mock_file.json") as test_file:
        web_result = propertyparser(json.load(test_file), name)
        id_list = []
        with Session(db_engine) as session:
            for item in web_result:
                if item.latitude != None and item.longitude != None:
                    if item.dist_coast == None:
                        calc_dist_cost(item)
                    if item.pub_count == None:
                        count_bars(item)
                    if item.shopping_count == None:
                        count_shop(item)
                    if item.baker_count == None:
                        count_bakery(item)
                    if item.food_count == None:
                        count_food(item)
                else:
                    item.dist_coast = -1
                    item.pub_count = -1
                    item.shopping_count = -1
                    item.baker_count = -1
                    item.food_count = -1
                id_list.append(item.id)
                session.merge(item)
            session.commit()
            update_sold(session, name, id_list)
            update_observed(session)
            to_translate = select_db_no_translation()
            for element in to_translate:
                print(element)
