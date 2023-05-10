import streamlit as st
import pandas as pd
import altair as alt
import os

os.chdir("c:/Users/tb450/Desktop/Work etc/album_sales/github/album_sales/")

@st.cache_data
def load_data(loc, index_col):
    df = pd.read_csv(loc, index_col=index_col)
    return df

df = load_data('album_sales_wide_5.csv', index_col="Artist")
df = df[df['Total'] >= 5000000]
df = df.loc[df['Genre'].isin(['Pop','Rock','Metal','Punk','Indie'])]

# st.write("Here's our first attempt at using data to create a table:")
# # st.write(pd.DataFrame({
# #     'first column': [1, 5, 3, 4],
# #     'second column': [10, 20, 30, 40]
# # }))

# st.write(df.head())
# df_sorted = df.reset_index().sort_values(["% Domestic", "Total"], ascending=[False, False])
# sorted_artists = list(df_sorted['Artist'])
# st.write(df_sorted.head())
# #st.bar_chart(df_sorted, x="Artist", y="% Domestic")

# # chart = alt.Chart(df_sorted).mark_bar().encode(
# #    alt.X('Artist', sort=sorted_artists), #alt.EncodingSortField(field="% Domestic", op="sum", order='descending')),
# #    alt.Y('% Domestic')
# # ).interactive()

# # chart2 = alt.Chart(df_sorted).mark_bar().encode(
# #     alt.X("% Domestic", bin=True),
# #     y='count()',
# # )

# x_var = 'Domestic Scaled'
# y_var = 'Intl Scaled'

# chart = alt.Chart(df_sorted).mark_circle().encode(
#    alt.X(x_var, scale=alt.Scale(type="symlog")),
#    alt.Y(y_var, scale=alt.Scale(type="symlog"))
# ).interactive()

# line = pd.DataFrame({
#     x_var: [0, 100000000],
#     y_var: [0, 100000000],
# })

# line_plot = alt.Chart(line).mark_line(color= 'red').encode(
#     x= x_var,
#     y= y_var,
# )

# chart_layer = alt.layer(chart, line_plot)

# st.altair_chart(chart_layer, theme=None, use_container_width=True)

import plotly.express as px
import geojson

# Map showing the average % of sales that are domestic map

#df = px.data.election()
#geo1 = px.data.election_geojson()
@st.cache_data
def load_geo(loc):
    with open(loc) as f:
        geo = geojson.load(f)
    return geo

geo = load_geo('countries.geojson')

st.write(df.head())
#st.write(geo1)
#st.write(geo)

df_domestic = df.groupby('Country')[['Country', "% Domestic", "% Domestic Scaled"]].mean().reset_index()
df_domestic['Country'] = df_domestic['Country'].replace({'United States': 'United States of America'})

#st.write(df_domestic)

#col1, col2, col3 = st.columns(3)

scaled = st.radio(
    "Display actual domestic percentages or scale by market size?",
    ('Actual', 'Scaled'))

if (scaled == 'Actual'):
    col = "% Domestic"
else:
    col = "% Domestic Scaled"

fig = px.choropleth(df_domestic, geojson=geo, color=col,
                locations="Country", featureidkey="properties.ADMIN",
                projection="cylindrical stereographic")
fig.update_geos(resolution=50)#fitbounds="locations", visible=True)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=False)
