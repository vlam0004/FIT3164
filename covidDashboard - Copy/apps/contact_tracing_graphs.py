#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import pycountry

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

# app = dash.Dash(__name__)
data = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
d = pd.read_csv(data)
d2 = pd.DataFrame(d.groupby(["location", "date"])['new_cases_smoothed_per_million'].sum())
d2 = d2.reset_index()


def getMonth(s):
    return s.split("-")[1]


def getYear(s):
    return s.split("-")[0]


d2['year'] = d2['date'].apply(lambda x: getYear(x))
d2['month'] = d2['date'].apply(lambda x: getMonth(x))

d3 = pd.DataFrame(d2.groupby(['location', 'year', 'month'])['new_cases_smoothed_per_million'].sum())
d3 = d3.reset_index()

d3['my'] = d3['month'].astype(str) + '-' + d3['year'].astype(str)
d3 = d3.drop(columns=['month', 'year'])

d3['my'] = pd.to_datetime(d3['my'], format='%m-%Y')

d3['my'] = d3['my'].dt.strftime('%Y-%m')
d3.reset_index()

data2 = "https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv"

df2 = pd.read_csv(data2)

df3 = pd.DataFrame(df2.groupby(["CountryName", "Date"])['H3_Contact tracing'].max())
df3 = df3.reset_index()

df3['Date'] = pd.to_datetime(df3['Date'], format='%Y%m%d')

df3['year'] = df3['Date'].dt.year
df3['month'] = df3['Date'].dt.month
df3.reset_index()

df4 = pd.DataFrame(df3.groupby(['CountryName', 'year', 'month'])['H3_Contact tracing'].mean().round())

df4 = df4.reset_index()

df4['Month-Year'] = df4['month'].astype(str) + '-' + df4['year'].astype(str)
df4 = df4.drop(columns=['month', 'year'])

df4['Month-Year'] = pd.to_datetime(df4['Month-Year'], format='%m-%Y')

df4['Month-Year'] = df4['Month-Year'].dt.strftime('%Y-%m')
df4.reset_index()

merged = df4.merge(d3, how='inner', left_on=["CountryName", "Month-Year"], right_on=["location", "my"])

merged = merged.drop(columns=['location', 'my'])

options_list = []
countries = list(merged['CountryName'].unique())
for i in countries:
    options_list.append({'label': i, 'value': i})

layout = html.Div([

    html.H1("COVID 19 Dashboard", style={'text-align': 'center'}),
    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Dropdown(id="slct_country",
                 options=options_list,
                 multi=False,
                 value='Australia',
                 style={'width': "40%"}
                 ),

    dcc.Graph(id='contact_tracing', figure={}),
    dcc.Link('Go to page 1', href='/apps/dashboard')

])


@app.callback(
    Output(component_id='contact_tracing', component_property='figure'),
    [Input("slct_country", "value")]
)
def update_graph(country):
    xx = merged[merged['CountryName'] == country]
    fig = go.Figure()
    # Full line
    fig.add_scattergl(x=xx["Month-Year"], y=xx.new_cases_smoothed_per_million, line={'color': 'black'})

    # Above threshold
    fig.add_scattergl(x=xx["Month-Year"], y=xx.new_cases_smoothed_per_million.where(xx['H3_Contact tracing'] == 1),
                      line={'color': 'red'})

    fig.add_scattergl(x=xx["Month-Year"], y=xx.new_cases_smoothed_per_million.where(xx['H3_Contact tracing'] == 2),
                      line={'color': 'green'})

    return fig

# ------------------------------------------------------------------------------
# if __name__ == '__main__':
#     app.run_server(debug=False)
#     print('hi')
