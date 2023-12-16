# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 14:13:38 2023

@author: Users
"""

import numpy as np
import pandas as pd
import os
#import basedosdados as bd
import geopandas as gpd
from shapely.validation import make_valid
#pip install ipeadatapy
import ipeadatapy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Setting working directory
os.chdir(r'C:\Users\femdi\Documents\UBC\ECON 526\Data Project')

# Finding GDP per capita dataset
ipeadatapy.list_series('PIB per capita')

# Describe dataset
ipeadatapy.describe('GAC_PIBCAPR')

# Getting data
data_GDP = ipeadatapy.timeseries("GAC_PIBCAPR", yearGreaterThan=1990)

# Plotting GDP per capita 
data_GDP['Year'] = data_GDP.index.year.astype(int)
data_GDP = data_GDP.set_index('Year')


# Plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(data_GDP['VALUE (R$ de 2022)'], color='black', label='GDP per capita')

# painting 2010's decade
for i in data_GDP.index[20:29]:
    plt.axvspan(i, i+1, facecolor='lightblue', alpha=0.5, zorder=-100)
    
ax.grid(axis='y', color='lightgrey', linestyle='dashed') # Grid lines
ax.tick_params(axis='x', rotation=90)
ax.tick_params(axis='y',  left='on')
ax.set_xticks(data_GDP.index)

# Create legend
# Manually creating a legend  (https://stackoverflow.com/questions/39500265/how-to-manually-create-a-legend)
handles, labels = ax.get_legend_handles_labels()
# manually define a new patch 
patch = mpatches.Patch(color='lightblue', label="2010's decade")
# handles is a list, so append manual patch
handles.append(patch) 
# plot the legend
plt.legend(handles=handles, loc='upper left')


plt.savefig('Outputs/Figures/GDP per capita.png', dpi = 1000, bbox_inches='tight')
plt.show()



############# DAGs

import graphviz as gr

g = gr.Digraph()
g.edge("Electricity Price", "GDP", style = 'dashed')
g.edge("Business Cycles", "GDP")
g.edge("Business Cycles", "Political Cycles")
g.edge("Political Cycles", "GDP")
g.edge("Political Cycles", "Electricity Price")
g.edge("Business Cycles", "Electricity Price")
g.edge("Rain", "Electricity Price")
g.node("Rain", style="filled")
g.view()





