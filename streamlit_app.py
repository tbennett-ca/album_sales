import streamlit as st
import pandas as pd
import altair as alt

@st.cache_data
def load_data(loc, index_col):
    df = pd.read_csv(loc, index_col=index_col)
    return df

df = load_data('album_sales_wide_5.csv', index_col="Artist")
df = df[df['Total'] >= 5000000]
df = df.loc[df['Genre'].isin(['Pop','Rock','Metal','Punk','Indie'])]

st.write("Here's our first attempt at using data to create a table:")
# st.write(pd.DataFrame({
#     'first column': [1, 5, 3, 4],
#     'second column': [10, 20, 30, 40]
# }))

st.write(df.head())
df_sorted = df.reset_index().sort_values(["% Domestic", "Total"], ascending=[False, False])
sorted_artists = list(df_sorted['Artist'])
st.write(df_sorted.head())
#st.bar_chart(df_sorted, x="Artist", y="% Domestic")

# chart = alt.Chart(df_sorted).mark_bar().encode(
#    alt.X('Artist', sort=sorted_artists), #alt.EncodingSortField(field="% Domestic", op="sum", order='descending')),
#    alt.Y('% Domestic')
# ).interactive()

# chart2 = alt.Chart(df_sorted).mark_bar().encode(
#     alt.X("% Domestic", bin=True),
#     y='count()',
# )

x_var = 'Domestic Scaled'
y_var = 'Intl Scaled'

chart = alt.Chart(df_sorted).mark_circle().encode(
   alt.X(x_var, scale=alt.Scale(type="symlog")),
   alt.Y(y_var, scale=alt.Scale(type="symlog"))
).interactive()

line = pd.DataFrame({
    x_var: [0, 100000000],
    y_var: [0, 100000000],
})

line_plot = alt.Chart(line).mark_line(color= 'red').encode(
    x= x_var,
    y= y_var,
)

chart_layer = alt.layer(chart, line_plot)

st.altair_chart(chart_layer, theme=None, use_container_width=True)