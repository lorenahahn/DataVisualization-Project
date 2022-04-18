import json
from unicodedata import name
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import urllib.request as urllib
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots

# from urllib.request import urlopen
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff
import numpy as np

mapbox_access_token = "pk.eyJ1Ijoic2Ftb2h0Z3JvZW4iLCJhIjoiY2wyMXJyOWxpMGJucDNkcGZmenAyMmNydSJ9.ViAqJfKMMdYsKzChAW71KA"
df = pd.read_csv("drinks.csv")
df_alcoholdeaths = pd.read_csv('deaths-attributed-to-alcohol-use-by-age.csv')
df_deathbyriskfactor = pd.read_csv('number-of-deaths-by-risk-factor.csv')
external_stylesheets = [dbc.themes.BOOTSTRAP]


geojson = "countries.geojson"

data_geo = dict()
with open(geojson) as json_file:
    data_geo = json.load(json_file)
    
for feature in data_geo['features']:
    feature['id'] = feature['properties']['ADMIN']

geojson = data_geo

alcohol_options = [
    "beer_servings",
    "spirit_servings",
    "wine_servings",
]

df_beer = df.sort_values(by='beer_servings', ascending=False)
top_15_beer = df_beer.head(15)
top_30_beer = df_beer.head(30)

df_wine = df.sort_values(by='wine_servings', ascending=False)
top_15_wine = df_wine.head(15)
top_30_wine = df_wine.head(30)

df_spirit = df.sort_values(by='spirit_servings', ascending=False)
top_15_spirit = df_spirit.head(15)
top_30_spirit = df_spirit.head(30)

titles = ['Beer servings', 'Wine servings', 'Spirit servings']

countries_death = ['Portugal', 'Spain', 'France']

df_sub = df_alcoholdeaths.loc[df_alcoholdeaths['Entity'].isin(countries_death)]
new_df = pd.DataFrame(df_sub)

