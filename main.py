# source /home/hlynge/dev/property/venv/bin/activate

import datetime
from tokenize import String
from bs4 import BeautifulSoup
import asyncio
from googleplaces import GooglePlaces, types, lang
import requests
import json
import pandas
import dao
from dao import Property
from sqlmodel import Field, SQLModel, create_engine, Session, select, update  #
from typing import List
import calcdist
from calcdist import create_rivertree, calc_dist_short, calc_dist_water
from datetime import date

production = True
google_api = False
API_KEY = open("apiKey.txt", "r").read()
API_KEY = ""
tree = calcdist.create_rivertree()


def deserialise_property(item, region) -> Property:
    stringid = item["realEstate"]["id"]
    is_new = item["realEstate"]["isNew"]
    price = item["realEstate"]["price"]["value"]
    price_drop = item["realEstate"]["price"]["loweredPrice"]
    bathrooms = item["realEstate"]["properties"][0]["bathrooms"]
    caption = item["realEstate"]["properties"][0]["caption"]
    category = item["realEstate"]["properties"][0]["category"]["name"]
    discription = item["realEstate"]["properties"][0]["description"]
    discription_dk = ""
    floor = item["realEstate"]["properties"][0]["floor"]
    if floor is None:
        floor = "not assigned"
    else:
        floor = item["realEstate"]["properties"][0]["floor"]["value"]
    rooms = item["realEstate"]["properties"][0]["rooms"]
    surface = item["realEstate"]["properties"][0]["surface"]
    lon = item["realEstate"]["properties"][0]["location"]["longitude"]
    lat = item["realEstate"]["properties"][0]["location"]["latitude"]
    marker = item["realEstate"]["properties"][0]["location"]["marker"]
    aphoto = []
    for photo in item["realEstate"]["properties"][0]["multimedia"]["photos"]:
        url = photo["urls"]["small"]
        aphoto.append(url)
    photo_list = json.dumps(aphoto)

    item = {
        "region": region,
        "id": stringid,
        "is_new": is_new,
        "price": price,
        "price_drop": price_drop,
        "bathrooms": bathrooms,
        "caption": caption,
        "category": category,
        "discription": discription,
        "discription_dk": discription_dk,
        "floor": floor,
        "rooms": rooms,
        "surface": surface,
        "longitude": lon,
        "latitude": lat,
        "marker": marker,
        "photo_list": photo_list,
    }
    return Property(**item)


def propertyparser(results, region) -> List[Property]:
    aresults = []
    for json in results["results"]:
        item = deserialise_property(json, region)
        aresults.append(item)
    return aresults


def updateTest():
    prop_1 = Property(
        id=12345678,
        region="TOSCANA",
        caption="This is a test House",
        category="Apartment",
        discription="The discription of the test House",
    )
    with Session(db_engine) as session:
        session.add(prop_1)
        session.commit()


def select_db_region(region):
    with Session(db_engine) as session:
        statement = select(Property).where(Property.region == region)
        out = session.execute(statement)
        return list(out)


def exist_db_property(id) -> bool:
    with Session(db_engine) as session:
        statement = select(Property.id).where(Property.id == id)
        data = session.execute(statement)
        if data == None:
            return True
        else:
            return False


def select_db_no_translation(session) -> dict:
    statement = select(
        Property.id, Property.discription, Property.discription_dk
    ).where(Property.discription_dk == "")
    out = session.execute(statement)
    result_list_of_dict = [
        {"id": col1, "discription": col2, "discription_dk": col3}
        for (col1, col2, col3) in out.fetchall()
    ]
    return result_list_of_dict


def get_list_id(sesson) -> list:
    statement = select(Property.id)
    data = session.execute(statement)
    resultlst = [i[0] for i in data]
    return resultlst


def update_observed(session):
    statement = (
        update(Property)
        .values(observed=str(date.today()))
        .where(Property.observed == None)
    )
    session.execute(statement)
    session.commit()


def update_sold(session, region, id_list):
    statement = (
        update(Property)
        .values(sold=1)
        .where(Property.region == region)
        .where(~Property.id.in_(id_list))
    )
    session.execute(statement)
    session.commit()


def calc_dist_cost(item: Property) -> Property:
    lat_input = float(item.latitude)
    long_input = float(item.longitude)
    poi = [lat_input, long_input]
    try:
        dist_coast = calcdist.calc_dist_short(poi)
    except:
        dist_coast = -1
    item.dist_coast = round(dist_coast, 2)
    return item


