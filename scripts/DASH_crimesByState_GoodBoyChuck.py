# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 10:05:23 2020

@author: jreye
"""
import os
import us
import glob
import pandas as pd

import plotly.express as px
#import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

app = dash.Dash(__name__)

#%%
# Set Data Directory
os.chdir(r'C:\Users\jreye\Documents\Projects\FBI_UCR\data\normalized')
# Pull in Data 
dfs = []
for file in glob.glob('*.csv'):
    df = pd.read_csv(file)
    df = df[df.columns[1:]].reset_index(drop=True)
    dfs.append(df)

# Concatenate all data into one DataFrame
crimesAll_df = pd.concat(dfs, ignore_index=True)

state_abbrs = []
for x in crimesAll_df['State']:
    state = us.states.lookup(x)
    abbr = state.abbr
    state_abbrs.append(abbr)
crimesAll_df.insert(2,'State_Abbr',state_abbrs)
# % of Crimes per 500,000 people per State 
crimesAll_df[crimesAll_df.columns[14:]] = \
    crimesAll_df[crimesAll_df.columns[14:]]*500000
crimesAll_df[crimesAll_df.columns[14:]] =\
    crimesAll_df[crimesAll_df.columns[14:]].astype(int)
#%%
crimesAll_df = crimesAll_df.rename(columns={'State_Abbr':'State Abbr'})

years = crimesAll_df.Year.sort_values().unique().tolist()
crimes = crimesAll_df.columns[3:].unique().tolist()

#%%
### DASH App ####
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1("U.S. Crimes By State", style={'text-align':'center'}),
    html.Span('Year: ',style={'font-weight':'bold','display':'inline-block',\
                              'padding-left':50,'text-align':'center'}),
    dcc.Dropdown(id="slct_year",
                     options=[{'label' : y, 'value' : y} for y in years],
                     multi=False,
                     value=2019,
                     placeholder='Select Year',
                     style={'width':100,'display':'inline-block'},
        ),
    html.Span('Crime: ',style={'font-weight':'bold', 'display':'inline-block',\
                               'padding-left':25,'text-align': 'center'}),
    dcc.Dropdown(id="slct_crime",
                     options=[{'label' : c, 'value' : c} for c in crimes],
                     multi=False,
                     value='Violent Crime',
                     placeholder='Select Crime',
                     style={'width':200,'display':'inline-block'},
        ),
    html.Br(),
    dcc.Graph(id='my_crime_map', figure={}, style={'width':'100%',\
                                                   'display':'inline-block'}
        ),
    # Create a Disclaimer for the percentages (%)
    html.Div(id='disclaimer', children=[\
        " * Percentages (%) of Crimes are total crimes per 500,000 people"]),
    html.Br(),
    # Create a data table
    dash_table.DataTable(
        data=crimesAll_df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in crimesAll_df.columns],
        #fixed_rows={'headers': True},
        filter_action='custom',
        filter_query='',
        sort_action='custom',
        sort_mode='multi',
        sort_by=[],
        style_table={'height':'300px','overflowY':'auto'},
        style_cell={
            'height': 'auto',
            'whiteSpace': 'normal',
            #'overflowX':'normal',
            'width':'auto',
            },   
        style_cell_conditional=[
            {
                'if': {'column_id':'State'},
                'width':'100px'
                },
            ],
    ),
])
    
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='my_crime_map', component_property='figure'),
    Input(component_id='slct_year', component_property='value'),
    Input(component_id='slct_crime', component_property='value'))

def update_graph(slct_year, slct_crime):   
    
    print(slct_year, slct_crime)
    #print(type(slct_year),type(slct_crime))
    
    dff = crimesAll_df.copy()
    dff = dff[dff['Year'] == slct_year]
    #dff = dff[slct_crime]
    pops = dff['Population'].values
    crimes = [slct_crime]
        
    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='State Abbr',
        scope='usa',
        color= slct_crime,
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={slct_crime:slct_crime},
        template='plotly_dark',
        hover_data = [slct_crime],
    )
    fig.update_layout(
        title_text= slct_crime+" in the USA",
        title_xanchor="center",
        title_font=dict(size=24),
        title_x=0.5,
        #margin=dict(l=60, r=60, t=50, b=50),
        geo=dict(
            scope='usa'),
    )
    return fig




#app.config.supress_callback_exceptions = True

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
