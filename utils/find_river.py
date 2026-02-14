import json

import pyproj
from shapely.geometry import *
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points, transform
from shapely.strtree import STRtree

wgs_proj = pyproj.CRS("EPSG:4326")
utm_proj = pyproj.CRS("EPSG:32633")
project = pyproj.Transformer.from_crs(wgs_proj, utm_proj, always_xy=True).transform

sweep_res = 10  # sweep resolution (degrees)
focal_pt = Point((10.3499, 44.0197))  # radial sweep centre point
sweep_radius = 10.0  # sweep radius


lst_lines = []
with open("Italy_waterLines.geojson") as f:
    features = json.load(f)["features"]
    flat_features = []
    for feature in features:
        chords = feature["geometry"]["coordinates"]
        line_geom = LineString(chords)
        lst_lines.append(transform(project, line_geom))
tree = STRtree(lst_lines)
utm_focalpoint = transform(project, focal_pt)
# print(tree.nearest_geom(utm_focalpoint))

p1, p2 = nearest_points(utm_focalpoint, tree.nearest_geom(utm_focalpoint))
print(utm_focalpoint)
print(p1)
print(p2)
distance = (p1.distance(p2)) / 1000
print(distance)
