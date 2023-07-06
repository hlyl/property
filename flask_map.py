from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import folium
import sqlite3
import dao
from dao import Property
from sqlalchemy import case, text, func
from datetime import datetime, timedelta
from sqlmodel import Field, create_engine, Session, select, update
import sys

app = Flask(__name__)
app.secret_key = 'lynge_property'
db_engine = dao.create_db("radius_database.db")
# Set default values
default_zoom = 8
default_latitude = 44.715
default_longitude = 10.745


@app.route('/')
def index():
#    map_center = session.get('map_center', [default_latitude, default_longitude]) 
#    map_zoom = session.get('map_zoom',default_zoom)
#    print("map_center "+str(map_center))

#    m = folium.Map(location = map_center, zoom_start = map_zoom, width="%100",height="100%")
    m = folium.Map(location = ['44.715','10.745'], zoom_start = '8', width="%100",height="100%")


    with Session(db_engine) as db_session:
        price_category = case(
                [
                    (Property.reviewed == 2, 'Hot'),
                    (Property.observed > text("(date('now','-15 day'))"), 'New'),
                    (Property.price.between(20000, 35000), 'Low'),
                    (Property.price.between(35001, 50000), 'Mid'),
                    (Property.price.between(50001, 75000), 'High'),
                ],
                else_='Unknown'
            )
        def get_icon_color(price_category):
            if price_category == 'Low':
                return 'green'
            elif price_category == 'Mid':
                return 'orange'
            elif price_category == 'High':
                return 'red'
            elif price_category == 'New':
                return 'pink'
            elif price_category == 'Hot':
                return 'black'
            else:
                return 'blue'

        statement = select(
            Property.id,
            Property.price,
            Property.latitude,
            Property.longitude,
            Property.observed,
            Property.reviewed,
            price_category.label('price_category')
        ).where((Property.reviewed != 1) & (Property.sold == 0))
        data = db_session.execute(statement)

        for item in data:
            url = f"https://www.immobiliare.it/en/annunci/{item.id}/?imm_source=homepage"
            mapsgoogle = f"https://www.google.com/maps?q={item.latitude},{item.longitude}"
            btn_remove = f'<a href="/update/{item.id}" class="update-btn">Remove</a>'
            btn_interested = f'<a href="/interested/{item.id}" class="update-btn">Interested</a>'
    
            dkk = item.price * 7.4
            popup_text = f'<a href="{url}" target="_blank">Annonce: {item.id}</a><br>\
            Price: {item.price}<br>\
            <a href="{mapsgoogle}" target="_blank">GoogleMaps<br>\
            {btn_remove}<br>{btn_interested}<br>DKK: {dkk:,}</a>'
            popup = folium.Popup(popup_text, max_width=250)
            icon_color = get_icon_color(item.price_category)
            marker = folium.Marker(location=[float(item.latitude), float(item.longitude)],
                            popup=popup,
                            icon = folium.Icon(color=icon_color, icon="glyphicon-home"))
            marker.add_to(m)

#    m = m._repr_html_()
#    return render_template('index.html', m=m)

    m.save('static/map.html')
    return render_template('index.html')

@app.route('/update/<int:id>', methods=['GET','POST'])
def update_value(id):
    session['map_zoom'] = request.form.get('zoom')
    session['map_center'] = request.form.get('center')
    
    with Session(db_engine) as db_session:  # Create a new session inside the function
        stmt = update(Property).where(Property.id == id).values(reviewed=1)
        db_session.execute(stmt)
        db_session.commit()
        print("item removed", file=sys.stderr)
        print(session['map_zoom'], file=sys.stderr)
        print(session['map_center'], file=sys.stderr)
    return redirect(url_for('index'))

@app.route('/interested/<int:id>', methods=['GET','POST'])
def mark_as_interested(id):
    with Session(db_engine) as db_session:  # Create a new session inside the function
        stmt = update(Property).where(Property.id == id).values(reviewed=2)
        db_session.execute(stmt)
        db_session.commit()
        print("item marked as interested", file=sys.stderr)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
