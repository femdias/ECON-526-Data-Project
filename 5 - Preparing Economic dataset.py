# -*- coding: utf-8 -*-

'''
In this code, 
'''

import numpy as np
import pandas as pd
import os
import basedosdados as bd
import geopandas as gpd
from shapely.validation import make_valid

# Setting working directory
os.chdir(r'C:\Users\Users\Documents\UBC\ECON 526\Data Project')


####################### Economic Data ##############################

''' GDP data'''
# from 1999 to 2012
# GDP current value and % na agriculture, % industry ans % services
# Source: https://sidra.ibge.gov.br/tabela/21#/n6/all/v/37,516/p/all/d/v37%200,v516%202/l/,v+p,t/cfg/cod,
gdp_2012 = pd.read_excel(r'Inputs/IBGE/GDP by Municipality 1999 to 2012.xlsx', na_values = '...',
                    sheet_name = 0, header = 2).rename(columns = {'Unnamed: 0':'Code',
                                                                  'Unnamed: 1':'Municipality',
                                                                  'Unnamed: 2':'Year'})
# Dropping last columns and forward fill codes
gdp_2012 = gdp_2012.drop(gdp_2012.index[-1]).fillna(method='ffill')


# from 2002 to 2020 
# GDP current value and % na agriculture, % industry ans % services
# Source: https://sidra.ibge.gov.br/tabela/5938#/n6/all/v/37,516,520,6574/p/all/d/v37%200,v516%202,v520%202,v6574%202/l/,v,t+p/cfg/cod,
gdp_2020 = pd.read_excel(r'Inputs/IBGE/GDP by Municipality 2002 to 2020.xlsx', na_values = '...',
                sheet_name = 0, header = 2).rename(columns = {'Unnamed: 0':'Code',
                                                              'Unnamed: 1':'Municipality',
                                                              'Unnamed: 2':'Year'}).fillna(method='ffill')

# Dropping last columns and forward fill codes
gdp_2020 = gdp_2020.drop(gdp_2020.index[-1]).fillna(method='ffill')


# Concatting gdp_2012 and gdp_2020
gdp_final_1999_2020 = pd.concat([gdp_2012, gdp_2020], 'rows')

# Remove duplicates, keeping last values (years 1999, 2000 and 2001 wit come from
# gdp_2012 and the rest wil come from gdp_2020
gdp_final_1999_2020 = gdp_final_1999_2020.drop_duplicates(subset = ['Code', 'Municipality', 'Year'],
                                                          keep = 'last')

# Sorting by Code and Year 
gdp_final_1999_2020 = gdp_final_1999_2020.sort_values(['Code', 'Year']).reset_index(drop = True)

# Renaming and Selecting columns
gdp_final_1999_2020.columns = ['Code', 'Municipality', 'Year', 'GDP',
                               'Share_Agriculture', 'Share_Industry', 
                               'Share_Services1', 'Share_Services2']

gdp_final_1999_2020 = gdp_final_1999_2020[['Code', 'Municipality', 'Year', 'GDP',
                               'Share_Agriculture', 'Share_Industry']]


# Removing strange negative GDP of one city in 2012
gdp_final_1999_2020 = gdp_final_1999_2020[gdp_final_1999_2020["Municipality"] != 'Guamaré (RN)']

# If there are any negative numbers, make it zero. If is bigger than 100
gdp_final_1999_2020[[ 'GDP', 'Share_Agriculture', 'Share_Industry']] = gdp_final_1999_2020[[ 'GDP',
                                                                                            'Share_Agriculture', 'Share_Industry']].clip(lower = 0)
gdp_final_1999_2020[['Share_Agriculture', 'Share_Industry']] = gdp_final_1999_2020[['Share_Agriculture', 'Share_Industry']].clip(upper = 100)

# Creating % services
gdp_final_1999_2020['Share_Services'] = 100 - gdp_final_1999_2020['Share_Agriculture'] - gdp_final_1999_2020['Share_Industry']



''' GDP per capita '''
# Importing population table
population_1991_2021 = pd.read_excel(r'Outputs/Population_by_Municip.xlsx')
population_1991_2021['Code'] = population_1991_2021['Code'].astype(str).str.rstrip('.0').str.ljust(7, '0')

# GDP / population
gdp_pc_1999_2020 = gdp_final_1999_2020.merge(population_1991_2021, how = 'left', 
                               left_on = ['Year','Code'],
                               right_on = ['Year','Code'])

gdp_pc_1999_2020['GDP_pc'] = gdp_pc_1999_2020['GDP']/gdp_pc_1999_2020['Population']

# Removing duplicates
gdp_pc_1999_2020.drop_duplicates(['Year', 'Code'])

# Removing the 5 cities without GDP per capita (without population information)
gdp_pc_1999_2020 = gdp_pc_1999_2020.dropna(subset = 'GDP_pc').reset_index(drop = True)


# Exporting the complete dataset
gdp_pc_1999_2020.to_excel(r'Outputs/EconomicData_by_Municip.xlsx')

