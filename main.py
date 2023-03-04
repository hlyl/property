# source /home/hlynge/dev/property/venv/bin/activate
# http://20.105.249.39:4444/
import os
from fnmatch import translate
from googleplaces import GooglePlaces, types
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
google_api = True
tree = calcdist.create_rivertree()


def deserialise_property(item, region) -> Property:
    stringid = item["realEstate"]["id"]
    is_new = item["realEstate"]["isNew"]
    price = item["realEstate"]["price"]["value"]
    price_drop = None
    if price_drop is None:
        price_drop = "No"
    else:
        print("WE have a PriceDrop")
        price_drop = item["realEstate"]["price"]["loweredPrice"]["originalPrice"]
        print("The orginal price was: " + str(price_drop))
    # bathrooms = item["realEstate"]["properties"][0]["bathrooms"]
    bathrooms = item.get("bathrooms", None)
    caption = item["realEstate"]["title"]
    category = item["realEstate"]["properties"][0]["category"]["name"]
    discription = item.get("description", None)
    if discription is None:
        discription = "There is not Discription"
    else:
        discription = item["realEstate"]["properties"][0]["description"]
    discription_dk = ""
    # floor = item["realEstate"]["properties"][0]["floor"]
    floor = item.get("floor", None)
    if floor is None:
        floor = "No Floor has been assigned"
    else:
        floor = item["realEstate"]["properties"][0]["floor"]["value"]
    rooms = item["realEstate"]["properties"][0]["rooms"]
    surface = item["realEstate"]["properties"][0]["surface"]
    if surface is None:
        surface = "1"
    else:
        surface = surface.split()[0]
    surface = surface.replace(",", "")
    price_m = round(price / int(surface))
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


def update_sold1(session):
    statement = update(Property).values(sold=0)
    session.execute(statement)
    session.commit()


