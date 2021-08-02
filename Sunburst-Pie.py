import pandas as pd
import plotly.express as px


import dash
import dash_core_components as dcc
import dash_html_components as heml
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
data = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'

df_date = pd.read_csv(data)
df_date = df_date.groupby(["location","date","continent"])[['total_cases']].sum()
df_date.reset_index(inplace=True)

df_date.date = pd.to_datetime(df_date.date)
df_date['day'] = df_date['date'].dt.day
df_date['month'] = df_date['date'].dt.month
df_date['year'] = df_date['date'].dt.year

df_year = df_date.groupby(["location","year","continent"])[['total_cases']].sum()
df_year_month = df_date.groupby(["location","year","month","continent"])[['total_cases']].sum()

df_date_pivot = pd.pivot_table(df_date, values=['total_cases','continent'], index='location', aggfunc=max)

df = px.data.tips()
fig = px.pie(df_date_pivot, values='total_cases', names='continent')
fig.show()

fig = px.sunburst(df_date, path=['continent', 'location'], values='total_cases')
fig.show()