df_deathbyriskfactor.dropna(subset = ['Code'], inplace = True)
df_ad = df_deathbyriskfactor[df_deathbyriskfactor['Code'].str.contains('OWID_WRL')==False]
df_disease = df_ad.rename(columns={'Entity':'Country','Deaths - Cause: All causes - Risk: Alcohol use - Sex: Both - Age: All Ages (Number)': 'Alcohol use','Deaths - Cause: All causes - Risk: Smoking - Sex: Both - Age: All Ages (Number)':'Smoking','Deaths - Cause: All causes - Risk: Air pollution - Sex: Both - Age: All Ages (Number)':'Air pollution','Deaths - Cause: All causes - Risk: Drug use - Sex: Both - Age: All Ages (Number)':'Drug use'})
df_ad_update = df_disease.loc[df_disease['Year']==2015][['Country','Code','Year','Drug use', 'Alcohol use', 'Smoking', 'Air pollution']]
df_sorted = df_ad_update.sort_values(by='Drug use', ascending=False)
df_sorted_ause = df_ad_update.sort_values(by='Alcohol use', ascending=False)
df_sorted_ap = df_ad_update.sort_values(by='Air pollution', ascending=False)
df_sorted_sg = df_ad_update.sort_values(by='Smoking', ascending=False)
df_sorted_top_10 = df_sorted.head(10)
df_sorted_top_10_ause = df_sorted_ause.head(10)
df_sorted_top_10_ap = df_sorted_ap.head(10)
df_sorted_top_10_sg = df_sorted_sg.head(10)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dbc.Row(
            [
                
            dbc.Col(
                html.H1(
                    'Alcohol consumption in the world', 
                    style={'textAlign':'center', 'padding-top': '40px'},
                    ),
                width=12,),
            html.P(
                'Analysis of the relationship between alcohol consumption and beverages. As well as the alcohol consuption of the health impact',
                style={
                    'textAlign':'center',
                    'padding-bottom': '12px'
                }
            )
            
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    html.H6
                    (
                            'Consumption by alcohol type',
                            style=
                            {
                                'textAlign':'center',
                                'margin-top': '9px'
                             
                            }
                    ),
                    html.P
                    (
                            'The cultures in the world differ widely. The same applies to their alcohol drinking habits. The map on the right explores the alcohol consumption by beverages in liters per capita.',
                            style={'textAlign':'center'}
                    ),
                    dcc.RadioItems(
                            labelStyle=
                            {'display': 'block',},
                            style=
                            {
                                'padding': '12px',
                                'margin-top':'8px',
                                'margin-left': '66px'
                            },
                            id='alcohol_options',
                            options=alcohol_options,
                            value="beer_servings",
                            inline=False), 
                    ]    
                ),
                dbc.Col(
                    dcc.Graph(id="graph"), 
                    width=10,
                    style=
                    {
                        'padding': '12px',
                        'box-shadow': '2px 2px 2px lightgrey'
                    },
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    html.H4(
                      'Top countries based on alcohol consumption',
                      style={'textAlign': 'center', 'padding-top': '46px'},  
                    ),
                    html.P(
                        'In the bar chart below, the Top 15 countries based on alcohol beverages can be explored.',
                        style={'textAlign': 'center'}
                    ),
                    dcc.Graph
                    (
                        id="subplots",
                        style={
                            'padding': '12px',
                            'margin-bottom':'26px',
                            'margin-top': '0px'
                        }
                    ),
                    dcc.Slider(
                        id='slider-width', min=.1, max=.9,
                        value=0.5,  step=0.1,
                    ) 
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4(
                            'Consumption of total litres of pure alcohol based on continents',
                            style=
                            {'textAlign': 'center',
                             'margin-top': '46px',
                             'margin-bottom': '36px'
                             }
                        ),
                        dcc.Checklist(
                            id='checklist',
                            options=['Asia', 'Europe', 'Africa', 'North America', 'South America', 'Oceania'],
                            value=['Asia', 'Europe', 'Africa', 'North America', 'South America', 'Oceania'],
                            inline=True
                        ),
                        dcc.Graph
                        (
                            id='scatter_plot',
                            style={
                                'margin-top': '0px',
                                'box-shadow': '2px 2px 2px lightgrey'
                            }
                        ),
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4(
                            'Inspection of specific countries and alcohol related causes of death',
                            style=
                            {'textAlign': 'center',
                             'margin-top': '46px',
                             'margin-bottom': '36px',
                             }
                        ),
                        html.P
                        (
                            'In the Line chart on the left the Alcohol use and the alcohol related deaths in the countries Spain, Portugal and France can be explored.',
                            style={'textAlign':'center'}
                        ),
                        html.P
                        (
                            'The bar char on the right shows the deaths in the countries related to different diseases as well as alcohol use.',
                            style=
                            {
                                'textAlign':'center',
                                'margin-bottom':'36px'
                            }
                        ),
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Checklist(
                            id='checklist_country',
                            options=countries_death,   
                            value=countries_death,
                            inline=True,
                        ),
                        dcc.Graph(
                            id='scatter_plot_deaths',
                            style={
                                'box-shadow': '2px 2px 2px lightgrey'
                            }
                            ),
                    ],width=6
                ),
                dbc.Col(
                    [   dcc.Checklist(
                            id='checklist_c',
                            options=['Alcohol use', 'Drug use', 'Air pollution', 'Smoking'],
                            value=['Alcohol use', 'Drug use', 'Air pollution', 'Smoking'],
                            inline=True
                        ),
                        dcc.Graph(
                            id='group',
                            style={
                                'box-shadow': '2px 2px 2px lightgrey',
                                'margin-bottom': '54px'
                            }
                        ),
                    ],width=6
                ),
                dbc.Col(
                    [
                        html.H6(
                            'Sources:',
                            style={'textAlign':'center'}
                        ),
                        html.Span(
                            
                        ),
                        html.P(
                            'Our world in Data:',
                            style={'font-size':'10px', 'textAlign':'center'}
                        ),
                        html.P(
                            'https://ourworldindata.org/893932e5-eba5-4a5f-adf6-bf90448e0e9b',
                            style={'font-size':'10px', 'textAlign':'center'}
                            
                        ),
                        html.P(
                            'https://ourworldindata.org/d0ae7443-178d-42f0-a84d-4fe6830fdc11',
                            style={'font-size':'10px', 'textAlign':'center'}
                        ),
                        html.P(
                            'Kaggle:',
                            style={'font-size':'10px', 'textAlign':'center'}
                        ),
                        html.P(
                            'https://www.kaggle.com/datasets/cansky/drinks',
                            style={'font-size':'10px', 'textAlign':'center'}
                        ),
                        html.H6(
                            'Author: Lorena Hahn (m20211302@novaims.unl.pt)',
                            style={'font-size':'10px','textAlign':'center'}
                        )
                    ]
                )
            ]
        )
    ],style={'margin': '60px'}
)

