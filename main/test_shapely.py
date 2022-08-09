import json
import shapely
from shapely.geometry import Polygon, LinearRing
from shapely.geometry import shape
from shapely.geometry import Point
from shapely.ops import nearest_points, transform
from geopy.distance import great_circle
from math import cos, sin, asin, sqrt, radians
import pyproj
from pyproj import Transformer

wgs_proj = pyproj.CRS("EPSG:4326")
utm_proj = pyproj.CRS("EPSG:32633")
transform = pyproj.Transformer.from_crs(wgs_proj, utm_proj, always_xy=True).transform


def calc_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km


your_json_file = json.loads(open("PolyShoreItaly.geojson").read())

poly = Polygon(your_json_file["features"][0]["geometry"]["coordinates"][0])

point = Point(41.8904258027315, 12.492230907067375)

point = Point(12.492230907067375, 41.8904258027315)

point = Point(807794, 4631914)

# project = pyproj.Transformer.from_proj(
#    pyproj.Proj(init="epsg:4326"),  # source coordinate system
#    pyproj.Proj(init="epsg:32633"),
# )  # destination coordinate system

# transformer = Transformer.from_crs("epsg:4326", "epsg:32633")
# point2 = transformer.transform(point.x, point.y)
# poly2 = transformer.transform(poly)

p1, p2 = nearest_points(poly.boundary, point)
# utm1, utm2 = nearest_points(poly2.boundary, point2)


project = pyproj.Transformer.from_crs(wgs_proj, utm_proj, always_xy=True).transform
p1utm_point = transform(p1.x, p1.y)
print(p2)
p2utm_point = transform(p2.x, p2.y)

print(p1utm_point)
print(p2utm_point)
# Determine the distance
# distance = p1utm_point.distance(p2utm_point)
# Print the distance

# print(great_circle(p1ok, p2ok))
