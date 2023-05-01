import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("radius_database.db")
c = conn.cursor()

# Add a new column named 'reviewed' with default value NULL
c.execute("ALTER TABLE Property ADD COLUMN reviewed INTEGER")

# Update all existing records to set the 'reviewed' value to 0
c.execute("UPDATE Property SET reviewed = 0")

# Commit the changes and close the connection
conn.commit()
conn.close()
