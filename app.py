from flask import Flask, render_template
from sqlalchemy import create_engine
import folium
import os

app = Flask(__name__)

@app.route('/')
def index():
    # create a map
    start_coords = (46.9540700, 142.7305860)  # Arbitrary location
    folium_map = folium.Map(location=start_coords, zoom_start=14)

    # create a database connection
    engine = create_engine('sqlite:///location_data.db')
    connection = engine.connect()

    # query the database to get the location data
    result = connection.execute("SELECT latitude, longitude FROM location_data")

    # add the location data to the map
    for row in result:
        folium.Marker([row['latitude'], row['longitude']]).add_to(folium_map)

    # save the map to the static folder
    folium_map.save('static/new_map.html')

    # render the index page with the map
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)