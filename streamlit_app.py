import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import os
#import plotly.graph_objects as go
#from plotly.subplots import make_subplots
import plotly.express as px

st.set_page_config(
    page_title="Album Sales Data",
    page_icon="🎸",
    layout="wide",
)

@st.cache_data
def load_data(loc):
    df = pd.read_csv(loc)
    df.columns = df.columns.str.replace('Intl', 'International')
    for c in ['Domestic', 'International', 'Domestic Scaled', 'International Scaled', 'Total']:
        df[c] = round(df[c], 0)

    df['Artist'] = df['Artist OG']
    df['% Domestic'] = round(df['% Domestic'], 3)
    df['% Domestic Scaled'] = round(df['% Domestic Scaled'], 3)
    df['% International'] = 1-df['% Domestic']
    df['% International Scaled'] = 1-df['% Domestic Scaled']
    df = df.set_index('Artist')
    return df

@st.cache_data
def load_pop_data(loc):
    df = pd.read_csv(loc, index_col='Country')
    return df

#@st.cache_data(experimental_allow_widgets=True)
def load_sidebar():
    with st.sidebar:
        _ = st.radio(
                "Display actual sales/percentages or scale by market size?",
                ('Actual', 'Scaled'), horizontal=True, key='scaled'),
        st.multiselect('Select genres (all if blank)', options=genres, key='genre_filter')
        #st.multiselect('Select artist country (all if blank)', options=countries, default=None, key='country_filter')

        if "min_sales" not in st.session_state:
            st.session_state.min_sales = 0

        if "max_sales" not in st.session_state:
            st.session_state.max_sales = 500

        sales_col_1, sales_col_2 = st.columns(2)
        with sales_col_1:
            st.number_input('Enter min sales (millions)', min_value=0, max_value = 100, on_change=adjust_sales_filter, key='min_sales')
        with sales_col_2:
            st.number_input('Enter max sales (millions)', min_value=1, max_value = 500, on_change=adjust_sales_filter, key='max_sales')
        st.button('Reset Filters', key='reset', on_click=reset_filters)

def reset_filters():
    st.session_state.genre_filter = []
    st.session_state.min_sales = 0
    st.session_state.max_sales = 500

def adjust_sales_filter():
    st.session_state.max_sales = max(st.session_state.max_sales, st.session_state.min_sales+1)

@st.cache_data
def country_charts(df_domestic, col_appendix):
    ch1 = alt.Chart(df_domestic.reset_index()).mark_bar().transform_fold(
        fold=['Domestic' + col_appendix, 'International' + col_appendix], 
        as_=['‎', 'Sales']
    ).encode(
        y=alt.Y('Sales:Q'),
        x=alt.X('Country:N', title=''),
        color='‎:N',
        tooltip=['Country:N', 
                alt.Tooltip('Total' + col_appendix, format=","), 
                alt.Tooltip('Domestic' + col_appendix, format=","), 
                alt.Tooltip('International' + col_appendix, format=",")], 
    ).configure_legend(
        orient='bottom'
    )
    
    ch2 = alt.Chart(df_domestic.reset_index()).mark_bar().transform_fold(
        fold=['% Domestic' + col_appendix, '% International' + col_appendix], 
        as_=['‎', 'Percent']
    ).encode(
        y=alt.Y('Percent:Q'),
        x=alt.X('Country:N', title=''),
        color='‎:N',
        tooltip=['Country:N', 
                alt.Tooltip('Total' + col_appendix, format=","), 
                alt.Tooltip('% Domestic' + col_appendix, format=".1%"), 
                alt.Tooltip('% International' + col_appendix, format=".1%")]
    ).configure_legend(
        orient='bottom'
    )
    
    ### Average sales per artist, average artists per population

    sales_per_col = 'Sales' + col_appendix + '/Person'
    artists_per_mil_col = 'Artists/Million People'

    ch3 = alt.Chart(df_domestic.reset_index()).mark_bar().encode(
        alt.X('Country'),
        alt.Y(sales_per_col),
        color=alt.value('#e6d97a')
    )

    ch4 = alt.Chart(df_domestic.reset_index()).mark_bar().encode(
        alt.X('Country'),
        alt.Y(artists_per_mil_col),
        color=alt.value('mediumslateblue')
    )

    return ch1, ch2, ch3, ch4

