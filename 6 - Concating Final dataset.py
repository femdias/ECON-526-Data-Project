# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 11:14:08 2023

@author: Users
"""

import numpy as np
import pandas as pd
import os
import thefuzz
from thefuzz import process

# Setting working directory
os.chdir(r'C:\Users\femdi\Documents\UBC\ECON 526\Data Project')

''' Making Precipitation dataset as year summation'''
### Next lines are commented because it takes some minutes to run

# Import clima dataset
#df_rain = pd.read_csv('Outputs\Precipitation_Munic.csv') # 1 takes minute

## Calculating the sum of daily precipitation for every year
#df_rain['Year'] = df_rain['Date'].str.slice(0,4)
#df_rain = df_rain.groupby(['Code_Munic','Year']).sum()
#df_rain = df_rain.reset_index()
## Exporting
#df_rain.to_excel('Outputs\Precipitation_Munic_yearly.xlsx', index = False)


''' Working with the Electricity price dataset'''

# Importing Electricity prices dataset (in 2 parts)
df_elec_prices = pd.read_excel('Inputs\Electricity Prices.xlsx')
df_elec_prices_part2 = pd.read_excel('Inputs\Electricity Prices Part 2.xlsx')

# Concating dfs
df_elec_prices = pd.concat([df_elec_prices,df_elec_prices_part2], axis = 'rows').drop_duplicates().reset_index()

# Filtering the type of energy that what we want

#df_elec_prices.columns
#df_elec_prices['Subgrupo'].value_counts() 
#df_elec_prices['Posto'].value_counts() 
#df_elec_prices['Subgrupo'].value_counts() 
#df_elec_prices['Modalidade'].value_counts() 
#df_elec_prices['Classe'].value_counts() 
#df_elec_prices['Subclasse'].value_counts() 
#df_elec_prices['Detalhe'].value_counts() 
#df_elec_prices['Acessante'].value_counts() 

df_elec_prices1 = df_elec_prices[(df_elec_prices['Unidade'] == 'R$/MWh') &
                                (df_elec_prices['Posto'] == 'Não se aplica') &
                                (df_elec_prices['Base Tarifária'] == 'Tarifa de Aplicação') &
                                (df_elec_prices['Subgrupo'] == 'A4') &   # Price for companies that utilize energy with tension between 2.3kV and 25kV (https://c2e.com.br/grupos-tarifarios-o-que-sao-e-quais-sao-os-tipos/)
                                (df_elec_prices['Modalidade'] == 'Convencional') & # NAzul 
                                (df_elec_prices['Classe'] == 'Não se aplica') & # Removing residential, public ilumination, and rural
                                (df_elec_prices['Subclasse'] == 'Não se aplica') &
                                (df_elec_prices['Detalhe'] == 'Não se aplica') &
                                (df_elec_prices['Acessante'] == 'Não se aplica')] # The company buying doesn't matter

# Example of Company
# enel = df_elec_prices1[df_elec_prices1['Sigla'] == 'Enel SP']

# Selecting important columns
df_elec_prices2 = df_elec_prices1[['Sigla', 'Início Vigência', 'Fim Vigência','TE']]

# transforming dataset into a panel
# Code taken from: https://stackoverflow.com/questions/66865649/generating-date-range-from-dataframe-columns-with-start-and-end-dates
df_elec_prices2['Date'] = list(map(lambda x, y: pd.date_range(start=x, end=y),
                      df_elec_prices2['Início Vigência'], 
                      df_elec_prices2['Fim Vigência']))

df_elec_prices3 = df_elec_prices2.explode('Date').drop(['Início Vigência', 'Fim Vigência'], axis=1).reset_index(drop = True)


# Calculating the average price per year
df_elec_prices3['Year'] = [df_elec_prices3['Date'][i].year for i in range(len(df_elec_prices3))]
df_elec_prices4 = df_elec_prices3.groupby(['Year', 'Sigla']).mean().reset_index().drop('Date', axis = 1)

# rename
df_elec_prices4.columns = ['Year', 'Company', 'Electricity_Price']




''' Merging datasets together '''

# Reading Yearly rain dataset
df_rain = pd.read_excel('Outputs\Precipitation_Munic_yearly.xlsx')

# Selecting only years between 2010 and 2020
df_rain = df_rain[df_rain['Year'] >= 2010]

# Rename
df_rain.columns = ['Code', 'Year', 'Precipitation']

# Reading GDP dataset
df_GDP = pd.read_excel('Outputs\EconomicData_by_Municip.xlsx')

# Reading Agriculture Cultivated Area
df_agricult = pd.read_excel('Inputs\IBGE\Agriculture Production - PAM.xlsx')

# Reading Commodities price index from Brazilian Central Bank (Source: https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiU6MTO3ZKDAxU7DbkGHctVCHUQFnoECAsQAQ&url=https%3A%2F%2Fwww.bcb.gov.br%2Fcontent%2Findeco%2Findicadoresselecionados%2Fie-02.xlsx&usg=AOvVaw2cXvjQWhUB31uySua7FyfM&cshid=1702687751982034&opi=89978449)
df_commodities = pd.read_excel('Inputs\Commodities Index - BCB.xlsx')

# Importing dataset with companies and cities
df_companies = pd.read_excel('Outputs\Companies and Municipality Codes.xlsx')


##### FOR SIMPLICITY LETS DROP DUPLICATES BY ----> CHANGE LATTER
df_companies = df_companies.drop_duplicates(subset = 'City')


# Merging datasets
complete_df = df_companies.merge(df_elec_prices4, how = 'left', on = 'Company')

# Some companies without matches
Not_Match = complete_df[complete_df['Electricity_Price'].isna()][['Company']].drop_duplicates()


# Doing a fuzzy matching to match Companies names

####### Following https://stackoverflow.com/questions/13636848/is-it-possible-to-do-fuzzy-match-merge-with-python-pandas
# Using "thefuzz" library 
def fuzzy_match(df_left, df_right, column_left, column_right, threshold=90, limit=1):
    # Create a series
    series_matches = df_left[column_left].apply(
        lambda x: process.extract(x, df_right[column_right], limit=limit)            # Creates a series with id from df_left and column name _column_left_, with _limit_ matches per item
)
    # Convert matches to a tidy dataframe
    df_matches = series_matches.to_frame()
    df_matches = df_matches.explode(column_left)     # Convert list of matches to rows
    df_matches[
        ['match_string', 'match_score', 'df_right_id']
    ] = pd.DataFrame(df_matches[column_left].tolist(), index=df_matches.index)       # Convert match tuple to columns
    df_matches.drop(column_left, axis=1, inplace=True)      # Drop column of match tuples

    # Reset index, as in creating a tidy dataframe we've introduced multiple rows per id, so that no longer functions well as the index
    if df_matches.index.name:
        index_name = df_matches.index.name     # Stash index name
    else:
        index_name = 'index'        # Default used by pandas
    df_matches.reset_index(inplace=True)
    df_matches.rename(columns={index_name: 'df_left_id'}, inplace=True)       # The previous index has now become a column: rename for ease of reference

    # Drop matches below threshold
    df_matches.drop(
        df_matches.loc[df_matches['match_score'] < threshold].index,
        inplace=True)

    return df_matches

# Running function
df_matches = fuzzy_match(Not_Match, df_elec_prices4 ,'Company','Company',threshold=10,limit=1)

# Merging
df_output = Not_Match.merge(df_matches,how='left',left_index=True, right_on='df_left_id').reset_index(drop = True)
df_output = df_output.drop_duplicates('Company').sort_values('match_score')[['match_string', 'Company']]
df_output.columns = ['Company_map', 'Company_price']

# Fixing by hand
df_output.loc[df_output[df_output['Company_price'] == 'Boa Vista'].index,'Company_map'] = 'Roraima Energia'
df_output.loc[df_output[df_output['Company_price'] == 'UHENPAL'].index,'Company_map'] = 'Nova Palma'
df_output.loc[df_output[df_output['Company_price'] == 'EBO'].index,'Company_map'] = 'Energisa Borborema'
df_output.loc[df_output[df_output['Company_price'] == 'ETO'].index,'Company_map'] = 'Energisa TO'
df_output.loc[df_output[df_output['Company_price'] == 'ESE'].index,'Company_map'] = 'Energisa SE'
df_output.loc[df_output[df_output['Company_price'] == 'EPB'].index,'Company_map'] = 'Energisa PB'
df_output.loc[df_output[df_output['Company_price'] == 'EMT'].index,'Company_map'] = 'Energisa MT'
df_output.loc[df_output[df_output['Company_price'] == 'EMS'].index,'Company_map'] = 'Energisa MS'
df_output.loc[df_output[df_output['Company_price'] == 'EMR'].index,'Company_map'] = 'Energisa MG'
df_output.loc[df_output[df_output['Company_price'] == 'AME'].index,'Company_map'] = 'Amazonas Energia'
df_output.loc[df_output[df_output['Company_price'] == 'CERON'].index,'Company_map'] = 'Energisa RO'
df_output.loc[df_output[df_output['Company_price'] == 'CEBDIS'].index,'Company_map'] = 'CEB DIS'
df_output.loc[df_output[df_output['Company_price'] == 'CELPE'].index,'Company_map'] = 'Neoenergia Pernambuco'
df_output.loc[df_output[df_output['Company_price'] == 'CERAL ARAPOTI'].index,'Company_map'] = 'Ceral DIS'
df_output.loc[df_output[df_output['Company_price'] == 'CERAÇÁ'].index,'Company_map'] = 'Ceraça'
df_output.loc[df_output[df_output['Company_price'] == 'ELETROPAULO'].index,'Company_map'] = 'Enel SP'
df_output.loc[df_output[df_output['Company_price'] == 'ELETROACRE'].index,'Company_map'] = 'Energisa AC'
df_output.loc[df_output[df_output['Company_price'] == 'CPFL Jaguari'].index,'Company_map'] = 'CPFL Santa Cruz (anterior)'
df_output.loc[df_output[df_output['Company_price'] == 'CEEE-D'].index,'Company_map'] = 'CEEE Equatorial'
df_output.loc[df_output[df_output['Company_price'] == 'Equatorial GO'].index,'Company_map'] = 'Equatorial GO'
df_output.loc[df_output[df_output['Company_price'] == 'CEA'].index,'Company_map'] = 'CEA Equatorial'
df_output.loc[df_output[df_output['Company_price'] == 'COELBA'].index,'Company_map'] = 'Neoenergia Coelba'
df_output.loc[df_output[df_output['Company_price'] == 'CERTEL ENERGIA'].index,'Company_map'] = 'Certel'



### Replacing Companies names on df_companies with the correct one for making the match
df_companies1 = df_companies.merge(df_output, how = 'left', left_on = 'Company', 
                                        right_on = 'Company_price').drop(['Company_price'], axis = 'columns')

df_companies1["Company"] = df_companies1["Company_map"].fillna(df_companies1["Company"])
df_companies1 = df_companies1.drop("Company_map", axis = 'columns')


########## Finally merging data!

# Let's duplicate all those lines to each year
df_companies2 = pd.concat([df_companies1]*(2020-2010+1)).sort_index().reset_index(drop = True)
df_companies2['Year'] = list(range(2010,2020+1)) * int(len(df_companies2)/11)


# Merging again (Company df and Prices df), now by Year and Company
complete_df1 = df_companies2.merge(df_elec_prices4, how = 'left', on = ['Year', 'Company'])


# Merging with rain df, now by Year and city code
complete_df1 = complete_df1.merge(df_rain, how = 'left', on = ['Year', 'Code'])

# Merging with GDP df, now by Year and city code
complete_df1 = complete_df1.merge(df_GDP, how = 'left', on = ['Year', 'Code'])


# Calculating Precipitation per km2
complete_df1['Precipitation_per_km2'] = complete_df1['Precipitation'] / complete_df1['Area'] 

# Selecting columns
complete_df1 = complete_df1[['Company', 'City', 'Code', 'Year', 'Area', 'Electricity_Price', 
                             'Precipitation', 'Precipitation_per_km2', 'GDP', 'Share_Agriculture',
       'Share_Industry', 'Share_Services', 'Population', 'GDP_pc']]

# Looking at the missing data
missing = complete_df1[complete_df1['Electricity_Price'].isna()]


# Exporting
complete_df1.to_excel('Outputs\Complete_dataset.xlsx', index = False)




''' Aggregating data into cities from the same company '''

complete_df_agg = complete_df1.drop(['City', 'Code', 'GDP_pc', 'Precipitation_per_km2'], axis = 1).groupby(
    ['Company', 'Year']).sum().reset_index()

# Creating GDP per capita, Precipitation per km
complete_df_agg['GDP_pc'] = complete_df_agg['GDP'] / complete_df_agg['Population']
complete_df_agg['Precipitation_per_km2'] = complete_df_agg['Precipitation'] / complete_df_agg['Area']

# Exporting dataset
complete_df_agg.to_excel('Outputs\Aggregate_by_Company_dataset.xlsx', index = False)











