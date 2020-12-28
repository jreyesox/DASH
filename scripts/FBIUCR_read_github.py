# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 00:46:25 2020

@author: jreye
"""

import pandas as pd
import requests
import io

def gitData(startYear, endYear):
    # Downloading the csv file from your GitHub account
    yyyy = list(range(startYear,endYear+1))
    gitFolder =\
    'https://raw.githubusercontent.com/jreyesox/FBI-UCR/main/data/normalized/'
    allFiles = []
    for year in yyyy:
        file = gitFolder+str(year)+'_crimes_byState.csv'
        print(file)
        df = pd.read_csv(file)
        allFiles.append(df)
    dff = pd.concat(allFiles)
    dff = dff.reset_index(drop=True)
    dff = dff.rename(columns={'Unnamed: 0':'checker'})
    return dff
#%%
blah = gitData(2013,2019)

