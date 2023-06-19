import sqlite3

# Random latitude and longitude values in Italy
italy_locations = [
    (41.9028, 12.4964),  # Rome
    (45.4642, 9.1900),   # Milan
    (40.8522, 14.2681),  # Naples
    (43.7696, 11.2558),  # Florence
    (45.4383, 10.9916),  # Verona
    (44.4057, 8.9463),   # Genoa
    (45.0703, 7.6869),   # Turin
    (37.5079, 15.0830),  # Catania
    (38.1157, 13.3615),  # Palermo
    (43.3188, 11.3308),  # Siena
]

# Create a new SQLite database (or connect to it if it already exists)
connection = sqlite3.connect('location_data.db')
cursor = connection.cursor()

# Create a new table named "location_data" with "latitude" and "longitude" columns
cursor.execute('''
    CREATE TABLE IF NOT EXISTS location_data (
        id INTEGER PRIMARY KEY,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL
    );
''')

# Insert the 10 locations in Italy into the "location_data" table
cursor.executemany('''
    INSERT INTO location_data (latitude, longitude)
    VALUES (?, ?);
''', italy_locations)

# Commit the transaction and close the connection
connection.commit()
connection.close()
