import os
import us
import glob
import pandas as pd

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
# Set Data Directory
os.chdir(r'C:\Users\jreye\Documents\Projects\FBI-UCR\data\normalized')
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
    dcc.Graph(id='crime_map', figure={}, style={'width':'100%',\
                                                   'display':'inline-block'}
        ),
    # Create a Disclaimer for the percentages (%)
    html.Div(id='disclaimer', children=[\
        " * Percentages (%) of Crimes are total crimes per 500,000 people"]),
    # Create Break
    html.Br(),
    # Create Scatter Plot 
    # dcc.Graph(
    #     id='scatter_plot'),
    html.Br(),
    # Create a data table
    html.Div(dash_table.DataTable(
        id='table-paging-with-graph',
        columns=[{"name": i, "id": i} for i in crimesAll_df.columns],
        page_current=0,
        page_size=20,
        page_action='custom',
        
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
        ),
    ),
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


# Connect the Plotly graphs with Dash Components
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
        title_text= slct_crime+" in the USA",
        title_xanchor="center",
        title_font=dict(size=24),
        title_x=0.5,
        #margin=dict(l=60, r=60, t=50, b=50),
        geo=dict(
            scope='usa'),
    )
    return fig

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
    dff = dff[dff['Year'] == slct_year]
    items_l = []
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
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

def update_scatter(slct_year, slct_crime):
    dff = crimesAll_df.copy()
    dff = dff[dff['Year'] == slct_year]
    #dff = dff[slct_crime]
    #fig = px.scatter(dff, x="State", y="Violent Crime", color="Year")
    #print (dff)
    return dff


#app.config.supress_callback_exceptions = True

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)