# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 10:05:23 2020

@author: jreye
"""
import os
import us
import glob
import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
#import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
#%%
def gitData(startYear, endYear):
    # Downloading the csv file from your GitHub account
    yyyy = list(range(startYear,endYear+1))
    gitFolder =\
    'https://raw.githubusercontent.com/jreyesox/FBI-UCR/main/data/normalized/'
    allFiles = []
    for year in yyyy:
        file = gitFolder+str(year)+'_crimes_byState.csv'
        #print(file)
        df = pd.read_csv(file)
        allFiles.append(df)
    dff = pd.concat(allFiles)
    dff = dff.reset_index(drop=True)
    dff = dff.rename(columns={'Unnamed: 0':'checker'})
    return dff
#%%
crimesAll_df = gitData(2013,2019)

# # Set Data Directory
# os.chdir(r'C:\\folder\file.csv')
# # Pull in Data 
# dfs = []
# for file in glob.glob('*.csv'):
#     df = pd.read_csv(file)
#     df = df[df.columns[1:]].reset_index(drop=True)
#     dfs.append(df)

# # Concatenate all data into one DataFrame
# crimesAll_df = pd.concat(dfs, ignore_index=True)


#%%
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

crimesAll_df = crimesAll_df.rename(columns={'State_Abbr':'State Abbr'})

#%%
years = crimesAll_df.Year.sort_values().unique().tolist()
crimes = crimesAll_df.columns[3:].unique().tolist()
# Copy Data for plotting
dff = crimesAll_df.copy()

#%%
### DASH App ####
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1("U.S. FBI Uniform Crime Reports", style={'text-align':'center'}),
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
                     value="Violent Crime",
                     placeholder='Select Crime',
                     style={'width':200,'display':'inline-block'},
        ),
    # Create a Disclaimer for the percentages (%)
    html.Div(id='data-disclaimer', children=[\
        " * Percentages (%) of Crimes are total crimes per 500,000 people"]),
    html.Label([" * Data Collected from FBI website: ",\
                html.A('Crime in the U.S',\
                href='https://ucr.fbi.gov/crime-in-the-u.s')]),
    html.Br(),
    
    # Create Crime Graphs
    html.Div(children=[
        # Create Crime Map
        dcc.Graph(id='crime_map', figure={}, style={'width':'50%',\
                                                   'display':'inline-block'}
        ),
        # Create Crime Line Graph
        dcc.Graph(id='line_graph', figure={}, style={'width':'49%',\
                                                   'display':'inline-block',
                                                   'padding-left':10}
        ),
    ],style={'width':'100%', 'display':'inline-block'}),

    # Create Break
    html.Br(),
    
    # Create Scatter Plot
    html.Div(dcc.Graph(id='scatter_plot', figure={},style={'width':'100%',\
                                                   'display':'inline-block'}
        )),
    
    html.Br(),
    
    # Create a data table
    html.Div(children=[
        html.H1(
            children='U.S. Crime Data Table',
            style={
                'textAlign': 'center',
                'color': 'rgb(63, 63, 63)'
            }
        ),
        dash_table.DataTable(
            id='table-paging-with-graph',
            columns=[{"name": i, "id": i} for i in crimesAll_df.columns],
            fixed_rows={'headers': True},
            fixed_columns={'headers': True},
            page_current=0,
            page_size=20,
            page_action='custom',
            
            filter_action='custom',
            filter_query='',
            
            sort_action='custom',
            sort_mode='multi',
            sort_by=[],
            
            style_table={'height':'300px','overflowY':'auto'},
            style_cell={
                'height': 'auto',
                'whiteSpace': 'normal',
                'overflowX':'normal',
                'width':'auto',
                'backgroundColor': 'rgb(128,128,128)',
                'color':'lightgrey'
                },
            style_data_conditional=[
                {
                    'if':{'row_index':'even'},
                    'backgroundColor': 'rgb(84, 84, 84)'
                    }
            ],
            style_header={
                'backgroundColor': 'rgb(63, 63, 63)',
                'fontWeight': 'bold'
                }
            ),
        ]),

  ])


operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith '],
             ['in','IN']]

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


### Connect the Plotly graphs with Dash Components ###

# Update Crime Map
@app.callback(
    Output(component_id='crime_map', component_property='figure'),
    Input(component_id='slct_year', component_property='value'),
    Input(component_id='slct_crime', component_property='value'))

def update_map(slct_year, slct_crime):   
    print(slct_year, slct_crime)
    #print(type(slct_year),type(slct_crime))
    
    dff = crimesAll_df.copy()
    dff = dff[dff['Year'] == slct_year]
    #dff = dff[['Year',slct_crime]]
        
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
        title_text= slct_crime+" by State",
        title_xanchor="center",
        title_font=dict(size=24),
        title_x=0.5,
        #margin=dict(l=60, r=60, t=50, b=50),
        geo=dict(
            scope='usa'),
    )
    return fig

# Update Line Graph
@app.callback(
    Output(component_id='line_graph', component_property='figure'),
    Input(component_id='slct_year', component_property='value'),
    Input(component_id='slct_crime', component_property='value'))

def update_line(slct_year, slct_crime):
    dff = crimesAll_df.copy()
    dff_low = dff.loc[dff[slct_crime]< \
                dff[slct_crime].quantile(.05)][['State','Year',slct_crime]]
    dff_high = dff.loc[dff[slct_crime] > \
                dff[slct_crime].quantile(.95)][['State','Year',slct_crime]]
    states_low = dff_low.State.unique().tolist()
    states_high = dff_high.State.unique().tolist()
    dff["color"] = 'orange'
    dff['color'].loc[dff['State'].isin(states_low)] = 'lightgrey'
    dff['color'].loc[dff['State'].isin(states_high)] = 'red'    
    dff_color = dff[['State','color']].drop_duplicates()
    
    # color map is a dict with colors, lightgrey for most, {"Aruba": "lightgrey", ... "Japan: "blue", ...}
    color_map = {v["State"]: v["color"] for k,v in dff_color.iterrows()}
    #print(color_map)
    # show sample from the dictionary
    #{k:color_map[k] for k in color_map if k in ["California","Texas","Wyoming","Vermont"]}
    fig = px.line(dff, x="Year", y=slct_crime,\
                  color='State', color_discrete_map=color_map,\
                  template='plotly_dark')  
    fig.update_layout(
        title_text= slct_crime+" by Year",
        title_xanchor="center",
        title_font=dict(size=24),
        title_x=0.5),
    return fig

# Update Scatter PLot
@app.callback(
    Output(component_id='scatter_plot', component_property='figure'),
    Input(component_id='slct_year', component_property='value'),
    Input(component_id='slct_crime', component_property='value'))

def update_scatter(slct_year, slct_crime):
    dff = crimesAll_df.copy()
    fig = px.scatter(dff, x="State", y=slct_crime, color="Year",
        color_continuous_scale = px.colors.sequential.YlOrRd,
        template='plotly_dark')
    fig.update_layout(
        title_text= slct_crime+" Trends",
        title_xanchor="center",
        title_font=dict(size=24),
        title_x=0.5),   
    return fig

# Update Data Table 
@app.callback(
    Output('table-paging-with-graph', "data"),
    Input('table-paging-with-graph', "page_current"),
    Input('table-paging-with-graph', "page_size"),
    Input('table-paging-with-graph', "sort_by"),
    Input('table-paging-with-graph', "filter_query"),
    Input('slct_year', 'value'))

def update_table(page_current, page_size, sort_by, filter,slct_year):
    filtering_expressions = filter.split(' && ')
    dff = crimesAll_df.copy()
    #dff = dff[dff['Year'] == slct_year]
    #items_l = []
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name] == filter_value]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    return dff.iloc[
        page_current*page_size: (page_current + 1)*page_size
    ].to_dict('records')

#app.config.supress_callback_exceptions = True

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
