import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import pycountry
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

app = dash.Dash(__name__)
data = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
d = pd.read_csv(data)
d2 = pd.DataFrame(d.groupby(["location","date"])['total_cases_per_million'].sum())
d2 = d2.reset_index()

def getMonth(s):
  return s.split("-")[1]

def getYear(s):
  return s.split("-")[0]

d2['year']= d2['date'].apply(lambda x: getYear(x))
d2['month']= d2['date'].apply(lambda x: getMonth(x))

d3 = pd.DataFrame(d2.groupby(['location','year','month'])['total_cases_per_million'].max())

d3 = d3.reset_index()
d3['my'] = d3['month'].astype(str) + '-' + d3['year'].astype(str)
d3 = d3.drop(columns = ['month','year'])

li = ['Asia','Africa', 'World', 'Europe', 'European Union', 'North America', 'South America', 'Oceania']
new_df = d3[~d3.location.isin(li)]

def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None


new_df['iso_alpha_3'] = new_df['location'].apply(get_country_code)
new_df.reset_index()
app.layout = html.Div([

    html.H1("COVID 19 Dashboard", style={'text-align': 'center'}),
    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018}],
                 multi=False,
                 value=2015,
                 style={'width': "40%"}
                 ),

    dcc.Graph(id='choropleth_month_wise', figure={})

])

@app.callback(
    Output(component_id='choropleth_month_wise', component_property='figure'),
    [Input()]
)
def update_graph():

    # Plotly Express
    fig = px.choropleth(new_df,  # Input Dataframe
                        locations="iso_alpha_3",  # identify country code column
                        color="total_cases_per_million",  # identify representing column
                        hover_name="location",  # identify hover name
                        animation_frame="my",  # identify date column
                        projection="natural earth",  # select projection
                        color_continuous_scale='Peach',  # select prefer color scale
                        range_color=[0, 25000]  # select range of dataset
                        )

    return fig


# ------------------------------------------------------------------------------
# if __name__ == '__main__':
#     app.run_server(debug=False)
#     print('hi')



