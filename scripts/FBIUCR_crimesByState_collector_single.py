import os
import pandas as pd
import numpy as np
import us

#%%
# --------------------------------------------------------------------------
#### Crime Data Manipulation ####
# Import and clean data (importing csv into pandas)
rawFolder = r'C:\Users\jreye\Documents\Projects\FBI_UCR\data\raw'
YYYY = input('What YYYY? ')
data = '\\'+YYYY+'_Crime_in_the_United_States_by_State.xls'
inFile_df = pd.read_excel(rawFolder+data)
title = inFile_df.loc[0][0]
method, year = inFile_df.loc[1][0].split(',')
year = year.strip()
#%%
# --------------------------------------------------------------------------
####### Import and clean data #######
### State 'Name' manipulation ###
# Create DataFrame (name_df)
# Slice column from inFile mess that has 'State' names 
# Convert column to title() format
# Drop 'np.nan' values from column
# Rename generic column name to 'States' column
# Reset index and drop old index
stateName_df = pd.DataFrame(inFile_df[inFile_df.columns[0]].str.title().\
            dropna()).rename(columns={inFile_df.columns[0]:"State"}).\
            reset_index(drop=True)
#%%
# Using a 'For loop' and the 'US' PYPI python package to match, pull out, 
# and ensure correct spelling of 'State' name values
stateMatch = []
for x in stateName_df['State']:
    if ', 6' in x:    # found ', 6' was failing in 2014 data
        x = x.replace(', 6','')
    x = us.states.lookup(x)
    stateMatch.append(x)
stateName_df['State'] = stateMatch
# Two ways to drop the 'None' values within the 'States' column
#df = df.mask(df.astype(object).eq('None')).dropna()
stateName_df = stateName_df.replace(to_replace='None',value=np.nan).dropna()
#%%
# --------------------------------------------------------------------------
### Crime 'Total' manipulation ###
# Convert 'Total' for D.C. to 'State Totals' (for filtering)
inFile_df[inFile_df.columns[1]] = \
    inFile_df[inFile_df.columns[1]].str.replace('Total','State Total')
# Select 'State Total' rows from 'inFile_df' to create 'totals_df' 
crimes_df = inFile_df[inFile_df.apply(lambda r: r.str.contains(\
            'State Total', case=False).any(), axis=1)]
#%%
# Convert number value columns to 'Integer' columns
for col in crimes_df:
    crimes_df[col] = pd.to_numeric(crimes_df[col],errors='ignore')
#%%
# Drop Non-Integer Columns
non_ints = []
for col in crimes_df:
    if crimes_df[col].dtypes != 'int64':
        non_ints.append(col)
crimes_df = crimes_df.drop(columns=non_ints)        
#%%
# Rename columns to match the crime 'State Totals'
num_cols = len(crimes_df.columns)
if num_cols == 10:
    crimes_df.columns = ['Population','Violent Crime','Murder-Manslaughter',\
                     'Rape','Robbery','Aggravated Assault','Property Crime',\
                    'Burglary','Larceny-Theft','Motor Vehicle Theft']
elif num_cols == 11:
    crimes_df.columns = ['Population','Violent Crime','Murder-Manslaughter',\
                     'Rape','Rape-Legacy','Robbery','Aggravated Assault',\
                     'Property Crime','Burglary','Larceny-Theft',\
                     'Motor Vehicle Theft']
    
#%%
# Add State 'Name' to crime 'Total' dataframe to the first position
crimes_df.insert(0,'State',stateName_df.State.values)
crimes_df = crimes_df.reset_index(drop=True)
#%%
# --------------------------------------------------------------------------
### Calculate Percent Totals ###
# Divide all crime columns by 'Population' column
crimesPct_df = crimes_df[['Violent Crime', 'Murder-Manslaughter', 'Rape',
       'Robbery', 'Aggravated Assault', 'Property Crime', 'Burglary',
       'Larceny-Theft', 'Motor Vehicle Theft']].div(crimes_df.Population, axis=0)
crimesPct_df.columns = ['% Violent Crime', '% Murder-Manslaughter', '% Rape',
       '% Robbery', '% Aggravated Assault', '% Property Crime', '% Burglary',
       '% Larceny-Theft', '% Motor Vehicle Theft']
# Add to % data to 'crimes_df'
crimes_df = pd.concat([crimes_df,crimesPct_df],axis=1)
# --------------------------------------------------------------------------
### Add Crime Table Year to data ###
crimes_df.insert(0,'Year',year)
#%%
normFolder = \
    r'C:\Users\jreye\Documents\Projects\FBI_UCR\data\normalized'
crimes_df.to_csv(normFolder+'\\'+year+'_crimes_byState.csv')
