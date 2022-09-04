import os
import string
from typing import Optional
import json
import requests
from typing import List
from sqlmodel import SQLModel, Field, create_engine, Session, select, update  #
from googleplaces import GooglePlaces, types
import calcdist
from calcdist import create_rivertree, calc_dist_short, calc_dist_water


tree = calcdist.create_rivertree()


class Property(SQLModel, table=True):  #
    id: Optional[int] = Field(default=None, primary_key=True)  #
    region: str
    is_new: Optional[int] = None
    price: Optional[int] = None
    price_drop: Optional[str] = None
    bathrooms: Optional[str]
    caption: Optional[str]
    category: str
    discription: str
    discription_dk: str
    floor: Optional[str]
    rooms: Optional[str]
    surface: Optional[str]
    price_m: Optional[int]
    longitude: Optional[str]
    latitude: Optional[str]
    marker: Optional[str]
    photo_list: str
    dist_coast: Optional[str]
    dist_water: Optional[str]
    shopping_count: Optional[int]
    pub_count: Optional[int]
    baker_count: Optional[int]
    food_count: Optional[int]
    sold: int = 0
    observed: Optional[str]


class Google_Place(SQLModel, table=True):  #
    stringid: Optional[int] = Field(default=None, primary_key=True)  #
    name: str
    rating: Optional[str] = None
    type_list: str


def deserialise_googleplaces(place) -> Google_Place:
    stringid = place["place_id"]
    name = place["name"]
    rating = place.get("rating", "No")
    a_types = []
    for type in place["types"]:
        a_types.append(type)
    type_list = json.dumps(a_types)

    place = {
        "id": stringid,
        "name": name,
        "rating": rating,
        "type_list": type_list,
    }
    return Google_Place(**place)


def Google_Placeparser(results) -> List[Google_Place]:
    aresults = []
    for json in results["results"]:
        item = deserialise_googleplaces(json)
        aresults.append(item)
    return aresults


def create_db(db_name):
    engine = create_engine(f"sqlite:///{db_name}")
    SQLModel.metadata.create_all(engine)
    return engine


def call_googleapi(
    lat: float, lng: float, radius: int, type: string, api_key: string
) -> int:
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lng}%2C{lat}&radius={radius}&types={type}&key={api_key}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    input_json = response.json()
    print("The count is: " + str(len(input_json["results"])))
    return len(input_json["results"])


def update_counts(session, api_key):
    statement = select(
        Property.id,
        Property.longitude,
        Property.latitude,
        Property.shopping_count,
        Property.pub_count,
        Property.baker_count,
        Property.food_count,
    ).where(Property.longitude != None)
    out = session.execute(statement)
    result_list_of_dict = [
        {
            "id": col1,
            "longitude": float(col2),
            "latitude": float(col3),
            "shopping_count": col4,
            "pub_count": col5,
            "baker_count": col6,
            "food_count": col7,
        }
        for (col1, col2, col3, col4, col5, col6, col7) in out.fetchall()
    ]
    for dic in result_list_of_dict:
        dic["shopping_count"] = call_googleapi(
            dic["longitude"], dic["latitude"], 2000, "supermarket", api_key
        )
        dic["pub_count"] = call_googleapi(
            dic["longitude"], dic["latitude"], 2000, "bar", api_key
        )
        dic["baker_count"] = call_googleapi(
            dic["longitude"], dic["latitude"], 2000, "baker", api_key
        )
        dic["food_count"] = call_googleapi(
            dic["longitude"], dic["latitude"], 2000, "restaurant", api_key
        )
        statement = (
            update(Property)
            .values(shopping_count=dic["shopping_count"])
            .values(pub_count=dic["pub_count"])
            .values(baker_count=dic["baker_count"])
            .values(food_count=dic["food_count"])
            .where(Property.id == dic["id"])
        )
        session.execute(statement)
    session.commit()
    return result_list_of_dict


if __name__ == "__main__":
    api_key = os.environ["API_KEY"]
    db_engine = create_db("database.db")
    with Session(db_engine) as session:
        exist_id = update_counts(session, api_key)
