# source /home/hlynge/dev/property/venv/bin/activate
# http://20.105.249.39:4444/
import json
import os
import time
from datetime import date

import requests
from dotenv import load_dotenv
from sqlmodel import Session, select, update  #

import dao
from dao import Property

# Import new service abstractions
from property_tracker.services.poi import get_poi_service
from property_tracker.services.translation import get_translation_service
from property_tracker.utils.distance import get_calculator

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
USE_GOOGLE_PLACES = os.getenv("USE_GOOGLE_PLACES", "false").lower() == "true"
USE_GOOGLE_TRANSLATE = os.getenv("USE_GOOGLE_TRANSLATE", "false").lower() == "true"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "database.db")
PRODUCTION = os.getenv("PRODUCTION", "true").lower() == "true"
LOG_FILE = os.getenv("LOG_FILE", "logging.txt")
POI_SEARCH_RADIUS = int(os.getenv("POI_SEARCH_RADIUS", "2000"))
POI_SEARCH_PROVIDER = os.getenv("POI_SEARCH_PROVIDER", "overpass").strip().lower()
ENABLE_POI_LOOKUP = os.getenv("ENABLE_POI_LOOKUP", "false").lower() == "true"
UPDATE_EXISTING_RECORDS = os.getenv("UPDATE_EXISTING_RECORDS", "false").lower() == "true"

USE_GOOGLE_POI_PROVIDER = USE_GOOGLE_PLACES or POI_SEARCH_PROVIDER == "google"

# Validate configuration
if USE_GOOGLE_POI_PROVIDER and not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is required when USE_GOOGLE_PLACES=true")

# Initialize services
poi_service = get_poi_service(USE_GOOGLE_POI_PROVIDER, GOOGLE_API_KEY)
translation_service = get_translation_service(USE_GOOGLE_TRANSLATE)

# Keep backward compatibility with existing code
production = PRODUCTION
google_api = USE_GOOGLE_POI_PROVIDER
# Get the distance calculator instance
distance_calculator = get_calculator()

# HTTP headers to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


def make_request_with_retry(url, max_retries=3, delay=2):
    """Make HTTP request with retries and proper headers."""
    for attempt in range(max_retries):
        try:
            time.sleep(delay)  # Rate limiting - wait between requests
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt == max_retries - 1:
                raise
            print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {delay * (attempt + 1)} seconds...")
            time.sleep(delay * (attempt + 1))
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            raise
    return None


def safe_get(data, *keys, default=None):
    """Safely get nested dictionary values."""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        elif isinstance(data, list) and isinstance(key, int) and len(data) > key:
            data = data[key]
        else:
            return default
    return data


