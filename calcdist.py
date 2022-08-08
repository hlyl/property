import json
import shapely
from shapely import wkt
from shapely.geometry import Point
from shapely.ops import nearest_points, transform
import pyproj
from pyproj import Transformer

wgs_proj = pyproj.CRS("EPSG:4326")
utm_proj = pyproj.CRS("EPSG:32633")
project = pyproj.Transformer.from_crs(wgs_proj, utm_proj, always_xy=True).transform


def format_p(item):
    return f"{item[0]} {item[1]}"


def format_t(items):
    items = ", ".join(list(map(format_p, items)))
    return f"POLYGON (({items}))"


def format_point(point):
    return f"POINT ({point[1]} {point[0]})"


# poi = [41.89042580273156, 12.492230907067375]

your_json_file = json.loads(open("PolyShoreItaly.geojson").read())
jsonString = your_json_file["features"][0]["geometry"]["coordinates"][0]
shore_italy = shapely.wkt.loads(format_t(jsonString))


def calc_dist_short(poi):
    pt = wkt.loads(format_point(poi))
    p1, p2 = nearest_points(shore_italy.boundary, pt)

    p1utm_point = transform(project, p1)
    p2utm_point = transform(project, p2)
    # Determine the distance
    distance = p1utm_point.distance(p2utm_point)
    # Print the distance
    return distance / 1000
