# source /home/hlynge/dev/property/venv/bin/activate
# http://20.105.249.39:4444/
import os
from fnmatch import translate
from googleplaces import GooglePlaces, types, lang
import requests
import json
import dao
from dao import Property
from sqlmodel import Field, create_engine, Session, select, update  #
from typing import List
import calcdist
from calcdist import create_rivertree, calc_dist_short, calc_dist_water
from datetime import date
from googletrans import Translator

translator = Translator()

production = True
google_api = False
tree = calcdist.create_rivertree()


def deserialise_property(item, region) -> Property:
    stringid = item["realEstate"]["id"]
    is_new = item["realEstate"]["isNew"]
    price = item["realEstate"]["price"]["value"]
    price_drop = item["realEstate"]["price"]["loweredPrice"]
    if price_drop is None:
        price_drop = "No"
    else:
        print("WE have a PriceDrop")
        price_drop = item["realEstate"]["price"]["loweredPrice"]["originalPrice"]
        print("The orginal price was: " + str(price_drop))
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
    price_m = round(price / int(surface.split()[0]))
    lon = item["realEstate"]["properties"][0]["location"]["longitude"]
    lat = item["realEstate"]["properties"][0]["location"]["latitude"]
    marker = item["realEstate"]["properties"][0]["location"]["marker"]
    aphoto = []
    for photo in item["realEstate"]["properties"][0]["multimedia"]["photos"]:
        url = photo["urls"]["small"]
        url = url.replace("xxs-c.jpg", "xxl.jpg")
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
        "price_m": price_m,
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
    for dic in result_list_of_dict:
        dic["discription"] = str(dic["discription"]).replace("\n", " ")
        dic["discription"] = str(dic["discription"]).replace("  ", " ")
        totranslatestr = dic["discription"]
        dic["discription_dk"] = (translator.translate(totranslatestr, "da")).text

    for dic in result_list_of_dict:
        statement = (
            update(Property)
            .values(discription_dk=dic["discription_dk"])
            .where(Property.id == dic["id"])
        )
        session.execute(statement)
    session.commit()
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


def count_bars(item: Property, google_places: GooglePlaces) -> Property:
    bar_query = google_places.nearby_search(
        lat_lng={"lat": float(item.latitude), "lng": float(item.longitude)},
        radius=2000,
        types=[types.TYPE_BAR] or [types.TYPE_CAFE],
    )
    bar_count = len(bar_query.places)
    item.pub_count = bar_count
    return item


def count_shop(item: Property, google_places: GooglePlaces) -> Property:
    shop_query = google_places.nearby_search(
        lat_lng={"lat": float(item.latitude), "lng": float(item.longitude)},
        radius=2000,
        types=[types.TYPE_GROCERY_OR_SUPERMARKET] or [types.TYPE_STORE],
    )
    shop_count = len(shop_query.places)
    item.shopping_count = shop_count
    return item


def count_bakery(item: Property, google_places: GooglePlaces) -> Property:
    bakery_query = google_places.nearby_search(
        lat_lng={"lat": float(item.latitude), "lng": float(item.longitude)},
        radius=2000,
        types=[types.TYPE_BAKERY],
    )
    bakery_count = len(bakery_query.places)
    item.baker_count = bakery_count
    return item


def count_food(item: Property, google_places: GooglePlaces) -> Property:
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
    api_key = os.environ["API_KEY"]

    google_places = GooglePlaces(api_key)
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
        first_observed = {}
        first_observed = json.loads(open("first_observed.json").read())
    else:
        db_engine = dao.create_db("test.db")
        data = [
            ("MILAN", "lom", "MI"),
        ]

    # "https://www.immobiliare.it/api-next/search-list/real-estates/?fkRegione=emi&idProvincia=BO&idNazione=IT&idContratto=1&idCategoria=1&prezzoMinimo=10000&prezzoMassimo=50000&idTipologia[0]=7&idTipologia[1]=31&idTipologia[2]=11&idTipologia[3]=12&idTipologia[4]=13&idTipologia[5]=4&localiMinimo=3&localiMassimo=5&bagni=1&boxAuto[0]=4&cantina=1&noAste=1&pag=1&paramsCount=17&path=%2Fen%2Fsearch-list%2F"
    total_count = 0
    print(first_observed)
    for name, region, province in data:
        print(name)
        page = 0
        while True:
            page = page + 1
            url = f"https://www.immobiliare.it/api-next/search-list/real-estates/?fkRegione={region}&idProvincia={province}&idNazione=IT&idContratto=1&idCategoria=1&prezzoMinimo=10000&prezzoMassimo=50000&idTipologia[0]=7&idTipologia[1]=31&idTipologia[2]=11&idTipologia[3]=12&idTipologia[4]=13&idTipologia[5]=4&localiMinimo=3&localiMassimo=5&bagni=1&boxAuto[0]=4&cantina=1&noAste=1&pag={page}&paramsCount=17&path=%2Fen%2Fsearch-list%2F"
            response = requests.get(url)
            input_json = response.json()
            pages = input_json["maxPages"]
            count = input_json["count"]
            web_result = propertyparser(input_json, name)
            id_list = []
            with Session(db_engine) as session:
                exist_id = get_list_id(session)
                for item in web_result:
                    first_observed.setdefault(item.id, str(date.today()))
                    if item.id not in exist_id:
                        if google_api:
                            count_bars(item, google_places)
                            count_shop(item, google_places)
                            count_bakery(item, google_places)
                            count_food(item, google_places)
                        if item.latitude != None and item.longitude != None:
                            calc_dist_cost(item)
                            calc_dist_water_main(item)
                        item.observed = str(date.today())
                        session.merge(item)
                    id_list.append(item.id)
                session.commit()
                print("We have committed : " + name + " - page: " + str(page))
                update_sold(session, name, id_list)
                to_translate = select_db_no_translation(session)
            if page == pages or count == 0 or response.status_code != 200:
                total_count = total_count + count
                print("Property count :" + str(total_count))
                print("we are in the break")
                break
    out_file = open("first_observed.json", "w+")
    new_today = [
        key for key, value in first_observed.items() if value == str(date.today())
    ]
    print(len(new_today))
    json.dump(first_observed, out_file)
