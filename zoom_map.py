from flask import Flask, render_template, request, redirect, url_for, session
import folium
from sqlalchemy import case, text
from sqlmodel import Session, select, update
import dao
from dao import Property

app = Flask(__name__)
app.secret_key = "lynge_property"
db_engine = dao.create_db("radius_database.db")
default_zoom = 8
default_latitude = 44.715
default_longitude = 10.745


def generate_map(map_center, map_zoom):
    m = folium.Map(
        location=map_center, zoom_start=map_zoom, width="%100", height="100%"
    )

    with Session(db_engine) as db_session:
        price_category = case(
            [
                (Property.reviewed == 2, "Hot"),
                (Property.observed > text("(date('now','-15 day'))"), "New"),
                (Property.price.between(20000, 35000), "Low"),
                (Property.price.between(35001, 50000), "Mid"),
                (Property.price.between(50001, 75000), "High"),
            ],
            else_="Unknown",
        )

        def get_icon_color(price_category):
            if price_category == "Low":
                return "green"
            elif price_category == "Mid":
                return "orange"
            elif price_category == "High":
                return "red"
            elif price_category == "New":
                return "pink"
            elif price_category == "Hot":
                return "black"
            else:
                return "blue"

        statement = select(
            Property.id,
            Property.price,
            Property.latitude,
            Property.longitude,
            Property.observed,
            Property.reviewed,
            price_category.label("price_category"),
        ).where((Property.reviewed != 1) & (Property.sold == 0))
        data = db_session.execute(statement)

        for item in data:
            url = (
                f"https://www.immobiliare.it/en/annunci/{item.id}/?imm_source=homepage"
            )
            mapsgoogle = (
                f"https://www.google.com/maps?q={item.latitude},{item.longitude}"
            )
            btn_remove = f'<a href="/update/{item.id}" class="btn">Remove</a>'
            btn_interested = (
                f'<a href="/interested/{item.id}" class="btn">Interested</a>'
            )

            dkk = item.price * 7.4
            popup_text = f'<a href="{url}" target="_blank">Annonce: {item.id}</a><br>\
            Price: {item.price}<br>\
            <a href="{mapsgoogle}" target="_blank">GoogleMaps<br>\
            {btn_remove}<br>{btn_interested}<br>DKK: {dkk:,}</a>'
            popup = folium.Popup(popup_text, max_width=250)
            icon_color = get_icon_color(item.price_category)
            marker = folium.Marker(
                location=[float(item.latitude), float(item.longitude)],
                popup=popup,
                icon=folium.Icon(color=icon_color, icon="glyphicon-home"),
            )
            marker.add_to(m)

    m.get_root().html.add_child(folium.Element("<script>var map = this;</script>"))
    m.save("static/map.html")


@app.route("/")
def index():
    print("Rendering index.html")
    map_center = session.get("map_center", [default_latitude, default_longitude])
    map_zoom = session.get("map_zoom", default_zoom)

    generate_map(map_center, map_zoom)

    return render_template("index.html")


@app.route("/update/<int:id>", methods=["POST"])
def update_value(id):
    print("Received POST request for /update/{}".format(id))
    print("Zoom level: ", request.form.get("zoom"))
    print("Center coordinates: ", request.form.get("center"))
    session["map_zoom"] = request.form.get("zoom")
    session["map_center"] = request.form.get("center")

    with Session(db_engine) as db_session:
        stmt = update(Property).where(Property.id == id).values(reviewed=1)
        db_session.execute(stmt)
        db_session.commit()
    return redirect(url_for("index"))


@app.route("/interested/<int:id>", methods=["POST"])
def mark_as_interested(id):
    print("Received POST request for /interested/{}".format(id))
    print("Zoom level: ", request.form.get("zoom"))
    print("Center coordinates: ", request.form.get("center"))
    session["map_zoom"] = request.form.get("zoom")
    session["map_center"] = request.form.get("center")

    with Session(db_engine) as db_session:
        stmt = update(Property).where(Property.id == id).values(reviewed=2)
        db_session.execute(stmt)
        db_session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
