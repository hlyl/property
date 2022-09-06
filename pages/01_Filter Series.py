import streamlit as st

df = st.session_state["df"]

overview = df[
    [
        "id",
        "region",
        "price",
        "price_m",
        "shopping_count",
        "pub_count",
        "baker_count",
        "food_count",
        "dist_coast",
        "dist_water",
        "longitude",
        "latitude",
    ]
].sort_values(by="price_m")

overview.replace(to_replace="", value="0")

overview["dist_coast"] = overview["dist_coast"].round(0)
overview["dist_water"] = overview["dist_water"].round(0)
overview["dist_coast"] = overview["dist_coast"].astype(int)
overview["dist_water"] = overview["dist_water"].astype(int)


# max_dist_coast = overview["dist_coast"].max().astype(int)
# max_dist_coast = max_dist_coast.astype(int)
# max_dist_water = overview["dist_water"].max().astype(int)

col1, col2, col3 = st.columns(3)

with col1:
    shops = st.slider("Min. Shops: ", 0, 20, 1)

with col2:
    pubs = st.slider("Min. Pubs: ", 0, 20, 1)

with col3:
    bakers = st.slider("Min. Bakers: ", 0, 20, 1)


col4, col5, col6 = st.columns(3)
with col4:
    food = st.slider("Min. Food: ", 0, 20, 1)

with col5:
    coast = st.slider("Max distance to Coast: ", 0, 100, 50)

with col6:
    water = st.slider("Max distance to River/lake: ", 0, 10, 5)


rslt = overview[
    (overview["shopping_count"] > shops)
    & (overview["pub_count"] > pubs)
    & (overview["baker_count"] > bakers)
    & (overview["food_count"] > food)
    & (overview["dist_coast"] < coast)
    & (overview["dist_water"] < water)
]


def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = str(link)
    link = "https://www.immobiliare.it/en/annunci/" + str(link)
    return f'<a target="_blank" href="{link}">{text}</a>'


# TRAILER is the column with hyperlinks
rslt["id"] = rslt["id"].apply(make_clickable)

st.write(rslt.to_html(escape=False, index=False), unsafe_allow_html=True)


st.header("This is  the map:")
lat_lon = rslt.dropna(subset=["longitude", "latitude"])
st.map(lat_lon)
