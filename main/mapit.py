import json
import folium
from folium.features import DivIcon
import geojson
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


# Set your point of interest. In our case that is Colosseum.
poi_name = "Colosseum"
poi = [41.89042580273156, 12.492230907067375]
pt = wkt.loads("POINT(12.492230907067375 41.8904258027315)")

your_json_file = json.loads(open("PolyShoreItaly.geojson").read())
jsonString = your_json_file["features"][0]["geometry"]["coordinates"][0]
shape = shapely.wkt.loads(format_t(jsonString))

p1, p2 = nearest_points(shape.boundary, pt)


# Map it!
m = folium.Map(location=poi, zoom_start=12)
geo_j = folium.GeoJson(your_json_file, style_function=lambda x: {"fillColor": "orange"})
geo_j.add_to(m)

# Display POI
folium.CircleMarker(location=poi, color="blue", radius=5, fill="blue").add_to(m)

folium.CircleMarker(location=[p1.y, p1.x], color="red", radius=10, fill="red").add_to(m)


# Display POI Name
folium.map.Marker(
    location=poi,
    icon=DivIcon(
        icon_size=(150, 36),
        icon_anchor=(0, 0),
        html='<div style="font-size: 18pt; color: red">{}</div>'.format(poi_name),
    ),
).add_to(m)

p1utm_point = transform(project, p1)
print(p1utm_point)
p2utm_point = transform(project, p2)
print(p2utm_point)

# Determine the distance
distance = p1utm_point.distance(p2utm_point)
print("This is distance between P1 and P2")
# Print the distance
print(distance / 1000)
# m.save("map_1.html")

m.save("map_2.html")
