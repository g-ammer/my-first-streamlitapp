import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import geojson
from urllib.request import urlopen
import json
from copy import deepcopy


# Load data into cache

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

@st.cache_data
def load_geodata(path):
    with open(path) as f:
        gj = geojson.load(f)
    return gj


# Load data
df_volc_raw = load_data(path="./data/volcano_ds_pop.csv")
df_volc = deepcopy(df_volc_raw)
gj_volc = load_geodata("./data/countries.geojson")

df_volc["Type"] = df_volc["Type"].replace({'Stratovolcanoes':'Stratovolcano',
                                           "Submarine volcanoes":"Submarine volcano",
                                           "Shield volcanoes":"Shield volcano",
                                           "Pyroclastic cones":"Pyroclastic cone",
                                           "Maars":"Maar",
                                           "Lava domes":"Lava dome",
                                           "Cinder cones":"Cinder cone"})

df_volc["Country"] = df_volc["Country"].replace({'United States':'United States of America',
                                                                      'Tanzania':'United Republic of Tanzania',
                                                                      'Martinique':'Martinique',
                                                                      'Sao Tome & Principe':'Sao Tome and Principe',
                                                                      'Guadeloupe':'Guadeloupe',
                                                                      'Wallis & Futuna':'Wallis and Futuna'})



# Add title and header
st.title("Volcanoes of the World")
st.subheader("Explore the locations of volcano types across this planet")

# Add widget to show dataframe
if st.checkbox("Show raw data"):
    st.subheader("Volcano dataset:")
    st.dataframe(data=df_volc)

# Setting up columns
left_column, middle_column, right_column = st.columns([2, 2, 1])

# Widget: radio button for chart type
chart_type = right_column.radio(
    label='Select chart type', options=['Globe map', 'Mercator'])

# Widget: selectbox for selecting volcano type
types = ["All"] + sorted(df_volc.Type.unique())
type = left_column.selectbox("Select volcano type", types)

if type == "All":
    df_volc_red = df_volc
else:
    df_volc_red = df_volc[df_volc["Type"] == type]

# Widget: selectbox for selecting country
countries = ["All"] + sorted(df_volc.Country.unique())
country = middle_column.selectbox("Select country", countries)

if country == "All":
    df_volc_red = df_volc_red
else:
    df_volc_red = df_volc_red[df_volc_red["Country"] == country]


# Group volcanoes based on country and rename
df_volc_group = df_volc_red.groupby("Country")["Volcano Name"].count().reset_index().rename(
    columns= {'Volcano Name':'Nr. of Volcanoes'})


### PLOT CHARTS OF VOLCANOES ###

# Plot Mapbox of volcanoes
fig_mp = go.Figure(
            go.Choroplethmapbox(
                geojson = gj_volc,
                locations=df_volc_group['Country'], 
                z=df_volc_group['Nr. of Volcanoes'], 
                featureidkey="properties.ADMIN",
                colorscale="Bluered",
                colorbar={"title": 'No. volc.'},
                text=df_volc_group['Country'],
                zmin=0, zmax=df_volc_group["Nr. of Volcanoes"].max(),
                marker_opacity=0.35,
                hovertemplate=
                    "Country: %{text}<br>" +
                    "Nr. volc.: %{z}<br>" +
                    "<extra></extra>"

))

fig_mp.add_trace(
            go.Scattermapbox(
                lon = df_volc_red['Longitude'],
                lat = df_volc_red['Latitude'],
                mode = 'markers',
                marker_color = "black",
                marker_opacity=0.7,
                text = df_volc_red["Volcano Name"],
                hovertemplate=
                    "Volcano: %{text}<br>" +
                    "lat: %{lat}<br>" +
                    "lon: %{lon}<br>" +
                    "<extra></extra>"
                )
)

