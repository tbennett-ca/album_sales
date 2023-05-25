import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import os
#import plotly.graph_objects as go
#from plotly.subplots import make_subplots
import plotly.express as px

st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)

@st.cache_data
def load_data(loc, index_col):
    df = pd.read_csv(loc, index_col=index_col)
    for c in ['Domestic', 'Intl', 'Domestic Scaled', 'Intl Scaled', 'Total']:
        df[c] = round(df[c], 0)

    df['% Domestic'] = round(df['% Domestic']*100, 1)
    df['% Domestic Scaled'] = round(df['% Domestic Scaled']*100, 1)
    df['% Intl'] = 100-df['% Domestic']
    df['% Intl Scaled'] = 100-df['% Domestic Scaled']
    return df

def load_sidebar():
    with st.sidebar:
        _ = st.radio(
                "Display actual domestic sales/percentages or scale by market size?",
                ('Actual', 'Scaled'), horizontal=True, key='scaled'),
        st.multiselect('Select genres (all if blank)', options=genres, default=['Rock','Metal'], key='genre_filter')
        st.multiselect('Select artist country (all if blank)', options=countries, default=None, key='country_filter')
        sales_col_1, sales_col_2 = st.columns(2)
        with sales_col_1:
            if "min_sales" in st.session_state:
                st.number_input('Enter min sales (millions)', min_value=0, max_value = 100, on_change=adjust_sales_filter, key='min_sales')
            else:
                st.number_input('Enter min sales (millions)', min_value=0, max_value = 100, value=0, on_change=adjust_sales_filter, key='min_sales')
        with sales_col_2:
            if "max_sales" in st.session_state:
                st.number_input('Enter max sales (millions)', min_value=1, max_value = 500, on_change=adjust_sales_filter, key='max_sales')
            else:
                st.number_input('Enter max sales (millions)', min_value=1, max_value = 500, value=500, on_change=adjust_sales_filter, key='max_sales')

def adjust_sales_filter():
    st.session_state.max_sales = max(st.session_state.max_sales, st.session_state.min_sales+1)

def country_charts():
    st.write("### Album sales by origin country")
    
    col_1_1, col_1_2 = st.columns(2)

    if (st.session_state.scaled == 'Actual'):
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
                    height=table_height, use_container_width=True)
        
    df_country_top = pd.DataFrame(df_filtered.groupby('Country')['Total' + col_appendix].nlargest(5))
    df_country_top['Rank'] = df_country_top.groupby('Country').rank(ascending=False, method='first')
    df_country_top_wide = df_country_top.drop('Total' + col_appendix, axis=1).reset_index().pivot_table(index='Country', columns='Rank', values='Artist', aggfunc=lambda x: ' '.join(x), fill_value='')
    df_country_top_wide.columns = ['Artist #1', 'Artist #2', 'Artist #3', 'Artist #4', 'Artist #5']
    table_height = (len(df_country_top_wide)+1)*35 + 3
    st.dataframe(df_country_top_wide, height=table_height, use_container_width=True)
        
