import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
            st.number_input('Enter min sales (millions)', min_value=0, max_value = 100, value=0, on_change=adjust_sales_filter, key='min_sales')
        with sales_col_2:
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
                    height=table_height)
        
def artist_charts():
    # TODO: update content, fix trapt country

    st.write("### Album sales by artist")
    if (st.session_state.scaled == 'Actual'):
        col_appendix = ""
    else:
        col_appendix = " Scaled"

    df_sorted_desc = df_filtered.reset_index().sort_values(["% Domestic" + col_appendix, "Total" + col_appendix], ascending=[False, False])#[:25]
    #df_sorted_desc = df_filtered.reset_index().sort_values("Domestic" + col_appendix, ascending=False)#[:25]
    df_sorted_desc['% Domestic' + col_appendix] = -1*df_sorted_desc['% Domestic' + col_appendix]
    sorted_artists_desc = list(df_sorted_desc['Artist'])

    # def percentFormat(x):
    #     return np.abs(x)
    
    # alt.Config(customFormatTypes=True)
    # alt.themes.register('percentFormat', percentFormat)

    # TODO: fix this and rename
    def pub_theme():
        return {'config': {"axisX": {"labelExpr": "isNumber(datum.label) ? datum.label : abs(datum.label)"}}} #"replace(datum.label, '-', '')"}}}
    alt.themes.register('pub', pub_theme)
    alt.themes.enable('pub')

    chart_artists_desc_1 = alt.Chart(df_sorted_desc).mark_bar(color='#0068C9').encode(
       alt.Y('Artist', sort=sorted_artists_desc),
       alt.X('% Domestic' + col_appendix)#, axis=alt.Axis(formatType='percentFormat')) 
    )#.interactive()

    chart_artists_desc_2 = alt.Chart(df_sorted_desc).mark_bar(color='#83C9FF').encode(
       alt.Y('Artist', sort=sorted_artists_desc),
       alt.X('% Intl' + col_appendix)
    )

    st.altair_chart(chart_artists_desc_1 + chart_artists_desc_2, theme=None, use_container_width=True)

    # chart_artists_desc = alt.Chart(df_sorted_desc).mark_bar().encode(
    #    alt.Y('Artist', sort=sorted_artists_desc), #alt.EncodingSortField(field="% Domestic", op="sum", order='descending')),
    #    alt.X('% Domestic' + col_appendix)
    # )#.interactive()

    # plotly
    # create subplots
    # fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
    #                     shared_yaxes=True, horizontal_spacing=0)

    # fig.append_trace(go.Bar(y=df_sorted_desc['Artist'], x=df_sorted_desc['Domestic']*-1, orientation='h', width=0.4, showlegend=False, marker_color='#4472c4'), 1, 1)
    # fig.append_trace(go.Bar(y=df_sorted_desc['Artist'], x=df_sorted_desc['Intl'], orientation='h', width=0.4, showlegend=False, marker_color='#ed7d31'), 1, 2)
    # fig.update_yaxes(showticklabels=False) # hide all yticks
    
    # annotations = []
    # for i, row in df.iterrows():
    #     if row.label1 != '':
    #         annotations.append({
    #             'xref': 'x1',
    #             'yref': 'y1',
    #             'y': i,
    #             'x': row.value1,
    #             'text': row.value1,
    #             'xanchor': 'right',
    #             'showarrow': False})
    #         annotations.append({
    #             'xref': 'x1',
    #             'yref': 'y1',
    #             'y': i-0.3,
    #             'x': -1,
    #             'text': row.label1,
    #             'xanchor': 'right',
    #             'showarrow': False})            
    #     if row.label2 != '':
    #         annotations.append({
    #             'xref': 'x2',
    #             'yref': 'y2',
    #             'y': i,
    #             'x': row.value2,
    #             'text': row.value2,
    #             'xanchor': 'left',
    #             'showarrow': False})  
    #         annotations.append({
    #             'xref': 'x2',
    #             'yref': 'y2',
    #             'y': i-0.3,
    #             'x': 1,
    #             'text': row.label2,
    #             'xanchor': 'left',
    #             'showarrow': False})

    # fig.update_layout(annotations=annotations)
    #st.plotly_chart(fig, use_container_width=False)
    #st.altair_chart(chart_artists_desc, theme=None, use_container_width=True)

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
    
    country_charts()
    artist_charts()

### Artists sorted 

#df = df.loc[df['Genre'].isin(['Pop','Rock','Metal','Punk','Indie'])]
# df_sorted_desc = df.reset_index().sort_values(["% Domestic", "Total"], ascending=[False, False])[:25]
# sorted_artists_desc = list(df_sorted_desc['Artist'])

# chart_artists_desc = alt.Chart(df_sorted_desc).mark_bar().encode(
#    alt.Y('Artist', sort=sorted_artists_desc), #alt.EncodingSortField(field="% Domestic", op="sum", order='descending')),
#    alt.X('% Domestic')
# ).interactive()

# df_sorted_asc = df.reset_index().sort_values(["% Domestic", "Total"], ascending=[True, False])[:25]
# sorted_artists_asc = list(df_sorted_asc['Artist'])

# chart_artists_asc = alt.Chart(df_sorted_asc).mark_bar().encode(
#    alt.Y('Artist', sort=sorted_artists_asc), #alt.EncodingSortField(field="% Domestic", op="sum", order='descending')),
#    alt.X('% Domestic')
# ).interactive()

# col_2_1, col_2_2 = st.columns(2)

# with col_2_1:
#     #st.bar_chart(df[["Domestic" + col_appendix, "Intl" + col_appendix]])
#     st.altair_chart(chart_artists_desc, theme=None, use_container_width=True)

# with col_2_2:
#     st.altair_chart(chart_artists_asc, theme=None, use_container_width=True)