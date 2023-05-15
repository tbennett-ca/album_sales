import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import os

os.chdir("c:/Users/tb450/Desktop/Work etc/album_sales/github/album_sales/")

st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)

@st.cache_data
def load_data(loc, index_col):
    df = pd.read_csv(loc, index_col=index_col)
    df['% Domestic'] = round(df['% Domestic']*100, 1)
    df['% Domestic Scaled'] = round(df['% Domestic Scaled']*100, 1)
    df['% Intl'] = 100-df['% Domestic']
    df['% Intl Scaled'] = 100-df['% Domestic Scaled']
    return df

df = load_data('album_sales_wide_5.csv', index_col="Artist")
#df = df[df['Total'] >= 1000000]
#df = df.loc[df['Genre'].isin(['Pop','Rock','Metal','Punk','Indie'])]

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

# domestic_intl_ratio = df['Domestic Scaled'].sum() / df['Intl Scaled'].sum()
# chart_max = max(df['Domestic Scaled'].max() / domestic_intl_ratio,  df['Intl Scaled'].max())

# chart = alt.Chart(df_sorted).mark_circle().encode(
#    alt.X(x_var, scale=alt.Scale(domainMax=chart_max*domestic_intl_ratio, type="symlog")),
#    alt.Y(y_var, scale=alt.Scale(domainMax=chart_max, type="symlog")),
#    tooltip=[x_var, y_var, 'Artist']
# ).properties(
#     width=1000,
#     height=1000
# ).interactive()

# line = pd.DataFrame({
#     x_var: [0, chart_max*domestic_intl_ratio],
#     y_var: [0, chart_max],
# })

# line_plot = alt.Chart(line).mark_line(color= 'red').encode(
#     x= x_var,
#     y= y_var,
# )

# chart_layer = alt.layer(chart, line_plot)

# st.altair_chart(chart_layer, theme=None, use_container_width=False)

#import plotly.express as px
#import geojson

# Map showing the average % of sales that are domestic map

#df = px.data.election()
#geo1 = px.data.election_geojson()
# @st.cache_data
# def load_geo(loc):
#     with open(loc) as f:
#         geo = geojson.load(f)
#     return geo

# geo = load_geo('countries.geojson')

st.write(df.head())
#st.write(geo1)
#st.write(geo)

#df_domestic = df.groupby('Country')[['Country', "% Domestic", "% Domestic Scaled", "Total"]].mean().reset_index()
df_country = df.groupby('Country')
df_domestic = df_country[['Country', "Domestic", "Domestic Scaled", "Intl", "Intl Scaled", "Total", "Total Scaled"]].sum()#.reset_index()
df_domestic['% Domestic'] = round(df_domestic['Domestic'] / df_domestic['Total'] * 100, 1)
df_domestic['% Domestic Scaled'] = round(df_domestic['Domestic Scaled'] / df_domestic['Total Scaled'] * 100, 1)
df_domestic['% Intl'] = round(df_domestic['Intl'] / df_domestic['Total'] * 100, 1)
df_domestic['% Intl Scaled'] = round(df_domestic['Intl Scaled'] / df_domestic['Total Scaled'] * 100, 1)
df_domestic['Artist Count'] = df_country['Country'].count()
df_domestic = df_domestic[df_domestic['Artist Count'] >= 5]
#df_domestic['Country'] = df_domestic['Country'].replace({'United States': 'United States of America'})
#df_domestic = df_domestic.set_index('Country')

df_sorted_desc = df.reset_index().sort_values(["% Domestic", "Total"], ascending=[False, False])[:25]
sorted_artists_desc = list(df_sorted_desc['Artist'])
#st.write(df_sorted.head())
#st.bar_chart(df_sorted, x="Artist", y="% Domestic")

chart_artists_desc = alt.Chart(df_sorted_desc).mark_bar().encode(
   alt.Y('Artist', sort=sorted_artists_desc), #alt.EncodingSortField(field="% Domestic", op="sum", order='descending')),
   alt.X('% Domestic')
).interactive()

df_sorted_asc = df.reset_index().sort_values(["% Domestic", "Total"], ascending=[True, False])[:25]
sorted_artists_asc = list(df_sorted_asc['Artist'])

chart_artists_asc = alt.Chart(df_sorted_asc).mark_bar().encode(
   alt.Y('Artist', sort=sorted_artists_asc), #alt.EncodingSortField(field="% Domestic", op="sum", order='descending')),
   alt.X('% Domestic')
).interactive()

# chart2 = alt.Chart(df_sorted).mark_bar().encode(
#     alt.X("% Domestic", bin=True),
#     y='count()',
# )

#st.write(df_domestic)
scaled = st.radio(
        "Display actual domestic sales/percentages or scale by market size?",
        ('Actual', 'Scaled'), horizontal=True)
#col1, col2, col3 = st.columns(3)
col_1_1, col_1_2 = st.columns(2)#, col_1_3 = st.columns(3)

if (scaled == 'Actual'):
    col_appendix = ""
else:
    col_appendix = " Scaled"

with col_1_1:
    st.bar_chart(df_domestic[["Domestic" + col_appendix, "Intl" + col_appendix]])

#with col_1_2:
    st.bar_chart(df_domestic[["% Domestic" + col_appendix, "% Intl" + col_appendix]])

with col_1_2:
    table_height = (len(df_domestic)+1)*35 + 3
    st.dataframe(df_domestic[["Domestic" + col_appendix, "Intl" + col_appendix, "Total" + col_appendix, "% Domestic" + col_appendix, "% Intl" + col_appendix, "Artist Count"]],
                 height=table_height)

col_2_1, col_2_2 = st.columns(2)

with col_2_1:
    #st.bar_chart(df[["Domestic" + col_appendix, "Intl" + col_appendix]])
    st.altair_chart(chart_artists_desc, theme=None, use_container_width=True)

with col_2_2:
    st.altair_chart(chart_artists_asc, theme=None, use_container_width=True)

# with col1_1:

#     if (scaled == 'Actual'):
#         col = "% Domestic"
#     else:
#         col = "% Domestic Scaled"

#     fig = px.choropleth(df_domestic, geojson=geo, color=col,
#                         title="Automatic Labels Based on Data Frame Column Names",
#                         locations="Country", featureidkey="properties.ADMIN",
#                         projection="cylindrical stereographic")
#     fig.update_geos(resolution=50)#fitbounds="locations", visible=True)
#     fig.update_layout(height=500)
#     #fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#     st.plotly_chart(fig, use_container_width=True)

# with col1_2:

#     fig2 = px.choropleth(df_domestic, geojson=geo, color='Total',
#                          title="Automatic Labels Based on Data Frame Column Names",
#                          locations="Country", featureidkey="properties.ADMIN",
#                          projection="cylindrical stereographic")
#     fig2.update_geos(resolution=50)#fitbounds="locations", visible=True)
#     fig2.update_layout(height=500)
#     #fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#     st.plotly_chart(fig2, use_container_width=True)

#col2_1, col2_2 = st.columns(2)

#with col2_1:
#st.write(df_domestic[["Domestic" + col_appendix, "Intl" + col_appendix, "Total" + col_appendix, "% Domestic" + col_appendix, "% Intl" + col_appendix, "Artist Count"]])#.sort_values(''))

# with col2_2:
#     st.write(df_domestic[["% Domestic" + col_appendix, "% Intl" + col_appendix]])