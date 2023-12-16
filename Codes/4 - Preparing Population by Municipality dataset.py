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


''' Table with Population municipal by Year (2001 a 2019), downloaded in SIDRA'''

# Lendo arquivo baixado em: https://sidra.ibge.gov.br/tabela/6579#/g/86/v/all/p/all/l/v,p,t/cfg/cod, 
population_hist = pd.read_excel(r'Inputs/IBGE/Population by Municipality IBGE.xlsx', 
                          header = 3, sheet_name = 0, na_values = '...').fillna(0)
# Renaming
population_hist = population_hist.rename(columns = {'Unnamed: 0':'Code',
                                                  'Unnamed: 1':'Municipality'})
population_hist['Code_6dig'] = [str(population_hist.loc[j,'Code'])[:6] for j in range(len(population_hist))]


''' Population from 1992 to 1999 IBGE's estimates  '''

# Source: https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html?=&t=downloads
for i in [1992,1993,1994,1995,1997,1998,1999]:
    #Importing
    pop_year = pd.read_excel(fr'Inputs/IBGE/estimativa_populacao_{i}.xls',header = 2)
    
    # Renaming and formatting municipality code
    pop_year.columns = ['UF', 'Code_State', 'Code_Munic', 'Municipality', str(i)]
    pop_year['Code_6dig'] = [str(pop_year.loc[j,'Code_State']).replace('.0','') + str(pop_year.loc[j,'Code_Munic']).replace('.0','').zfill(4) for j in range(len(pop_year))]
    
    # Adding to population dataset
    population_hist = population_hist.merge(pop_year[['Code_6dig',str(i)]], how = 'left', on = 'Code_6dig')
    
                        
''' Population from 1991, 2000 and 2010 Census and 2007 and 1996 count '''
#2000 e 2010
# Source: https://sidra.ibge.gov.br/tabela/202#/n1/all/n6/all/u/y/v/allxp/p/1991,2000,2010/c2/0/c1/0/l/v,p+c2,t+c1/cfg/cod,
population_censo = pd.read_excel(r'Inputs/IBGE/Population by Municipality Census 1991 2000 and 2010.xlsx', 
                          header = 5, sheet_name = 0, na_values = '...').fillna(0)
# Renaming
population_censo.columns = ['Code', 'Municipality', 'Total', '1991', '2000', '2010']

# Selecting
population_censo = population_censo[['Code', '1991', '2000', '2010']]

#2007
# Source: https://sidra.ibge.gov.br/tabela/579#/n6/all/v/2049/p/all/c1/6795/l/v,p+c1,t
pop_2007 = pd.read_excel(r'Inputs/IBGE/Population by Municipality Count 2007.xlsx', 
                          header = 4, sheet_name = 0, na_values = '...').fillna(0)
# Renaming
pop_2007.columns = ['Code', 'Municipality', '2007']

# Selecting
pop_2007 = pop_2007[['Code', '2007']]


#1996
# Source: https://sidra.ibge.gov.br/tabela/305#/n6/all/v/allxp/p/all/c293/0/c1/0/l/v,p+c293,c1+t
pop_1996 = pd.read_excel(r'Inputs/IBGE/Population by Municipality Count 1996.xlsx', 
                          header = 4, sheet_name = 0, na_values = '...').iloc[:,1:].fillna(0)
# Renaming
pop_1996.columns = ['Code', 'Municipality', '1996']

# Selecting
pop_1996 = pop_1996[['Code', '1996']]

# Converting Codes to string
pop_1996['Code'] = pop_1996['Code'].astype(str).str.rstrip('.0')


'''  Merging everthing '''

population_1991_2021 = population_hist.merge(population_censo, how = 'left', on = 'Code')
population_1991_2021 = population_1991_2021.merge(pop_2007, how = 'left', on = 'Code')
population_1991_2021 = population_1991_2021.merge(pop_1996, how = 'left', on = 'Code')


# The 2007 count was made only form cities with more than 160k population. So, there are
# a few missing values. In this case, let's use the mean between 2006 and 2008
# Furthermore, some municipalities have the 2000 population as zero, In these cases,
# we calculate it pop from 2001 * (2001/2002)
for i in range(len(population_1991_2021)):
    if pd.isna(population_1991_2021.loc[i,'2007']):
        population_1991_2021.loc[i,'2007'] = (population_1991_2021.loc[i,'2006'] + population_1991_2021.loc[i,'2008'])/2
   # if population_1991_2021.loc[i,'2000'] == 0:
     #   population_1991_2021.loc[i,'2000'] = (population_1991_2021.loc[i,'2001']/population_1991_2021.loc[i,'2002'])*population_1991_2021.loc[i,'2001']


# Removing 6 cities with missing population in 2010
population_1991_2021 = population_1991_2021.dropna(subset = '2010')


#Pivoting the table
population_1991_2021 = pd.melt(population_1991_2021, id_vars = 'Code', 
                         value_vars=['1991', '1992', '1993', '1994', 
                                     '1995', '1996', '1997', '1998',
                                     '1999', '2000', '2001', '2002', 
                                     '2003', '2004', '2005', '2006', 
                                     '2007', '2008', '2009', '2010',
                                     '2011', '2012', '2013', '2014',
                                     '2015', '2016', '2017', '2018',
                                     '2019', '2020', '2021'], 
                         var_name='Year', value_name = 'Population')


#Transforming year column to float
population_1991_2021['Year'] = population_1991_2021['Year'].astype(int)

# Export
population_1991_2021.to_excel(r'Outputs/Population_by_Municip.xlsx', index = False)


