import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

data = pd.read_json("BDD.json", lines=False)
data2 = pd.DataFrame(data)
data2 = data2.rename(columns={"lieuTravail.longitude": "lon","lieuTravail.latitude": "lat"})
data3 = data2[['lon','lat']]

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=46.84,
        longitude=2.35,
        zoom=5,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=data3,
           get_position='[lon, lat]',
           radius=3000,
           elevation_scale=10,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=data3,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=3000,
        ),
    ],
))

