# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 23:09:45 2023

@author: Users
"""

import pandas as pd
import numpy as np
import os
import tqdm
from unidecode import unidecode
# pip install thefuzz
import thefuzz
from thefuzz import process
import geopandas as gpd
from shapely.geometry import Point, Polygon
from matplotlib import pyplot
import matplotlib.pyplot as plt
from shapely.validation import make_valid


# Setting working directory
os.chdir(r'C:\Users\femdi\Documents\UBC\ECON 526\Data Project')


# Bringing code and matching with the municipality name
Munic_Code =  pd.read_excel('Inputs/IBGE/Municipalities and Codes.xlsx')

# Rename 
Munic_Code.columns = ['Code', 'City']

# converting code to str
Munic_Code['Code'] = Munic_Code['Code'].astype(str)

# Reading dataset of Companies and Municipalities and dataset with units 
Companies_munic = pd.read_excel('Outputs/Companies and Municipalities.xlsx')
#df_comp_units = pd.read_excel('Outputs\Companies and Munic Qty of Households.xlsx')
#Companies_munic = pd.concat([Companies_munic, df_comp_units], axis = 'rows')

# Fixing number as str
#Companies_munic['Treated Unities'] = Companies_munic['Treated Unities'].str.replace('.', '').astype(float)


# Keeping the company that have most units in each city 
#Companies_munic = Companies_munic.sort_values(["Treated Unities"], ascending = False
#                                        ).drop_duplicates(subset = ["City"], keep = 'first'
 #                                       ).drop('Treated Unities', axis = 1).reset_index(drop = True)


# Removing rows with "Municipio - Estado"
Companies_munic = Companies_munic[Companies_munic['City'] != 'Município - Estado'].reset_index(drop = True)

# Adjusting the name of the city to have a perfect match
Munic_Code['City'] = [unidecode(Munic_Code.loc[i, 'City'].replace('´',"'")) for i in range(len(Munic_Code))]
Companies_munic['City'] = [unidecode(Companies_munic.loc[i, 'City'].replace(' - ', ' (').replace('´',"'")) + ")" for i in range(len(Companies_munic))]

# Merging
Companies_munic_codes = Companies_munic.merge(Munic_Code, how = 'left', on = 'City')


# Cities without Code (names slightly different)
not_merge = Companies_munic_codes[Companies_munic_codes['Code'].isna()]


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


# Making corrections by hand
not_merge.loc[not_merge[not_merge['City'] == 'Vila Alta (PR)'].index,'City'] = 'Alto Paraiso (PR)'
not_merge.loc[not_merge[not_merge['City'] == 'Augusto Severo (RN)'].index,'City'] = 'Campo Grande (RN)'
not_merge.loc[not_merge[not_merge['City'] == 'Campo de Santana (PB)'].index,'City'] = 'Barra de Santana (PB)'
not_merge.loc[not_merge[not_merge['City'] == 'Embu (SP)'].index,'City'] = 'Embu das Artes (SP)'
not_merge.loc[not_merge[not_merge['City'] == 'Sao Domingos de Pombal (PB)'].index,'City'] = 'Sao Domingos (PB)'
not_merge.loc[not_merge[not_merge['City'] == 'Presidente Juscelino (RN)'].index,'City'] = 'Serra Caiada (RN)'
not_merge.loc[not_merge[not_merge['City'] == 'Santarem (PB)'].index,'City'] = 'Joca Claudino (PB)'
not_merge.loc[not_merge[not_merge['City'] == 'Itabirinha de Mantena (MG)'].index,'City'] = 'Itabirinha (MG)'
not_merge.loc[not_merge[not_merge['City'] == 'Sao Valerio da Natividade (TO)'].index,'City'] = 'Sao Valerio (TO)'
not_merge.loc[not_merge[not_merge['City'] == 'Santa Teresinha (BA)'].index,'City'] = 'Santa Terezinha (BA)'


# Running function
df_matches = fuzzy_match(not_merge, Munic_Code,'City','City',threshold=80,limit=1)

# Merging
df_output = not_merge.merge(df_matches,how='left',left_index=True,
                      right_on='df_left_id')

# Merging with Munic_Code df
df_output = df_output.merge(Munic_Code, how='left',left_on='df_right_id',
                          right_index=True,suffixes=['_df1', '_df2'])

df_output.set_index('df_left_id', inplace=True)       # For some reason the first merge operation wrecks the dataframe's index. Recreated from the value we have in the matches lookup table

df_output = df_output[['Company','City_df1', 'Code_df2']]      # Drop columns used in the matching
df_output.columns = ['Company','City', 'Code']
######

# Concating and dropping na
Companies_munic_codes = pd.concat([Companies_munic_codes, df_output], axis = 'rows')
Companies_munic_codes = Companies_munic_codes.dropna()



################################################################
''' Making map '''

# Reading shapefile of Municipalities
map_br = gpd.read_file(r'Inputs\Shapefile Munic\BR_Municipios_2022.shp')

# Making geometries valid
map_br['geometry'] = map_br.apply(lambda row: make_valid(row.geometry) if not row.geometry.is_valid else row.geometry, axis=1)

# Adding municipality area to the final dataframe
Companies_munic_codes = Companies_munic_codes.merge(map_br[['CD_MUN', 'AREA_KM2']],
                                                    how = 'left', right_on = 'CD_MUN', 
                                                    left_on = 'Code')

Companies_munic_codes = Companies_munic_codes.drop('CD_MUN', axis = 1).rename(columns = {'AREA_KM2':'Area'})

# Exporting
Companies_munic_codes.to_excel('Outputs\Companies and Municipality Codes.xlsx', index = False)




# Merging with map of Brazil, to make the plot
map_br1 = map_br.merge(Companies_munic_codes, how = 'left', left_on = 'CD_MUN', right_on = 'Code')

# Plotting 1st bank
boundaries = map_br1.boundary
ax = map_br1.plot(column='Company',
                                     figsize=(30, 20), antialiased=False,
                                     missing_kwds={"color": "white"})
                                     #legend_kwds={'loc': 'lower right'})
boundaries.plot(ax = ax, color = 'black', linewidth = 0.2, alpha = 0.4)
ax.set_axis_off()
plt.savefig(f'Outputs/Figures/Map of Distributers.png',facecolor='white', bbox_inches = 'tight', dpi = 1000)  








