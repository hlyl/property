import json
import shapely
from shapely import wkt
from shapely.strtree import STRtree
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points, transform
import pyproj
from pyproj import Transformer
from main import tree

wgs_proj = pyproj.CRS("EPSG:4326")
utm_proj = pyproj.CRS("EPSG:32633")
project = pyproj.Transformer.from_crs(wgs_proj, utm_proj, always_xy=True).transform


def create_rivertree() -> STRtree:
    lst_lines = []
    with open("Italy_waterLines.geojson") as f:
        features = json.load(f)["features"]
        flat_features = []
        for feature in features:
            chords = feature["geometry"]["coordinates"]
            line_geom = LineString(chords)
            lst_lines.append(transform(project, line_geom))
    tree = STRtree(lst_lines)
    return tree


def format_p(item):
    return f"{item[0]} {item[1]}"


def format_t(items):
    items = ", ".join(list(map(format_p, items)))
    return f"POLYGON (({items}))"


def format_point(point):
    return f"POINT ({point[1]} {point[0]})"


your_json_file = json.loads(open("PolyShoreItaly.geojson").read())
jsonString = your_json_file["features"][0]["geometry"]["coordinates"][0]
shore_italy = shapely.wkt.loads(format_t(jsonString))


def calc_dist_short(poi):
    pt = wkt.loads(format_point(poi))
    p1, p2 = nearest_points(shore_italy.boundary, pt)
    p1utm_point = transform(project, p1)
    p2utm_point = transform(project, p2)
    distance = p1utm_point.distance(p2utm_point)
    return distance / 1000


def calc_dist_water(tree, poi):
    pt = wkt.loads(format_point(poi))
    pt = transform(project, pt)
    p1, p2 = nearest_points(pt, tree.nearest_geom(pt))
    p2utm_point = transform(project, p2)
    # Determine the distance
    distance = p1.distance(p2utm_point)
    # Print the distance
    return distance / 1000
