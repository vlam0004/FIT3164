import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import pycountry
import numpy as np
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_table
from app import app

card1 = dbc.Card(
    [
        dbc.CardImg(src="/assets/world.png", top=True),
        dbc.CardBody(
            [
                html.H4("COVID-19 Worldwide", className="card-title"),
                html.P(
                    "The Worldwide visualisations page shows you different "
                    "COVID 19 trends across the world.",
                    className="card-text",
                ),
                dbc.Button("Worldwide visualisations", color="primary", href='/apps/dashboard'),
            ]
        ),
    ],

)
card2 = dbc.Card(
    [
        dbc.CardImg(src="/assets/country.jpg", top=True),
        dbc.CardBody(
            [
                html.H4("Country wise", className="card-title"),
                html.P(
                    "The country-wise visualisations show you COVID 19 "
                    "trends as per your selected country.",
                    className="card-text",
                ),
                dbc.Button("Countrywise visualisations", color="primary", href='/apps/contact_tracing_graphs'),
            ]
        ),
    ],

)
card3 = dbc.Card(
    [
        dbc.CardImg(src="/assets/virus.jpg", top=True),
        dbc.CardBody(
            [
                html.H4("SIR model", className="card-title"),
                html.P(
                    "The SEIR model allows you to visualize how COVID 19 "
                    "progresses.",
                    className="card-text",
                ),
                dbc.Button("SIR model", color="primary", href='/apps/sirmodel'),
            ]
        ),
    ],

)
data = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
data2 = "https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv"
df = pd.read_csv(data)
total_cases = df.loc[df.location == 'World', ['total_cases']].max()
new_cases = df.loc[df.location == 'World', ['new_cases']].max()
total_deaths = df.loc[df.location == 'World', ['total_deaths']].max()
new_deaths = df.loc[df.location == 'World', ['new_deaths']].max()
layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1(children='Welcome to our COVID 19 Dashboard!'), className="mb-2")
        ]),
        dbc.Row(
            [dbc.Col(dbc.Alert("Total number of people affected by COVID:", color="primary"), width=4),
             dbc.Col(dbc.Alert(html.Div(
                 id='placeholder', children="..."
             ), color="danger"), width=2)]), dcc.Interval(
            id='serverside-interval',
            interval=5000,
            n_intervals=1
        ),
        dbc.Row(
            [dbc.Col(dbc.Alert("Total number of deaths due to COVID:", color="primary"), width=4),
             dbc.Col(dbc.Alert(html.Div(
                 id='placeholder2', children="..."
             ), color="danger"), width=2)]), dcc.Interval(
            id='serverside-interval2',
            interval=5000,
            n_intervals=1
        ),
        dbc.Row([
            dbc.Col(html.H4(children='Aim of this Dashboard'), className="mb-2")
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody('One of the most severe public health crises our world has faced, '
                                          'the coronavirus disease, has not only posed a serious threat to human '
                                          'life, but has significantly impacted our social and economic activity. In '
                                          'order to survive such a pandemic, we have to effectively control the '
                                          'infectious disease, this can be achieved through many interventions such '
                                          'as quarantining and travelling restrictions. Contact tracing is one of the '
                                          'most effective ways of identifying such a situation as the virus has an '
                                          'incubation period which may allow the spread through asymptomatic '
                                          'infection while remaining undetected. Despite this, there seems to be no '
                                          'widespread integration of digital contact tracing strategies across the '
                                          'world. We aim to equip the population with a better understanding of '
                                          'epidemiology so that they may participate in reducing and preventing the '
                                          'spread of the disease. We aim to achieve this with the help of '
                                          'visualizations, information and simulations to help educate the general '
                                          'public to the severity of COVID-19.')))
        ]),
        html.Br(), html.Br(),
        dbc.Row([dbc.Col(card1, width=4),
                 dbc.Col(card2, width=4), dbc.Col(card3, width=4)] )

    ])])


@app.callback(
    Output('placeholder', 'children'),
    Input('serverside-interval', 'n_intervals'),
)
def update_cases(n_intervals):
    data1 = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
    df1 = pd.read_csv(data1)
    total_cases1 = df1.loc[df1.location == 'World', ['total_cases']].max()
    return total_cases1


@app.callback(
    Output('placeholder2', 'children'),
    Input('serverside-interval2', 'n_intervals'),
)
def update_deaths(n_intervals):
    data3 = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
    df2 = pd.read_csv(data3)
    total_deaths2 = df2.loc[df2.location == 'World', ['total_deaths']].max()
    return total_deaths2
