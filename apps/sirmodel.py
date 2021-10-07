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
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody('This specific SEIR model can be used to model the vital dynamics of '
                                          'COVID-19. By adjusting each parameter, you will be able to see how it '
                                          'affects the different curves in the graph. The purpose of this simulator '
                                          'is not to be a predictive model, but more so to show the user the severity '
                                          'when an epidemic is not controlled. Note that this simple model omits '
                                          'variables such as birth rates, death rates, or the case that the person is '
                                          'asymptomatic but still infectious. The provided link will show a more '
                                          'detailed model with more parameters. - '
                                          'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7376536/')))
        ]),
        html.Br(),
        dcc.Graph(id='SEIR', figure={}),
        html.Br(),

        dbc.Row([dbc.Col(dbc.Card(dbc.CardBody('Latent Period')), width={"size": 2}, align='center'),
                 dbc.Col(dcc.Slider(
                     id='latent_period',
                     min=1,
                     max=14,
                     step=1,
                     marks={
                         1: '1',
                         14: '14'
                     },
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
                         marks={
                             0.01: '0.01',
                             1: '1'
                         },
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
                         marks={
                             0.0001: '0.0001',
                             0.01: '0.01'
                         },
                         value=0.0001
                     ), align='center')]),
        html.Br(),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([html.H4("Latent period", className="card-title"),
                                           html.P('The latent period, also known as the incubation time of a disease, '
                                                  'is the time where a person is exposed but not yet showing symptoms '
                                                  'and being able to spread the disease. By having a shorter latent '
                                                  'period (when the slider is to the right), the disease will spread '
                                                  'more violently as it will take less time for a person who has been '
                                                  'infected to be able to spread the disease. On the other hand, '
                                                  'if the disease has a longer latent period (when the slider is to '
                                                  'the left), it will take longer before an exposed person will be '
                                                  'able to spread it. The latent period may not be able to be '
                                                  'controlled but it does encourage the general public to get tested '
                                                  'as soon as they know that they may have been in a COVID-19 hotspot. '
                                                  'Therefore, this supports the use of contact tracing applications, '
                                                  'as it informs the public and enables them the choice to get tested '
                                                  'earlier and begin isolating if they do test positive. '

                                                  ,
                                                  className="card-text",
                                                  )
                                           ])))
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([html.H4("Infectious period", className="card-title"),
                                           html.P('The infectious period, also known as the time before recovery, '
                                                  'is the period before an infectious person has recovered from the '
                                                  'disease. By increasing the time before recovery (when the slider is '
                                                  'to the left), you will increase the amount of people who will be '
                                                  'infected at the same time, and by decreasing the time before '
                                                  'recovery (when the slider is to the right), you will decrease the '
                                                  'amount of people who will be infected at the same time as this will '
                                                  'have people recover from the disease at a faster rate. Vaccines are '
                                                  'an effective way of decreasing the time of recovery as people who '
                                                  'catch COVID-19 will have milder symptoms and therefore are more '
                                                  'likely to recover at a faster rate than those who have not received '
                                                  'the vaccine and are more prone to having more severe symptoms. '

                                                  ,
                                                  className="card-text",
                                                  )
                                           ])))
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([html.H4("Contact rate", className="card-title"),
                                           html.P('The contact rate is known as the probability of making contact with '
                                                  'someone who has the disease and becoming exposed. By decreasing the '
                                                  'contact rate (when the slider is to the left), you are lowering the '
                                                  'probability of a susceptible person making contact with an infected '
                                                  'person, and if you increase the contact rate (when the slider is to '
                                                  'the right), you are increasing the probability. The contact rate '
                                                  'relates to the current situation of the pandemic. When people who '
                                                  'are infected isolate, the community practices social distancing and '
                                                  'wear masks, they can lower the chance of a healthy person '
                                                  'contracting the disease. '

                                                  ,
                                                  className="card-text",
                                                  )
                                           ])))
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody('All these factors can be altered in some way or can be applied to our '
                                          'current situation in the pandemic, by taking proper precautions as well as '
                                          'taking initiative, we will be able to flatten the curve and reduce the '
                                          'severity of this disease.')))
        ]),
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