@st.cache_data
def sale_country_charts(df_sale_country, col_appendix):

    ### Domestic/International sales by sale country

    min_sales = 10e6
    df_sale_country_filt = df_sale_country.loc[df_sale_country['Total' + col_appendix] >= min_sales, ["Total" + col_appendix, "Domestic" + col_appendix, 
                                                                                                      "International" + col_appendix, "% Domestic" + col_appendix, 
                                                                                                      "% International" + col_appendix]].reset_index()
    df_sale_country_filt = df_sale_country_filt.rename({'index': 'Country'}, axis=1)
    
    ch1 = alt.Chart(df_sale_country_filt).mark_bar().transform_fold(
        fold=['Domestic' + col_appendix, 'International' + col_appendix], 
        as_=['‎', 'Sales']
    ).encode(
        y=alt.Y('Sales:Q'),
        x=alt.X('Country:N', title=''),
        color='‎:N',
        tooltip=['Country:N', 
                alt.Tooltip('Total' + col_appendix +':Q', format=","), 
                alt.Tooltip('Domestic' + col_appendix, format=","), 
                alt.Tooltip('International' + col_appendix, format=",")], 
                # alt.Tooltip('% Domestic' + col_appendix, format=".0f"), 
                # alt.Tooltip('% International' + col_appendix, format=".0f")]
    ).configure_legend(
        orient='bottom'
    )

    ch2 = alt.Chart(df_sale_country_filt).mark_bar().transform_fold(
        fold=['% Domestic' + col_appendix, '% International' + col_appendix], 
        as_=['‎', 'Percent']
    ).encode(
        y=alt.Y('Percent:Q'),
        x=alt.X('Country:N', title=''),
        color='‎:N',
        tooltip=['Country:N', 
                alt.Tooltip('Total' + col_appendix +':Q', format=","),  
                alt.Tooltip('% Domestic' + col_appendix, format=".1%"), 
                alt.Tooltip('% International' + col_appendix, format=".1%")]
    ).configure_legend(
        orient='bottom'
    )

    ### Heatmap of slaes by origin/sale country

    df_sale_country_heatmap = df_sale_country.drop(['Total' + col_appendix, 'Domestic' + col_appendix, 'International' + col_appendix, '% Domestic' + col_appendix, '% International' + col_appendix], axis=1)
    df_sale_country_heatmap = round(df_sale_country_heatmap/df_sale_country_heatmap.sum(axis=0),3)*100

    ch3 = px.imshow(df_sale_country_heatmap.transpose(),
                    labels=dict(x="Sale Country", y="Origin Country", color="Percentage Sales" + col_appendix),
                    aspect='auto',
                    color_continuous_scale='Teal')

    return ch1, ch2, ch3