fig_mp.update_layout(
                #mapbox_zoom=0.75,
                width=1000, height=650,
                #title={"text": "Type of volcano: " + type,
                #"x":0.5,
                #"xanchor": 'center',
                #"y":0.97,
                #"font_size":22
                #},
                margin={"r":0,"t":0,"l":0,"b":0}
            )

fig_mp.update_geos(fitbounds="locations")

fig_mp.update_layout(
                mapbox_style="white-bg",
                mapbox_layers=[
                {
                "opacity": 0.7,
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "United States Geological Survey",
                "source": [
                    "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
            }
      ])




#Plot globe map

fig_geo = go.Figure(go.Choropleth(
                geojson = gj_volc,
                locations=df_volc_group['Country'], 
                z=df_volc_group['Nr. of Volcanoes'], 
                featureidkey="properties.ADMIN",
                colorscale="Bluered",
                colorbar={"title": 'No. volc.'},
                text=df_volc_group['Country'],
                zmin=0, zmax=df_volc_group["Nr. of Volcanoes"].max(),
                marker_opacity=0.35,
                hovertemplate=
                    "Country: %{text}<br>" +
                    "Nr. volc.: %{z}<br>" +
                    "<extra></extra>"

))

fig_geo.add_trace(
            go.Scattergeo(
                    lon = df_volc_red['Longitude'],
                    lat = df_volc_red['Latitude'],
                    mode = 'markers',
                    marker_color = "black",
                    text = df_volc_red["Volcano Name"],
                    hovertemplate=
                        "Volcano: %{text}<br>" +
                        "lat: %{lat}<br>" +
                        "lon: %{lon}<br>" +
                        "<extra></extra>"
                )
)

fig_geo.update_layout(
            #mapbox_style="open-street-map",
            #mapbox_zoom=0.75,
            width=1000, height=650,
            #title={"text": "Type of volcano: " + type,
            #    "x":0.35,
            #    "xanchor": 'center',
            #    "y":0.97,
            #    "font_size":22
            #},
            margin={"r":0,"t":0,"l":0,"b":0}
            )

fig_geo.update_geos(projection_type="orthographic", fitbounds="locations")


if chart_type == "Globe map":
    st.plotly_chart(fig_geo)
elif chart_type == "Mercator":
    st.plotly_chart(fig_mp)


df_volc_top = df_volc_red
df_volc_type = df_volc_red

# Make new df's with top 30 countries w. most volcanoes and volcano types
if country == "All" and type == "All":
    df_volc_top = df_volc_red.groupby("Country")["Volcano Name"].count().sort_values(ascending=False).head(30)
    df_volc_type = df_volc_red.groupby("Type")["Volcano Name"].count().sort_values(ascending=False)
elif country == "All" and not type == "All":
    df_volc_top = df_volc_red.groupby("Country")["Volcano Name"].count().sort_values(ascending=False).head(30)
    df_volc_type = df_volc_red.groupby("Type").count()
elif type == "All" and not country == "All":
    df_volc_top = df_volc_red.groupby("Country").count()
    df_volc_type = df_volc_red.groupby("Type")["Volcano Name"].count().sort_values(ascending=False)

# Make figure with top countries
fig_top_countries = go.Figure()
fig_top_countries.add_bar(
            x=list(df_volc_top.index),
            y=df_volc_top
            )

fig_top_countries.update_layout(width=1000, height=500,
    title_text = "Top countries",
    yaxis_title_text = "#volcanoes",
)


# Plot figure with volcano types
fig_type = go.Figure()
fig_type.add_bar(
            x=list(df_volc_type.index),
            y=df_volc_type,
            marker_color = "LightSeaGreen"
            )

fig_type.update_layout(width=1000, height=500,
    title_text = "Volcano types across the world",
    yaxis_title_text = "log (#volcanoes)",
)

if country == "All" and type == "All":
    st.plotly_chart(fig_top_countries)
    st.plotly_chart(fig_type)
elif country == "All" and not type == "All":
    st.plotly_chart(fig_top_countries)
elif type == "All" and not country == "All":
    st.plotly_chart(fig_type)