def update_sold2(session, first_observed, id_list):
    sold_items = []
    for item in first_observed:
        item_id = str(item)
        if item_id not in id_list:
            sold_items.append(item_id)
    print("Items sold are: ")
    print(sold_items)
    statement = update(Property).values(sold=1).where(Property.id.in_(sold_items))
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
    print("The count of bars is :" + str(bar_count))
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
    from loguru import logger

    logger.add("logging.txt")
    logger.debug("That's it, beautiful and simple logging!")
    api_key = os.environ["API_KEY"]
    google_places = GooglePlaces(api_key)
    if production:
        db_engine = dao.create_db("radius_database.db")
        with open("first_observed.json") as f:
            first_observed = json.load(f)
            print(len(first_observed))
    else:
        db_engine = dao.create_db("test.db")
    # "Test of what branch we are using"
    # "https://www.immobiliare.it/api-next/search-list/real-estates/?fkRegione=tos&idProvincia=LU&idNazione=IT&idContratto=1&idCategoria=1&prezzoMinimo=10000&prezzoMassimo=50000&idTipologia[0]=7&idTipologia[1]=31&idTipologia[2]=11&idTipologia[3]=12&idTipologia[4]=13&idTipologia[5]=4&localiMinimo=3&localiMassimo=5&bagni=1&boxAuto[0]=4&cantina=1&noAste=1&pag=1&paramsCount=17&path=%2Fen%2Fsearch-list%2F"

    # "https://www.immobiliare.it/api-next/search-list/real-estates/?fkRegione=tos&idProvincia=LU&idNazione=IT&idContratto=1&idCategoria=1&prezzoMinimo=10000&prezzoMassimo=50000&idTipologia[0]=7&idTipologia[1]=31&idTipologia[2]=11&idTipologia[3]=12&idTipologia[4]=13&idTipologia[5]=4&localiMinimo=3&localiMassimo=5&bagni=1&boxAuto[0]=4&cantina=1&noAste=1&pag=1&paramsCount=17&path=%2Fen%2Fsearch-list%2F"
    # "https://www.immobiliare.it/api-next/search-list/real-estates/?raggio=300000&centro=44.51456,11.29172&idContratto=1&idCategoria=1&prezzoMinimo=20000&prezzoMassimo=90000&idTipologia[0]=7&idTipologia[1]=31&idTipologia[2]=11&idTipologia[3]=12&idTipologia[4]=13&idTipologia[5]=4&localiMinimo=4&bagni=1&boxAuto[0]=4&cantina=1&noAste=1&criterio=rilevanza&__lang=en&pag=1&paramsCount=11&path=/en/search-list/"
    # The good one:
    # "https://www.immobiliare.it/api-next/search-list/real-estates/?raggio=300000&centro=44.51456%2C11.29172&idContratto=1&idCategoria=1&prezzoMinimo=20000&prezzoMassimo=75000&idTipologia[0]=7&idTipologia[1]=11&idTipologia[2]=12&idTipologia[3]=13&localiMinimo=4&tipoProprieta=1&boxAuto[0]=1&boxAuto[1]=3&giardino[0]=10&giardino[1]=40&giardino[2]=20&criterio=rilevanza&noAste=1&__lang=en&pag=1&paramsCount=15&path=%2Fen%2Fsearch-list%2F"

    # "https://www.immobiliare.it/api-next/search-list/real-estates/?raggio=300000&centro=44.51456,11.29172&idContratto=1&idCategoria=1&prezzoMinimo=20000&prezzoMassimo=90000&idTipologia[0]=7&idTipologia[1]=31&idTipologia[2]=11&idTipologia[3]=12&idTipologia[4]=13&idTipologia[5]=4&localiMinimo=4&criterio=rilevanza&__lang=en&pag=1&paramsCount=11&path=/en/search-list/"

    # "https://www.immobiliare.it/api-next/search-list/real-estates/?raggio=200000&centro=44.339565,7.9953&idContratto=1&idCategoria=1&prezzoMinimo=20000&prezzoMassimo=90000&localiMinimo=4&criterio=rilevanza&__lang=en&pag=1&paramsCount=11&path=/en/search-list/"
    total_count = 0
    id_list = []
    print("Running")
    page = 0
    name = "Radius"
    region = "Radius"
    while True:
        page = page + 1
        #        url = f"https://www.immobiliare.it/api-next/search-list/real-estates/?raggio=300000&centro=44.51456%2C11.29172&idContratto=1&idCategoria=1&prezzoMinimo=20000&prezzoMassimo=75000&idTipologia[0]=7&idTipologia[1]=11&idTipologia[2]=12&idTipologia[3]=13&localiMinimo=4&tipoProprieta=1&boxAuto[0]=1&boxAuto[1]=3&giardino[0]=10&giardino[1]=40&giardino[2]=20&criterio=rilevanza&noAste=1&__lang=en&pag={page}&paramsCount=15&path=%2Fen%2Fsearch-list%2F"
        url = f"https://www.immobiliare.it/api-next/search-list/real-estates/?raggio=300000&centro=44.51456%2C11.29172&idContratto=1&idCategoria=1&prezzoMinimo=20000&prezzoMassimo=75000&superficieMinima=200&idTipologia[0]=7&idTipologia[1]=11&idTipologia[2]=12&idTipologia[3]=13&localiMinimo=4&tipoProprieta=1&boxAuto[0]=1&boxAuto[1]=3&balconeOterrazzo[0]=terrazzo&balconeOterrazzo[1]=balcone&giardino[0]=10&giardino[1]=40&giardino[2]=20&giardino[3]=40&criterio=rilevanza&noAste=1&__lang=en&pag={page}&paramsCount=17&path=%2Fen%2Fsearch-list%2F"
        response = requests.get(url)
        input_json = response.json()
        pages = int(input_json["maxPages"])
        count = int(input_json["count"])
        web_result = propertyparser(input_json, name)

        with Session(db_engine) as session:
            # exist_id = get_list_id(session)
            for item in web_result:
                item_id = str(item.id)
                if item_id not in first_observed:
                    first_observed[item_id] = str(date.today())
                    # if item.id not in exist_id:
                    if item.latitude != None and item.longitude != None:
                        calc_dist_cost(item)
                        calc_dist_water_main(item)
                        if google_api:
                            count_bars(item, google_places)
                            count_shop(item, google_places)
                            count_bakery(item, google_places)
                            count_food(item, google_places)
                    item.observed = str(date.today())
                    session.merge(item)
                id_list.append(str(item.id))
            session.commit()
            logger.debug(
                "We have committed : "
                + name
                + " - page: "
                + str(page)
                + " - out of total pages: "
                + str(pages)
            )
            # to_translate = select_db_no_translation(session)
        if page == pages or count == 0 or response.status_code != 200:
            total_count = total_count + count
            break

    new_today = [
        key for key, value in first_observed.items() if value == str(date.today())
    ]
    print(len(new_today))
    logger.debug("Today we have added :" + str(new_today))
    with Session(db_engine) as session:
        update_sold1(session)
        update_sold2(session, first_observed, id_list)
    with open("first_observed.json", "w") as f:
        json.dump(first_observed, f, indent=4)