#Choropleth
@app.callback(
    Output('graph', 'figure'), 
    Input('alcohol_options', 'value'))

def display_cloropleth(alcohol_options):
    fig = px.choropleth_mapbox(
        df, 
        geojson=geojson, 
        color=alcohol_options,
        locations='country', 
        featureidkey='properties.ADMIN',
        center={'lat': 56.5, 'lon': 11},
        zoom = 1.8,
    )
        
    fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    mapbox_accesstoken=mapbox_access_token)
        
    return fig

#Subplots
@app.callback(
    Output('subplots', 'figure'),
    Input('slider-width', 'value'))

def display_subplots(left_width):
    titles = ['Beer servings (top 15)', 'Wine servings (top 15)', 'Spirit servings (top 15)']
    fig_subplots = make_subplots(rows=1, cols=3,
                subplot_titles=titles, column_widths=[left_width, 1 - left_width, 1 - left_width])
    
    fig_subplots.add_trace(
    go.Bar(y=top_15_beer['beer_servings'], x=top_15_beer['country']), row=1, col=1
    )
    fig_subplots.add_trace(
    go.Bar(y=top_15_wine['wine_servings'], x=top_15_wine['country']), row=1, col=2
    )
    fig_subplots.add_trace(
    go.Bar(y=top_15_spirit['spirit_servings'], x=top_15_spirit['country']), row=1, col=3
    )
    fig_subplots.update_layout(showlegend=False)
    return fig_subplots

#Scatterplot
@app.callback(
    Output('scatter_plot', 'figure'),
    Input('checklist', 'value'))

def update_line_chart(continents):
    mask = df['continent'].isin(continents)
    fig_scatter = px.line(df[mask],
        x='country', y='total_litres_of_pure_alcohol', 
        color='continent',
        labels={'total_litres_of_pure_alcohol': 'Total litres: Pure alcohol'}
        )
    return fig_scatter

#Scatterplot_deaths
@app.callback(
    Output('scatter_plot_deaths', 'figure'),
    Input('checklist_country', 'value'))

def update_line_chart_deaths(countries_scatter):
    mask = new_df['Entity'].isin(countries_scatter)
    fig_scatter_spec = px.line(new_df[mask],
                    x = 'Year', 
                    y = 'Deaths - Cause: All causes - Risk: Alcohol use - Sex: Both - Age: 15-49 years (Number)',
                    labels={
                        'Deaths - Cause: All causes - Risk: Alcohol use - Sex: Both - Age: 15-49 years (Number)': 'Alcohol use'
                        },
                    color = 'Entity')
    return fig_scatter_spec

@app.callback(
    Output('group', 'figure'), 
    Input('checklist_c', 'value'))

def update_line_chart_use(countries):
    mask = df_sorted_top_10['Country'].isin(countries) 
    fig_ubc = px.bar(df_sorted_top_10[mask], x='Country', y='Drug use', 
                 color='Country', barmode='group')
    
    fig_ubc.add_trace(
    go.Bar(y=df_sorted_top_10_ause['Alcohol use'], x=df_sorted_top_10_ause['Country'], name='Alcohol use'),
    )
    fig_ubc.add_trace(
    go.Bar(y=df_sorted_top_10_sg['Smoking'], x=df_sorted_top_10_sg['Country'], name='Smoking'),
    )
    fig_ubc.add_trace(
    go.Bar(y=df_sorted_top_10_ap['Air pollution'], x=df_sorted_top_10_ap['Country'], name='Air pollution'),
    )
    fig_ubc.add_trace(
    go.Bar(y=df_sorted_top_10['Drug use'], x=df_sorted_top_10['Country'], name='Drug use'),
    )
    
    return fig_ubc


app.run_server(debug=True)

