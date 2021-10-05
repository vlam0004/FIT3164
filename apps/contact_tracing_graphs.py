#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import pycountry

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import app
import dash_bootstrap_components as dbc

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
dff = d[d['location'] == 'Australia']
dff = dff[['date', 'new_cases_smoothed']]
fig = px.line(dff, x='date', y='new_cases_smoothed', template='plotly_dark')

layout = dbc.Container([

    dbc.Row([html.H1("COVID 19 in your Country", style={'text-align': 'center'})]),
    html.Div(id='output_container', children=[]),
    html.Br(),
    html.H5("Please select a country", style={'text-align': 'left'}),
    dcc.Dropdown(id="slct_country",
                 options=options_list,
                 multi=False,
                 value='Australia',
                 style={'width': "40%"}
                 ),
    dbc.Row([dbc.Col(dbc.Card(dbc.CardBody(
        'This line chart depicts the number of new cases per million for the selected country month wise as well as '
        'the level of contact tracing implemented in that month for that country. this helps to showcase the fact '
        'that when countries implemented high contact tracing, the situation was somewhat under control.')),
        width={"size": 3}, align='center'),
        dbc.Col(

            dcc.Graph(id='contact_tracing', figure={})),

    ]),
    html.Br(), html.Br(),
    html.Div([
        html.Div(
            id='status', children=""
        ),
        dcc.Graph(id='myDiv', figure=fig),
        dcc.RangeSlider(id='slider',
                        min=0,
                        max=1000,
                        value=[0, dff.shape[0]],
                        updatemode='mouseup'),
        html.Button('>', id='button', n_clicks=0),
        dcc.Store(
            id='dataframe', data={}
        ),
        dcc.Interval(
            id='serverside-interval',
            interval=10000,
            n_intervals=1
        ),
        dcc.Interval(
            id='playing',
            n_intervals=1,
            interval=25,
            disabled=True
        ),
    ])
])


@app.callback(
    Output(component_id='contact_tracing', component_property='figure'),
    [Input("slct_country", "value")]
)
def update_graph(country):
    xx = merged[merged['CountryName'] == country]
    fig = go.Figure()
    # Full line
    fig.add_scattergl(x=xx["Month-Year"], y=xx.new_cases_smoothed_per_million, line={'color': 'cyan'},
                      name='No contact tracing')

    # Above threshold
    fig.add_scattergl(x=xx["Month-Year"], y=xx.new_cases_smoothed_per_million.where(xx['H3_Contact tracing'] == 1),
                      line={'color': 'red'}, name='Medium level tracing')

    fig.add_scattergl(x=xx["Month-Year"], y=xx.new_cases_smoothed_per_million.where(xx['H3_Contact tracing'] == 2),
                      line={'color': 'green'}, name='High level tracing')

    fig.update_layout(
        title="COVID-19 in" + country,
        xaxis_title="Month-Year",
        yaxis_title="Number of cases per million",
        legend_title="Contact tracing level",
        template='plotly_dark')

    return fig


@app.callback(
    Output('dataframe', 'data'),
    Output('slider', 'max'),
    Input('serverside-interval', 'n_intervals'),
    Input("slct_country", "value")
)
def update_store_data(n_intervals, country):
    dff = d[d['location'] == country]
    dff = dff[['date', 'new_cases_smoothed']]
    fig = px.line(dff, x='date', y='new_cases_smoothed', template='plotly_dark')
    return [dff['date'], dff['new_cases_smoothed']], dff.shape[0]


app.clientside_callback(
    """
    function(n_intervals, drag_value, value, data, not_playing) {
        value[0] = drag_value[0];
        if (not_playing) {
            value[1] = drag_value[1]
            new_data = {
            x: data[0].slice(value[0], value[1]),
            y: data[1].slice(value[0], value[1]),
            type: 'scatter'
            };
            data = [new_data];
            layout = {
                        title: 'COVID 19',
                        template: 'plotly_dark'
                    };
            Plotly.newPlot('myDiv', data, layout);
            return [value[0], value[1]];
        } else {
            if (drag_value[1] != value[1]) {
                value[1] = drag_value[1];
            } else {
                value[1] = value[1]+1;
            }
            new_data = {
            x: data[0].slice(value[0], value[1]),
            y: data[1].slice(value[0], value[1]),
            type: 'scatter'
            };
            data = [new_data];
             layout = {
                        title: 'COVID 19',
                        template: 'plotly_dark'
                    };
            Plotly.newPlot('myDiv', data, layout);
            return [value[0], value[1]];
        }
    }
    """,
    Output('slider', 'value'),
    Input('playing', 'n_intervals'),
    Input('slider', 'drag_value'),
    State('slider', 'value'),
    State('dataframe', 'data'),
    State('playing', 'disabled'),
    prevent_initial_call=True
)

app.clientside_callback(
    """
    function(n_clicks, not_playing) {
        if (not_playing) {
            return false;
        } else {
            return true;
        }
    }
    """,
    Output('playing', 'disabled'),
    Input('button', 'n_clicks'),
    State('playing', 'disabled'),
    prevent_initial_call=True
)

# ------------------------------------------------------------------------------
# if __name__ == '__main__':
#     app.run_server(debug=False)
#     print('hi')
