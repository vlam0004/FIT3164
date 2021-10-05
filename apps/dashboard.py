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

external_stylesheets = [dbc.themes.CYBORG]
# app = dash.Dash(__name__)
data = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
data2 = "https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv"
d = pd.read_csv(data)
d2 = pd.DataFrame(d.groupby(["location", "date"])['total_cases_per_million'].sum())
d2 = d2.reset_index()


def getMonth(s):
    return s.split("-")[1]


def getYear(s):
    return s.split("-")[0]


d2['year'] = d2['date'].apply(lambda x: getYear(x))
d2['month'] = d2['date'].apply(lambda x: getMonth(x))

d3 = pd.DataFrame(d2.groupby(['location', 'year', 'month'])['total_cases_per_million'].max())

d3 = d3.reset_index()
d3['Month-Year'] = d3['month'].astype(str) + '-' + d3['year'].astype(str)
d3 = d3.drop(columns=['month', 'year'])

li = ['Asia', 'Africa', 'World', 'Europe', 'European Union', 'North America', 'South America', 'Oceania']
new_df = d3[~d3.location.isin(li)]


def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None


new_df['iso_alpha_3'] = new_df['location'].apply(get_country_code)
new_df.reset_index()

dn2 = pd.DataFrame(d.groupby(["location", "date", "continent"])['new_cases_smoothed_per_million'].sum())
dn2 = dn2.reset_index()

dn2['year'] = dn2['date'].apply(lambda x: getYear(x))
dn2['month'] = dn2['date'].apply(lambda x: getMonth(x))
dn3 = pd.DataFrame(dn2.groupby(['location', 'year', 'month', 'continent'])['new_cases_smoothed_per_million'].sum())

dn3 = dn3.reset_index()

dn3['my'] = dn3['month'].astype(str) + '-' + dn3['year'].astype(str)
dn3 = dn3.drop(columns=['month', 'year'])

new_dfn = dn3[~dn3.location.isin(li)]

new_dfn['my'] = pd.to_datetime(new_dfn['my'], format='%m-%Y')

new_dfn['my'] = new_dfn['my'].dt.strftime('%Y-%m')
new_dfn.reset_index()
df2 = pd.read_csv(data2)
df3 = pd.DataFrame(df2.groupby(["CountryName", "Date"])['H3_Contact tracing'].max())
df3 = df3.reset_index()
df3['Date'] = pd.to_datetime(df3['Date'], format='%Y%m%d')
df3['year'] = df3['Date'].dt.year
df3['month'] = df3['Date'].dt.month
df3.reset_index()
df4 = pd.DataFrame(df3.groupby(['CountryName', 'year', 'month'])['H3_Contact tracing'].mean().round())

df4 = df4.reset_index()
dn2 = dn2.rename({
    'location': 'CountryName'
}, axis='columns')
df4['Month-Year'] = df4['month'].astype(str) + '-' + df4['year'].astype(str)
df4 = df4.drop(columns=['month', 'year'])
df4['Month-Year'] = pd.to_datetime(df4['Month-Year'], format='%m-%Y')
df4['Month-Year'] = df4['Month-Year'].dt.strftime('%Y-%m')
merged = df4.merge(new_dfn, how='inner', left_on=["CountryName", "Month-Year"], right_on=["location", "my"])
oka = pd.DataFrame(merged.groupby(["CountryName", "H3_Contact tracing"])['new_cases_smoothed_per_million'].sum())
oka = oka.reset_index()
merged['iso_alpha_3'] = merged['location'].apply(get_country_code)
merged.reset_index()

# create a list of our conditions
conditions = [
    (merged['H3_Contact tracing'] == 0.0),
    (merged['H3_Contact tracing'] == 1.0),
    (merged['H3_Contact tracing'] == 2.0),
    (merged['H3_Contact tracing'].isnull())
]

# create a list of the values we want to assign for each condition
values = ['No Contact Tracing', 'Mediocre Contact Tracing', 'High Contact Tracing', 'No Data']

# create a new column and use np.select to assign values to it using our lists as arguments
merged['Contact Tracing'] = np.select(conditions, values)
merged[merged['new_cases_smoothed_per_million'] < 0] = 0
conditions2 = [
    (oka['H3_Contact tracing'] == 0.0),
    (oka['H3_Contact tracing'] == 1.0),
    (oka['H3_Contact tracing'] == 2.0),
    (oka['H3_Contact tracing'].isnull())
]
oka['Contact Tracing'] = np.select(conditions2, values)

layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1(children='COVID-19 Worldwide at a glance'), className="mb-2")
        ]),
        dbc.Row([
            dbc.Col(html.H6(
            ), className="mb-4")
        ]),
        dbc.Row([dbc.Col(dbc.Card(dbc.CardBody('This interactive choropleth map depicts the total cases per million '
                                               'for all the countries on the map. It has an interactive slider below '
                                               'it which can be played as well as set to a specific month. You can '
                                               'also hover your mouse over any country to get the exact data for '
                                               'that country')), width={"size": 3}, align='center'),
                 dbc.Col(
                     dcc.Graph(id='choropleth_month_wise',
                               figure=px.choropleth(new_df,  # Input Dataframe
                                                    locations="iso_alpha_3",  # identify country code column
                                                    # identify representing column
                                                    hover_name="location",  # identify hover name
                                                    animation_frame="Month-Year",  # identify date column
                                                    projection="natural earth",  # select projection
                                                    color="total_cases_per_million",
                                                    title="Choropleth map of Total Cases per million",
                                                    width=1000, height=600,
                                                    color_continuous_scale=px.colors.sequential.Redor,
                                                    template="plotly_dark"
                                                    # select range of dataset
                                                    )), width={"size": 9})]),

        # dcc.Graph(id='sunburst_contact_tracing',
        #           figure=px.sunburst(oka, path=['Contact Tracing', 'CountryName'],
        #                              values='new_cases_smoothed_per_million')),
        html.Br(),
        dbc.Row([dbc.Col(dcc.Graph(id='treemap_contact_tracing',
                                   figure={})),
                 dbc.Col(dbc.Card(dbc.CardBody('This is an interactive treemap which depicts the level of contact '
                                               'tracing(given by the section/colour that the country is in) as well '
                                               'as the number of cases per million for that country*given by the size '
                                               'of the box of that country) in a particular month. The treemap has an '
                                               'interactive slider below which can be used to select whichever month '
                                               'the user would like to see.')), width={"size": 3}, align='center')]),
        dbc.Row([dbc.Col(dcc.Slider(
            id="slider",
            min=0,
            max=len(merged['Month-Year'].unique()) - 1,
            value=0,
            marks={i: str(merged['Month-Year'].unique()[i]) for i in range(len(merged['Month-Year'].unique()))},
            step=1,
        ))]),


    ])
])


@app.callback(
    Output(component_id='treemap_contact_tracing', component_property='figure'),
    [Input("slider", "value")]
)
def update_graph(yr):
    yr = merged['Month-Year'].unique()[yr]
    new = merged[merged['Month-Year'] == yr]
    fig = px.treemap(new, path=[px.Constant("World"), new['Contact Tracing'], new['continent'],
                                new['CountryName'], ], values=new['new_cases_smoothed_per_million'],
                     title="Treemap depicting Contact Tracing data", template="plotly_dark", color_discrete_sequence=px.colors.sequential.Sunsetdark)

    return fig
# if __name__ == '__main__':
#     app.run_server(debug=False)