def deserialise_property(item, region) -> Property:
    try:
        # Extract basic property info
        stringid = safe_get(item, "realEstate", "id")
        is_new = safe_get(item, "realEstate", "isNew")
        raw_price = safe_get(item, "realEstate", "price", "value")
        try:
            price = int(round(float(raw_price))) if raw_price is not None else None
        except (TypeError, ValueError):
            price = None

        # Handle price drop
        price_drop_data = safe_get(item, "realEstate", "price", "loweredPrice")
        if price_drop_data is None:
            price_drop = "No"
        else:
            print("WE have a PriceDrop")
            price_drop = safe_get(price_drop_data, "originalPrice", default="No")
            print("The original price was: " + str(price_drop))

        # Get property details - properties is an array, get first element
        prop = safe_get(item, "realEstate", "properties", 0, default={})

        bathrooms = safe_get(prop, "bathrooms")
        caption = safe_get(prop, "caption")
        category = safe_get(prop, "category", "name")
        discription = safe_get(prop, "description", default="")
        discription_dk = ""

        # Handle floor
        floor_data = safe_get(prop, "floor")
        floor = "not assigned" if floor_data is None else safe_get(floor_data, "value", default="not assigned")

        rooms = safe_get(prop, "rooms")
        surface = safe_get(prop, "surface")

        # Calculate price per sqm
        price_m = None
        if price and surface:
            try:
                surface_num = int(surface.split()[0])
                price_m = round(price / surface_num)
            except (ValueError, ZeroDivisionError, IndexError):
                price_m = None

        # Location data
        location = safe_get(prop, "location", default={})
        lon = safe_get(location, "longitude")
        lat = safe_get(location, "latitude")
        marker = safe_get(location, "marker")

        # Photos
        aphoto = []
        photos = safe_get(prop, "multimedia", "photos", default=[])
        for photo in photos:
            url = safe_get(photo, "urls", "small")
            if url:
                url = url.replace("xxs-c.jpg", "xxl.jpg")
                aphoto.append(url)
        photo_list = json.dumps(aphoto)

        item_dict = {
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
        return Property(**item_dict)
    except Exception as e:
        print(f"Error deserializing property: {e}")
        print(f"Item data: {json.dumps(item, indent=2)}")
        raise


def propertyparser(results, region) -> list[Property]:
    aresults = []
    for result_item in results["results"]:
        item = deserialise_property(result_item, region)
        aresults.append(item)
    return aresults


def update_test():
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
        return data is None


def select_db_no_translation(session) -> dict:
    statement = select(Property.id, Property.discription, Property.discription_dk).where(Property.discription_dk == "")
    out = session.execute(statement)
    result_list_of_dict = [{"id": col1, "discription": col2, "discription_dk": col3} for (col1, col2, col3) in out.fetchall()]
    for dic in result_list_of_dict:
        dic["discription"] = str(dic["discription"]).replace("\n", " ")
        dic["discription"] = str(dic["discription"]).replace("  ", " ")
        totranslatestr = dic["discription"]
        # Use new translation service
        dic["discription_dk"] = translation_service.translate(totranslatestr)

    for dic in result_list_of_dict:
        statement = update(Property).values(discription_dk=dic["discription_dk"]).where(Property.id == dic["id"])
        session.execute(statement)
    session.commit()
    return result_list_of_dict


def update_observed(session):
    statement = update(Property).values(observed=str(date.today())).where(Property.observed is None)
    session.execute(statement)
    session.commit()


def update_sold(session, region, id_list):
    statement = update(Property).values(sold=1).where(Property.region == region).where(~Property.id.in_(id_list))
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
    try:
        dist_coast = distance_calculator.calculate_coast_distance(lat_input, long_input)
    except Exception:
        dist_coast = -1
    item.dist_coast = round(dist_coast, 2)
    return item


def calc_dist_water_main(item: Property) -> Property:
    lat_input = float(item.latitude)
    long_input = float(item.longitude)
    try:
        dist_water = distance_calculator.calculate_water_distance(lat_input, long_input)
    except Exception:
        dist_water = -1
    item.dist_water = round(dist_water, 2)
    return item


def enrich_with_pois(item: Property) -> Property:
    """Enrich property with POI counts using the configured service.

    Args:
        item: Property to enrich with POI data

    Returns:
        Property with pub_count, shopping_count, baker_count, and food_count populated
    """
    try:
        counts = poi_service.get_all_counts(lat=float(item.latitude), lon=float(item.longitude), radius=POI_SEARCH_RADIUS)
        item.pub_count = counts.bars
        item.shopping_count = counts.shops
        item.baker_count = counts.bakeries
        item.food_count = counts.restaurants
        print(f"POI counts: bars={counts.bars}, shops={counts.shops}, bakeries={counts.bakeries}, restaurants={counts.restaurants}")
    except Exception as e:
        print(f"Failed to get POI counts: {e}")
        item.pub_count = 0
        item.shopping_count = 0
        item.baker_count = 0
        item.food_count = 0
    return item


def update_existing_property(existing_item: Property, incoming_item: Property) -> Property:
    """Update refreshable listing fields on an existing property record.

    Keeps user-managed fields (review status, notes, interaction flags) untouched.
    """
    existing_item.region = incoming_item.region
    existing_item.is_new = incoming_item.is_new
    existing_item.price = incoming_item.price
    existing_item.price_drop = incoming_item.price_drop
    existing_item.bathrooms = incoming_item.bathrooms
    existing_item.caption = incoming_item.caption
    existing_item.category = incoming_item.category
    existing_item.discription = incoming_item.discription
    existing_item.floor = incoming_item.floor
    existing_item.rooms = incoming_item.rooms
    existing_item.surface = incoming_item.surface
    existing_item.price_m = incoming_item.price_m
    existing_item.longitude = incoming_item.longitude
    existing_item.latitude = incoming_item.latitude
    existing_item.marker = incoming_item.marker
    existing_item.photo_list = incoming_item.photo_list
    return existing_item


def get_list_id(session) -> list:
    statement = select(Property.id)
    data = session.execute(statement)
    resultlst = [i[0] for i in data]
    return resultlst


if __name__ == "__main__":  #
    from loguru import logger

    logger.add(LOG_FILE)
    logger.debug("That's it, beautiful and simple logging!")
    logger.info(f"Using Google Places: {USE_GOOGLE_POI_PROVIDER}")
    logger.info(f"Using Google Translate: {USE_GOOGLE_TRANSLATE}")
    logger.info(f"POI lookup enabled: {ENABLE_POI_LOOKUP}")
    logger.info(f"Update existing records: {UPDATE_EXISTING_RECORDS}")
    logger.info(f"POI provider: {'google' if USE_GOOGLE_POI_PROVIDER else 'overpass'}")
    logger.info(f"POI radius (m): {POI_SEARCH_RADIUS}")

    if production:
        db_engine = dao.create_db(DATABASE_PATH)
        # Radius-based search: (name, centro, raggio, min_lat, max_lat, min_lng, max_lng)
        data = [
            # Center near Parma, 400km radius covers most of Northern Italy
            ("NORTHERN_ITALY", "44.8,10.3", 400000, 43.5, 47.1, 6.6, 14.0),
        ]
        with open("first_observed.json") as f:
            first_observed = json.load(f)
            print(len(first_observed))
    else:
        db_engine = dao.create_db(os.getenv("TEST_DATABASE_PATH", "test.db"))
        data = [
            # Center near Parma, 400km radius covers most of Northern Italy
            ("NORTHERN_ITALY", "44.8,10.3", 400000, 43.5, 47.1, 6.6, 14.0),
        ]  # Load or initialize first_observed for test mode
        try:
            with open("first_observed.json") as f:
                first_observed = json.load(f)
                print(len(first_observed))
        except FileNotFoundError:
            first_observed = {}
            print("first_observed.json not found, starting with empty dictionary")

    total_count = 0
    id_list = []
    for name, centro, raggio, min_lat, max_lat, min_lng, max_lng in data:
        print(name)
        page = 0

        while True:
            page = page + 1
            url = f"https://www.immobiliare.it/api-next/search-list/listings/?raggio={raggio}&centro={centro}&idContratto=1&idCategoria=1&prezzoMassimo=100000&idTipologia[0]=7&idTipologia[1]=11&idTipologia[2]=12&idTipologia[3]=13&localiMinimo=4&bagni=2&stato=2&tipoProprieta=1&balconeOterrazzo[0]=terrazzo&giardino[0]=10&__lang=en&minLat={min_lat}&maxLat={max_lat}&minLng={min_lng}&maxLng={max_lng}&pag={page}&paramsCount=18&path=%2Fen%2Fsearch-list%2F"
            response = make_request_with_retry(url)
            input_json = response.json()

            # Save sample response for debugging (first page only)
            if page == 1 and name == "NORTHERN_ITALY":
                with open("api_response_sample.json", "w") as f:
                    json.dump(input_json, f, indent=2)
                print("Saved sample API response to api_response_sample.json")
            pages = input_json["maxPages"]
            count = input_json["count"]
            web_result = propertyparser(input_json, name)
            page_new_items = 0
            page_updated_existing_items = 0
            page_poi_queries = 0
            page_poi_bars = 0
            page_poi_shops = 0
            page_poi_bakeries = 0
            page_poi_restaurants = 0

            with Session(db_engine) as session:
                # exist_id = get_list_id(session)
                for item in web_result:
                    item_id = str(item.id)
                    existing_item = session.get(Property, item.id)
                    is_new_item = existing_item is None

                    if is_new_item:
                        page_new_items += 1
                        first_observed[item_id] = str(date.today())
                        working_item = item
                    else:
                        if item_id not in first_observed:
                            first_observed[item_id] = existing_item.observed or str(date.today())

                        if not UPDATE_EXISTING_RECORDS:
                            id_list.append(str(item.id))
                            continue

                        page_updated_existing_items += 1
                        working_item = update_existing_property(existing_item, item)

                    if working_item.latitude is not None and working_item.longitude is not None:
                        calc_dist_cost(working_item)
                        calc_dist_water_main(working_item)
                        if ENABLE_POI_LOOKUP:
                            enrich_with_pois(working_item)
                            page_poi_queries += 1
                            page_poi_bars += working_item.pub_count or 0
                            page_poi_shops += working_item.shopping_count or 0
                            page_poi_bakeries += working_item.baker_count or 0
                            page_poi_restaurants += working_item.food_count or 0

                    if is_new_item:
                        working_item.observed = str(date.today())
                        session.merge(working_item)
                    id_list.append(str(item.id))
                session.commit()
                if ENABLE_POI_LOOKUP:
                    poi_note = ""
                    if page_poi_queries == 0:
                        poi_note = " (no properties with coordinates were enriched on this page)"
                    logger.info(
                        f"{name} page {page}/{pages} committed: scraped={len(web_result)}, new={page_new_items}, updated_existing={page_updated_existing_items}, "
                        f"poi_queries={page_poi_queries}, POIs found bars={page_poi_bars}, shops={page_poi_shops}, "
                        f"bakeries={page_poi_bakeries}, restaurants={page_poi_restaurants}{poi_note}"
                    )
                else:
                    logger.info(
                        f"{name} page {page}/{pages} committed: scraped={len(web_result)}, new={page_new_items}, "
                        f"updated_existing={page_updated_existing_items}"
                    )
                to_translate = select_db_no_translation(session)
            if page == pages or count == 0 or response.status_code != 200:
                total_count = total_count + count
                break

    new_today = [key for key, value in first_observed.items() if value == str(date.today())]
    print(len(new_today))
    logger.debug("Today we have added :" + str(new_today))
    with Session(db_engine) as session:
        update_sold1(session)
        update_sold2(session, first_observed, id_list)
    with open("first_observed.json", "w") as f:
        json.dump(first_observed, f, indent=4)
