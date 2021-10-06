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
from scipy.integrate import odeint

U0 = [10000, 0, 1, 0]
global latent_period, infectious_period, contact_rate
latent_period, infectious_period, contact_rate = 1 / 5, 1 / 14, 0.001
time = np.linspace(0, 30, 100)


def SEIR(U, t):
    return [-contact_rate * U[0] * U[2],
            contact_rate * U[0] * U[2] - latent_period * U[1],
            latent_period * U[1] - infectious_period * U[2],
            infectious_period * U[2]]


# 60.79905

layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1(children='COVID-19 SEIR Model'), className="mb-2")
        ]),
        dbc.Row([
            dbc.Col(html.H6(
            ), className="mb-4")
        ]),
        dcc.Graph(id='SEIR', figure={}),
        html.Br(),
        dbc.Row([dbc.Col(dbc.Card(dbc.CardBody('Latent Period')), width={"size": 2}, align='center'),
                 dbc.Col(dcc.Slider(
                     id='latent_period',
                     min=0.01,
                     max=1,
                     step=0.001,
                     value=1 / 5
                 ), align='center')]),
        html.Br(),
        dbc.Row([dbc.Col(dbc.Card(dbc.CardBody('Infectious Period')), width={"size": 2}, align='center'),
                 dbc.Col(
                     dcc.Slider(
                         id='infectious_period',
                         min=0.01,
                         max=1,
                         step=0.001,
                         value=1 / 14
                     ), align='center')]),
        html.Br(),
        dbc.Row([dbc.Col(dbc.Card(dbc.CardBody('Contact rate')), width={"size": 2}, align='center'),
                 dbc.Col(
                     dcc.Slider(
                         id='contact_rate',
                         min=0.0001,
                         max=0.01,
                         step=0.00001,
                         value=0.0001
                     ), align='center')])

    ])
])

@app.callback(
    Output(component_id='SEIR', component_property='figure'),
    [Input(component_id='latent_period', component_property='value'),
    Input(component_id='infectious_period', component_property='value'),
    Input(component_id='contact_rate', component_property='value')]
)
def update_graph(lp, ip, cr):

    global latent_period, infectious_period, contact_rate
    latent_period = lp
    infectious_period = ip
    contact_rate = cr

    results = odeint(SEIR, U0, time)
    S, E, I, R = results[:, 0], results[:, 1], results[:, 2], results[:, 3]

    fig = go.Figure()
    # Full line
    fig.add_scattergl(x=time, y=S, line={'color': 'green'}, name='Susceptible')
    # Above threshold
    fig.add_scattergl(x=time, y=E,
                      line={'color': 'orange'}, name='Exposed')

    fig.add_scattergl(x=time, y=I,
                      line={'color': 'red'}, name='Infected')

    fig.add_scattergl(x=time, y=R,
                      line={'color': 'cyan'}, name='Recovered')
    fig.update_layout(
        title="SEIR Model",
        xaxis_title="Time",
        yaxis_title="Value",
        legend_title="Legend",
        template='plotly_dark')

    return fig