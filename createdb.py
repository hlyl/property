import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE locations (id INTEGER PRIMARY KEY, lat REAL, lng REAL, value INTEGER, status INTEGER)''')
conn.commit()
conn.close()
