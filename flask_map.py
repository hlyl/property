from flask import Flask, render_template, jsonify, request, redirect, url_for
import folium
import sqlite3
import dao
from dao import Property
from sqlmodel import Field, create_engine, Session, select, update
import sys

print('This is error output', file=sys.stderr)
print('This is standard output', file=sys.stdout)

app = Flask(__name__)
db_engine = dao.create_db("radius_database.db")


@app.route('/')
def index():
    m = folium.Map(location=[44.715, 10.745], zoom_start=10)
    #44.71528006921618, 10.74521045661985

    with Session(db_engine) as session:
        #statement = select(Property.id,Property.price, Property.latitude, Property.longitude)
        statement = select(Property.id, Property.price, Property.latitude, Property.longitude).where(Property.reviewed == 0)
        data = session.execute(statement)

        for item in data:
            url = f"https://www.immobiliare.it/en/annunci/{item.id}/?imm_source=homepage"
            mapsgoogle = f"https://www.google.com/maps?q={item.latitude},{item.longitude}"
            btn = f'<a href="/update/{item.id}" class="update-btn">Update status</a>'
            popup_text = f'<a href="{url}" target="_blank">Annonce: {item.id}</a><br>\
            Price: {item.price}<br>\
            <a href="{mapsgoogle}" target="_blank">GoogleMaps<br>\
            {btn}</a>'
            popup = folium.Popup(popup_text, max_width=250)
            marker = folium.Marker(location=[float(item.latitude), float(item.longitude)],
                            popup=popup,
                            icon = folium.Icon(color='blue', icon_size=(20,20)))
            marker.add_to(m)
    print('This is error output', file=sys.stderr)
    print('This is standard output', file=sys.stdout)

    m = m._repr_html_()
    return render_template('index.html', m=m)

@app.route('/update/<int:id>', methods=['GET','POST'])
def update_value(id):
    with Session(db_engine) as session:  # Create a new session inside the function
        stmt = update(Property).where(Property.id == id).values(reviewed=1)
        session.execute(stmt)
        session.commit()
        return redirect(url_for('index'))  # Redirect to the root route after updating the value
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