def calc_dist_water_main(item: Property) -> Property:
    lat_input = float(item.latitude)
    long_input = float(item.longitude)
    poi = [lat_input, long_input]
    try:
        dist_water = calcdist.calc_dist_water(tree, poi)
    except:
        dist_water = -1
    item.dist_water = round(dist_water, 2)
    return item


def count_bars(item: Property) -> Property:
    google_places = GooglePlaces(API_KEY)
    bar_query = google_places.nearby_search(
        lat_lng={"lat": float(item.latitude), "lng": float(item.longitude)},
        radius=2000,
        types=[types.TYPE_BAR] or [types.TYPE_CAFE],
    )
    bar_count = len(bar_query.places)
    item.pub_count = bar_count
    return item


def count_shop(item: Property) -> Property:
    google_places = GooglePlaces(API_KEY)
    shop_query = google_places.nearby_search(
        lat_lng={"lat": float(item.latitude), "lng": float(item.longitude)},
        radius=2000,
        types=[types.TYPE_GROCERY_OR_SUPERMARKET] or [types.TYPE_STORE],
    )
    shop_count = len(shop_query.places)
    item.shopping_count = shop_count
    return item


def count_bakery(item: Property) -> Property:
    google_places = GooglePlaces(API_KEY)
    bakery_query = google_places.nearby_search(
        lat_lng={"lat": float(item.latitude), "lng": float(item.longitude)},
        radius=2000,
        types=[types.TYPE_BAKERY],
    )
    bakery_count = len(bakery_query.places)
    item.baker_count = bakery_count
    return item


def count_food(item: Property) -> Property:
    google_places = GooglePlaces(API_KEY)
    food_query = google_places.nearby_search(
        lat_lng={"lat": float(item.latitude), "lng": float(item.longitude)},
        radius=2000,
        types=[types.TYPE_RESTAURANT] or [types.TYPE_FOOD],
    )
    food_count = len(food_query.places)
    item.food_count = food_count
    return item


def get_list_id(session) -> list:
    statement = select(Property.id)
    data = session.execute(statement)
    resultlst = [i[0] for i in data]
    return resultlst


if __name__ == "__main__":  #

    if production:
        db_engine = dao.create_db("database.db")
        data = [
            ("LUCCA", "tos", "LU"),
            ("PISA", "tos", "PI"),
            ("LEGHORN", "tos", "LI"),
            ("VENICE", "ven", "VE"),
            ("TREVISO", "ven", "TV"),
            ("PORDENONE", "fri", "PN"),
            ("PADUA", "ven", "PD"),
            ("ROViGO", "ven", "RO"),
            ("BOLOGNA", "emi", "BO"),
            ("MILAN", "lom", "MI"),
        ]
    else:
        db_engine = dao.create_db("test.db")
        data = [
            ("MILAN", "lom", "MI"),
        ]

    # "https://www.immobiliare.it/api-next/search-list/real-estates/?fkRegione=lom&idProvincia=MI&idNazione=IT&idContratto=1&idCategoria=1&prezzoMinimo=10000&prezzoMassimo=30000&idTipologia[0]=7&idTipologia[1]=31&idTipologia[2]=11&idTipologia[3]=12&idTipologia[4]=13&idTipologia[5]=4&localiMinimo=3&localiMassimo=5&bagni=1&boxAuto[0]=4&cantina=1&noAste=1&pag=1&paramsCount=17&path=%2Fen%2Fsearch-list%2F"

    for name, region, province in data:
        print(name)
        url = f"https://www.immobiliare.it/api-next/search-list/real-estates/?fkRegione={region}&idProvincia={province}&idNazione=IT&idContratto=1&idCategoria=1&prezzoMinimo=10000&prezzoMassimo=50000&idTipologia[0]=7&idTipologia[1]=31&idTipologia[2]=11&idTipologia[3]=12&idTipologia[4]=13&idTipologia[5]=4&localiMinimo=3&localiMassimo=5&bagni=1&boxAuto[0]=4&cantina=1&noAste=1&pag=1&paramsCount=17&path=%2Fen%2Fsearch-list%2F"
        response = requests.get(url)
        web_result = propertyparser(response.json(), name)
        id_list = []
        with Session(db_engine) as session:
            exist_id = get_list_id(session)
            print(exist_id)
            for item in web_result:
                if item.id not in exist_id:
                    if google_api:
                        count_bars(item)
                        count_shop(item)
                        count_bakery(item)
                        count_food(item)
                    if item.latitude != None and item.longitude != None:
                        calc_dist_cost(item)
                        calc_dist_water_main(item)
                    item.observed = str(date.today())
                id_list.append(item.id)
                session.merge(item)
            session.commit()
            update_sold(session, name, id_list)
            to_translate = select_db_no_translation(session)
            print(to_translate)