@st.cache_data        
def artist_charts(df_filtered, col_appendix):
    ### Histogram & Scatterplot

    histogram = alt.Chart(df_filtered).mark_bar(
        opacity=1,
        binSpacing=0
    ).encode(
        alt.X('% Domestic' + col_appendix + ':Q', bin=alt.Bin(maxbins=5), axis=alt.Axis(format='.0%')),
        alt.Y('count()'),
        color=alt.value('lightseagreen')
    )

    scatter = px.scatter(df_filtered.reset_index(), 
                     x="International" + col_appendix, y="Domestic" + col_appendix, 
                     hover_name="Artist", 
                     log_x=True, log_y=True,
                     range_x=[5e3, 5e8], range_y=[5e3, 5e8],
                     color_discrete_sequence=['lightcoral'])
    scatter.update_layout(shapes = [{'type': 'line', 'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 1, 'x0': 0, 'x1': 1}])

    return histogram, scatter

@st.cache_data
def get_artist_comp_charts(df_artist_comp, df_artist_long, col_appendix):
     
    ch1 = alt.Chart(df_artist_comp.reset_index()).mark_bar().transform_fold(
        fold=['Domestic' + col_appendix, 'International' + col_appendix], 
        as_=['‎', 'Sales']
    ).encode(
        y=alt.Y('Sales:Q'),
        x=alt.X('Artist:N', title=''),
        color='‎:N',
        tooltip=['Artist:N', 
                alt.Tooltip('Total' + col_appendix  +':Q', format=","),  
                alt.Tooltip('Domestic' + col_appendix, format=","), 
                alt.Tooltip('International' + col_appendix, format=",")]
    ).configure_legend(
        orient='bottom'
    )

    ch2 = alt.Chart(df_artist_long.reset_index()).mark_bar().encode(
        alt.X('Artist', sort=[st.session_state.artist1, st.session_state.artist2]),
        alt.Y('Sales' + col_appendix, axis=alt.Axis(format=',')),
        color='Country'
    ).interactive()

    return ch1, ch2
    
@st.cache_data
def get_chart_artists_full(df_sorted_desc, sorted_artists_desc, col_appendix): 
    ch1 = alt.Chart(df_sorted_desc).mark_bar().transform_fold(
        fold=['Domestic' + col_appendix, 'International' + col_appendix], 
        as_=['‎', 'Domestic/International']
    ).encode(
        y=alt.Y('Artist', sort=sorted_artists_desc),
        x=alt.X('Domestic/International:Q'),
        color='‎:N',
        tooltip=['Artist', 
                alt.Tooltip('Total' + col_appendix, format=","), 
                alt.Tooltip('Domestic' + col_appendix, format=","), 
                alt.Tooltip('International' + col_appendix, format=","), 
                alt.Tooltip('% Domestic' + col_appendix, format=".1%"), 
                alt.Tooltip('% International' + col_appendix, format=".1%")]
    ).configure_legend(
        orient='bottom'
    )

    ch2 = alt.Chart(df_sorted_desc).mark_bar().transform_fold(
        fold=['% Domestic' + col_appendix, '% International' + col_appendix], 
        as_=['‎', '% Domestic/International']
    ).encode(
        y=alt.Y('Artist', sort=sorted_artists_desc),
        # x=alt.X('% Domestic/International:Q', axis=alt.Axis(labelExpr='abs(datum.value)', tickCount=10)),
        x=alt.X('% Domestic/International:Q', axis=alt.Axis(tickCount=10)),
        color='‎:N',
        tooltip=['Artist', 
                alt.Tooltip('Total' + col_appendix, format=","), 
                alt.Tooltip('Domestic' + col_appendix, format=","), 
                alt.Tooltip('International' + col_appendix, format=","), 
                # alt.Tooltip('% Domestic OG' + col_appendix, format=".0f", title='% Domestic'), 
                alt.Tooltip('% Domestic' + col_appendix, format=".1%"), 
                alt.Tooltip('% International' + col_appendix, format=".1%")]
    ).configure_legend(
        orient='bottom'
    )
    return ch1, ch2


@st.cache_data
def gen_country_data(df, min_count=5):
    df_country = df.groupby('Country')
    df_domestic = df_country[['Country', "Domestic", "Domestic Scaled", "International", "International Scaled", "Total", "Total Scaled"]].sum()#.reset_index()
    df_domestic['% Domestic'] = round(df_domestic['Domestic'] / df_domestic['Total'], 3)
    df_domestic['% Domestic Scaled'] = round(df_domestic['Domestic Scaled'] / df_domestic['Total Scaled'], 3)
    df_domestic['% International'] = round(df_domestic['International'] / df_domestic['Total'], 3)
    df_domestic['% International Scaled'] = round(df_domestic['International Scaled'] / df_domestic['Total Scaled'], 3)
    df_domestic['Artist Count'] = df_country['Country'].count()
    df_domestic = df_domestic[df_domestic['Artist Count'] >= min_count]
    df_domestic['Population'] = df_domestic.merge(right=df_population, on='Country')['Population']
    df_domestic['Sales/Person'] = round(df_domestic['Total'] / df_domestic['Population'], 2)
    df_domestic['Sales Scaled/Person'] = round(df_domestic['Total Scaled'] / df_domestic['Population'], 2)
    df_domestic['Artists/Million People'] = round(df_domestic['Artist Count'] / df_domestic['Population'] * 1e6, 2)
    return df_domestic

@st.cache_data
def gen_country_top_wide(df_filtered, col_appendix):
    df_country_top = pd.DataFrame(df_filtered.groupby('Country')['Total' + col_appendix].nlargest(5))
    df_country_top['Rank'] = df_country_top.groupby('Country').rank(ascending=False, method='first')
    df_country_top_wide = df_country_top.drop('Total' + col_appendix, axis=1).reset_index().pivot_table(index='Country', columns='Rank', values='Artist', aggfunc=lambda x: ' '.join(x), fill_value='')
    df_country_top_wide.columns = ['Artist #' + str(i) for i in range(1, len(df_country_top_wide.columns)+1)]
    return df_country_top_wide

@st.cache_data
def gen_sale_country_data(df_filtered, col_appendix, sales_cols):
    def domestic_sales(df, c):
        sales = 0
        if c in df.columns:
            sales = df.loc[c,c]
        return sales

    df_sale_country = df_filtered.copy()
    df_sale_country = df_sale_country.set_index('Country')
    df_sale_country = df_sale_country.filter(regex=sales_cols + '\|', axis=1)
    df_sale_country.columns = df_sale_country.columns.str.replace(sales_cols + '\|', '', regex=True)
    df_sale_country = df_sale_country.groupby('Country').sum()
    df_sale_country = df_sale_country.transpose()
    df_sale_country['Total' + col_appendix] = df_sale_country.sum(axis=1)
    df_sale_country['Domestic' + col_appendix] = [domestic_sales(df_sale_country, c) for c in df_sale_country.index]
    df_sale_country['International' + col_appendix] = df_sale_country['Total' + col_appendix] - df_sale_country['Domestic' + col_appendix]
    df_sale_country['% Domestic' + col_appendix] = round(df_sale_country['Domestic' + col_appendix] / df_sale_country['Total' + col_appendix], 3)
    df_sale_country['% International' + col_appendix] = round(df_sale_country['International' + col_appendix] / df_sale_country['Total' + col_appendix], 3)
    
    return df_sale_country

@st.cache_data
def gen_sales_country_top(df_filtered, sales_cols):
    df_sale_top = df_filtered.copy()
    df_sale_top = df_sale_top.filter(regex=sales_cols + '\|', axis=1)
    df_sale_top.columns = df_sale_top.columns.str.replace(sales_cols + '\|', '', regex=True)
    df_sale_top = df_sale_top.transpose()
    df_sale_top['Top5'] = [";".join(df_sale_top.iloc[i][df_sale_top.iloc[i] != 0].nlargest(5).index) for i in range(len(df_sale_top))]
    df_sale_top = df_sale_top[df_sale_top['Top5'] != '']
    df_sale_top[['Artist #1', 'Artist #2', 'Artist #3', 'Artist #4', 'Artist #5']] = df_sale_top['Top5'].str.split(';',expand=True)
    df_sale_top = df_sale_top[['Artist #1', 'Artist #2', 'Artist #3', 'Artist #4', 'Artist #5']]
    df_sale_top = df_sale_top.fillna(' ')
    return df_sale_top

@st.cache_data
def get_sorted_artists(df_filtered, col_appendix, sort_col, sort_dir):
    sort_by = sort_col
    is_ascending = sort_dir == 'Ascending'

    if sort_by == 'Total Sales':
        df_sorted_desc = df_filtered.reset_index().sort_values(["Total" + col_appendix, "% Domestic" + col_appendix], ascending=[is_ascending, is_ascending])
    elif sort_by == 'Domestic Sales':
        df_sorted_desc = df_filtered.reset_index().sort_values("Domestic" + col_appendix, ascending=is_ascending)
    elif sort_by == 'International Sales':
        df_sorted_desc = df_filtered.reset_index().sort_values("International" + col_appendix, ascending=is_ascending)
    else:
        df_sorted_desc = df_filtered.reset_index().sort_values(["% Domestic" + col_appendix, "Total" + col_appendix], ascending=[is_ascending, is_ascending])
    
    sorted_artists_desc = list(df_sorted_desc['Artist'])
    return df_sorted_desc, sorted_artists_desc

@st.cache_data 
def get_comp_data(df_filtered, col_appendix):
    df_artist_comp = df_filtered.copy().filter(items=[st.session_state.artist1, st.session_state.artist2], axis=0)
    df_artist_comp_sales = df_artist_comp.filter(regex=sales_cols + '\|', axis=1)
    df_artist_comp_sales.columns = df_artist_comp_sales.columns.str.replace(sales_cols + '\|', '', regex=True)
    df_artist_long = pd.melt(df_artist_comp_sales, var_name='Country', value_name='Sales' + col_appendix, ignore_index=False)
    df_artist_long = df_artist_long.loc[df_artist_long['Sales' + col_appendix] > 0]
    return df_artist_comp, df_artist_long

@st.cache_data
def apply_filters(df_full, genre_filter, min_sales, max_sales):
    df = df_full.copy()

    # Genre
    if len(st.session_state.genre_filter) > 0:
        #df = df.loc[df['Genre'].isin(st.session_state.genre_filter)]
        genres = [g.lower() for g in genre_filter]
        df = df[pd.DataFrame(list(df['Genre'].str.split(', '))).isin(genres).any(1).values]

    # # Country
    # if len(st.session_state.country_filter) > 0:
    #     df = df.loc[df['Country'].isin(st.session_state.country_filter)]

    # Sales
    df = df.loc[(df['Total'] >= min_sales*1000000) & (df['Total'] <= max_sales*1000000)]
    
    return df

@st.cache_data
def get_genres(df):
    genres = []

    for gs in df['Genre']:
        gs_split = gs.split(', ')
        for g in gs_split:
            if not g.title() in genres:
                genres.append(g.title())
    return sorted(genres)
    
if __name__ == '__main__':
    os.chdir("c:/Users/tb450/Desktop/Work etc/album_sales/github/album_sales/")
    df_full = load_data('data/album_sales_wide_5.csv')
    #genres = sorted(list(set(df_full['Genre'])))
    genres = get_genres(df_full)
    countries = sorted(list(set(df_full['Country'])))
    df_population = load_pop_data('data/population_by_country_2020.csv')

    load_sidebar()
    df_filtered = apply_filters(df_full, st.session_state.genre_filter, st.session_state.min_sales, st.session_state.max_sales)

    if (st.session_state.scaled == 'Actual'):
        col_appendix = ""
        sales_cols = 'Sales' 
    else:
        col_appendix = " Scaled"
        sales_cols = 'Scaled'

    if len(df_filtered) == 0:
        st.write('No artists meet the filter criteria.')
    else:
        df_domestic = gen_country_data(df_filtered, min_count=1)
        df_country_top_wide = gen_country_top_wide(df_filtered, col_appendix)
        df_sale_country = gen_sale_country_data(df_filtered, col_appendix, sales_cols)

        tab_overview, tab_country_origin, tab_country_sale, tab_artist, tab_artist_full = st.tabs(["Overview", "Origin Country", "Sale Country", "Artist Comparison", "Full Artist Charts"])
        
        with tab_overview:
            st.write('# Album Sales Analysis')
            st.write('## Motivation')
            st.write('## Source Data')
            st.write('## Notable Findings')
            st.write('### International Artists')
            st.write('### Domestic Artists')
            st.write('### Best Countries for Each Genre')

        with tab_country_origin:
            st.write("### Album sales by origin country")

            chart_df_domestic, chart_df_domestic_pct, chart_sales_per, chart_artists_per = country_charts(df_domestic, col_appendix)

            col_1_1, col_1_2 = st.columns(2)

            ### Domestic/International sales by country

            with col_1_1:
                st.altair_chart(chart_df_domestic, use_container_width=True)

            with col_1_2:
                st.altair_chart(chart_df_domestic_pct, use_container_width=True)

            col_2_1, col_2_2 = st.columns(2)
            
            ### Average sales per artist

            with col_2_1:
                st.altair_chart(chart_sales_per, use_container_width=True)

            ### Average artists per population
            with col_2_2:
                st.altair_chart(chart_artists_per, use_container_width=True)

            ### Top artists by country            
            table_height = (len(df_country_top_wide)+1)*35 + 3
            st.dataframe(df_country_top_wide, height=table_height, use_container_width=True)

        with tab_country_sale:
            st.write("### Album sales by sale country")

            col_1_1, col_1_2 = st.columns(2)

            ### Domestic/International sales by sale country

            chart_sales_country, chart_sales_country_pct, chart_heat = sale_country_charts(df_sale_country, col_appendix)
            
            with col_1_1:
                st.altair_chart(chart_sales_country, use_container_width=True)

            with col_1_2:
                st.altair_chart(chart_sales_country_pct, use_container_width=True)

            ### Heatmap of slaes by origin/sale country

            st.plotly_chart(chart_heat, use_container_width=True)

            ### Top 5 artists by SALE country
            
            df_sale_top = gen_sales_country_top(df_filtered, sales_cols)
            table_height = (len(df_sale_top)+1)*35 + 3
            st.dataframe(df_sale_top, height=table_height, use_container_width=True)   

        with tab_artist:   
            st.write("### Album sales by artist")

            histogram, scatter = artist_charts(df_filtered, col_appendix)

            ### Histogram & Scatterplot

            col_1_1, col_1_2 = st.columns([1,2])

            with col_1_1:
                st.altair_chart(histogram, use_container_width=False)

            with col_1_2:
                st.plotly_chart(scatter)

            ### Artist comparison

            display_cols = ['Country', 'Genre', 'Total' + col_appendix, 'Domestic' + col_appendix, 'International' + col_appendix, "% Domestic" + col_appendix, "% International" + col_appendix]

            col_2_1, col_2_2 = st.columns(2)

            with col_2_1:
                st.selectbox('Artist #1', sorted(df_filtered.index), key='artist1')
                st.write(df_filtered[display_cols].filter(items=[st.session_state.artist1], axis=0).style.format(
                    {'Total' + col_appendix: "{:,.0f}", 'Domestic' + col_appendix: "{:,.0f}", 'International' + col_appendix: "{:,.0f}",
                    '% Domestic' + col_appendix: "{:.1%}", '% International' + col_appendix: "{:.1%}"}))

            with col_2_2:
                st.selectbox('Artist #2', sorted(df_filtered.index), index=1, key='artist2')
                st.write(df_filtered[display_cols].filter(items=[st.session_state.artist2], axis=0).style.format(
                    {'Total' + col_appendix: "{:,.0f}", 'Domestic' + col_appendix: "{:,.0f}", 'International' + col_appendix: "{:,.0f}",
                    '% Domestic' + col_appendix: "{:.1%}", '% International' + col_appendix: "{:.1%}"}))
            
            df_artist_comp, df_artist_long = get_comp_data(df_filtered, col_appendix)
            artist_comp_chart, artist_comp_chart_full = get_artist_comp_charts(df_artist_comp, df_artist_long, col_appendix)

            col_3_1, col_3_2 = st.columns(2)

            with col_3_1:
                st.altair_chart(artist_comp_chart, use_container_width=True)
            
            with col_3_2:
                st.altair_chart(artist_comp_chart_full, use_container_width=True)

        with tab_artist_full:
            st.write("### Domestic/International Sales By Artist")

            col_1_1, col_1_2 = st.columns(2)

            with col_1_1:
                st.radio('Sort by', ['Total Sales', 'Domestic Sales', 'International Sales', '% Domestic'], key='sort_col', horizontal=True)
            
            with col_1_2:
                st.radio('Sort direction', ['Descending', 'Ascending'], key='sort_dir', horizontal=True)

            # Get the sorted list
            
            df_sorted_desc, sorted_artists_desc = get_sorted_artists(df_filtered, col_appendix, st.session_state.sort_col, st.session_state.sort_dir)
            chart_artists_desc, chart_artists_desc_pct = get_chart_artists_full(df_sorted_desc, sorted_artists_desc, col_appendix)

            col_2_1, col_2_2 = st.columns(2)

            with col_2_1:
                ### Domestic/International Sales
                st.altair_chart(chart_artists_desc, use_container_width=True)

            with col_2_2: 
                ### % Domestic/International %
                st.altair_chart(chart_artists_desc_pct, use_container_width=True)

# TODO: overview page