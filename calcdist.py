import json
import os
import shapely
from shapely import wkt
from shapely.strtree import STRtree
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points, transform
import pyproj
from pyproj import Transformer

wgs_proj = pyproj.CRS("EPSG:4326")
utm_proj = pyproj.CRS("EPSG:32633")
project = pyproj.Transformer.from_crs(wgs_proj, utm_proj, always_xy=True).transform
script_dir = os.path.dirname(os.path.realpath(__file__))


def create_rivertree() -> STRtree:
    Italy_waterline = os.path.join(script_dir, "Italy_waterLines.geojson")
    lst_lines = []
    with open(Italy_waterline) as f:
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

PolyShoreItaly = os.path.join(script_dir, "PolyShoreItaly.geojson")
your_json_file = json.loads(open(PolyShoreItaly).read())
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
    distance = pt.distance(p2)
    return distance / 1000