def artist_charts():
    st.write("### Album sales by artist")
    if (st.session_state.scaled == 'Actual'):
        col_appendix = ""
        sales_cols = 'Sales' 
    else:
        col_appendix = " Scaled"
        sales_cols = 'Scaled' 

    ### Histogram & Scatterplot

    histogram = alt.Chart(df_filtered).mark_bar(
        opacity=1,
        binSpacing=0
    ).encode(
        alt.X('% Domestic' + col_appendix + ':Q', bin=alt.Bin(maxbins=5)),
        alt.Y('count()')
    )

    scatter = px.scatter(df_filtered.reset_index(), 
                     x="Intl" + col_appendix, y="Domestic" + col_appendix, 
                     hover_name="Artist", 
                     log_x=True, log_y=True,
                     range_x=[5e3, 5e8], range_y=[5e3, 5e8])
    scatter.update_layout(shapes = [{'type': 'line', 'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 1, 'x0': 0, 'x1': 1}])

    col_1_1, col_1_2 = st.columns([1,2])

    with col_1_1:
        st.altair_chart(histogram, use_container_width=False)

    with col_1_2:
        st.plotly_chart(scatter)

    ### Artist comparison

    display_cols = ['Country', 'Genre', 'Total' + col_appendix, 'Domestic' + col_appendix, 'Intl' + col_appendix, "% Domestic" + col_appendix, "% Intl" + col_appendix]

    col_2_1, col_2_2 = st.columns(2)

    with col_2_1:
        st.selectbox('Artist #1', sorted(df_filtered.index), key='artist1')
        st.dataframe(df_filtered[display_cols].filter(items=[st.session_state.artist1], axis=0), use_container_width=True)

    with col_2_2:
        st.selectbox('Artist #2', sorted(df_filtered.index), key='artist2')
        st.dataframe(df_filtered[display_cols].filter(items=[st.session_state.artist2], axis=0), use_container_width=True)

    col_3_1, col_3_2 = st.columns(2)

    with col_3_1:
        df_artist_comp = df_filtered.filter(items=[st.session_state.artist1, st.session_state.artist2], axis=0)
        df_artist_long = pd.melt(df_artist_comp, var_name='Country', value_name='Sales' + col_appendix, ignore_index=False)
        df_artist_long = pd.melt(df_artist_comp, value_vars=['Domestic' + col_appendix, 'Intl' + col_appendix], var_name='‎', value_name='Sales' + col_appendix, ignore_index=False)

        artist_comp_chart = alt.Chart(df_artist_long.reset_index()).mark_bar().encode(
            alt.X('Artist'),
            alt.Y('Sales' + col_appendix),
            color='‎'
        ).interactive()
        
        st.altair_chart(artist_comp_chart, use_container_width=True)
    
    with col_3_2:
        df_artist_comp = df_filtered.filter(items=[st.session_state.artist1, st.session_state.artist2], axis=0)
        df_artist_comp = df_artist_comp.filter(regex=sales_cols + '\|', axis=1)
        df_artist_comp.columns = df_artist_comp.columns.str.replace(sales_cols + '\|', '', regex=True)
        df_artist_long = pd.melt(df_artist_comp, var_name='Country', value_name='Sales' + col_appendix, ignore_index=False)
        df_artist_long = df_artist_long.loc[df_artist_long['Sales' + col_appendix] > 0]
        
        artist_comp_chart_full = alt.Chart(df_artist_long.reset_index()).mark_bar().encode(
            alt.X('Artist'),
            alt.Y('Sales' + col_appendix),
            color='Country'
        ).interactive()

        st.altair_chart(artist_comp_chart_full, use_container_width=True)

    ### Full artist list chart

    df_sorted_desc = df_filtered.reset_index().sort_values(["% Domestic" + col_appendix, "Total" + col_appendix], ascending=[False, False])
    #df_sorted_desc = df_filtered.reset_index().sort_values("Domestic" + col_appendix, ascending=False)#[:25]
    df_sorted_desc['% Domestic OG' + col_appendix] = df_sorted_desc['% Domestic' + col_appendix]
    df_sorted_desc['% Domestic' + col_appendix] = -1*df_sorted_desc['% Domestic' + col_appendix]
    sorted_artists_desc = list(df_sorted_desc['Artist'])

    # chart_artists_desc_1 = alt.Chart(df_sorted_desc).mark_bar(color='#0068C9').encode(
    #    alt.Y('Artist', sort=sorted_artists_desc),
    #    alt.X('% Domestic' + col_appendix, axis=alt.Axis(labelExpr='abs(datum.value)', tickCount=10))#, axis=alt.Axis(formatType='percentFormat')) 
    # )#.interactive()

    # chart_artists_desc_2 = alt.Chart(df_sorted_desc).mark_bar(color='#83C9FF').encode(
    #    alt.Y('Artist', sort=sorted_artists_desc),
    #    alt.X('% Intl' + col_appendix)
    # )

    # st.altair_chart(chart_artists_desc_1 + chart_artists_desc_2, theme=None, use_container_width=True)

    chart_artists_desc = alt.Chart(df_sorted_desc).mark_bar().transform_fold(
        fold=['% Domestic' + col_appendix, '% Intl' + col_appendix], 
        as_=['‎', '% Domestic/Intl']
    ).encode(
        y=alt.Y('Artist', sort=sorted_artists_desc),
        x=alt.X('% Domestic/Intl:Q', axis=alt.Axis(labelExpr='abs(datum.value)', tickCount=10)),
        color='‎:N',
        tooltip=['Artist', 
                 alt.Tooltip('Total' + col_appendix, format=","), 
                 alt.Tooltip('Domestic' + col_appendix, format=","), 
                 alt.Tooltip('Intl' + col_appendix, format=","), 
                 alt.Tooltip('% Domestic OG' + col_appendix, format=".0f", title='% Domestic'), 
                 alt.Tooltip('% Intl' + col_appendix, format=".0f")]
    ).configure_legend(
        orient='bottom'
    )

    st.altair_chart(chart_artists_desc, use_container_width=True)

#@st.cache_data
def gen_country_data(df, min_count=5):
    df_country = df.groupby('Country')
    df_domestic = df_country[['Country', "Domestic", "Domestic Scaled", "Intl", "Intl Scaled", "Total", "Total Scaled"]].sum()#.reset_index()
    df_domestic['% Domestic'] = round(df_domestic['Domestic'] / df_domestic['Total'] * 100, 1)
    df_domestic['% Domestic Scaled'] = round(df_domestic['Domestic Scaled'] / df_domestic['Total Scaled'] * 100, 1)
    df_domestic['% Intl'] = round(df_domestic['Intl'] / df_domestic['Total'] * 100, 1)
    df_domestic['% Intl Scaled'] = round(df_domestic['Intl Scaled'] / df_domestic['Total Scaled'] * 100, 1)
    df_domestic['Artist Count'] = df_country['Country'].count()
    df_domestic = df_domestic[df_domestic['Artist Count'] >= min_count]
    return df_domestic

def apply_filters(df_full):
    df = df_full.copy()

    # Genre
    if len(st.session_state.genre_filter) > 0:
        df = df.loc[df['Genre'].isin(st.session_state.genre_filter)]

    # Country
    if len(st.session_state.country_filter) > 0:
        df = df.loc[df['Country'].isin(st.session_state.country_filter)]

    # Sales
    df = df.loc[(df['Total'] >= st.session_state.min_sales*1000000) & (df['Total'] <= st.session_state.max_sales*1000000)]
    
    return df
    
if __name__ == '__main__':
    os.chdir("c:/Users/tb450/Desktop/Work etc/album_sales/github/album_sales/")
    df_full = load_data('album_sales_wide_5.csv', index_col="Artist")
    genres = sorted(list(set(df_full['Genre'])))
    countries = sorted(list(set(df_full['Country'])))

    load_sidebar()
    df_filtered = apply_filters(df_full)
    df_domestic = gen_country_data(df_filtered)

    tab_overview, tab_country_origin, tab_country_sale, tab_artist = st.tabs(["Overview", "Origin Country", "Sale Country","Artists"])
    
    with tab_country_origin:
        country_charts()

    with tab_artist:   
        artist_charts()

# TODO: add pages: 1) Overview, findings, sources etc 2) Country, 3) Artist
# TODO: add count of artists by country? top k artists by country? similar data but for sale country?
# TODO: fix trapt country, replace dashes with spaces instead of nothing
# TODO: make artist comp charts always display in the right order, fix column widths, annotations etc.