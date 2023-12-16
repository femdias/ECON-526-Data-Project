# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 17:47:24 2023

@author: Users
"""

import selenium
import pandas as pd
import numpy as np
import time
import webdriver_manager
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import ChromiumOptions
from webdriver_manager.chrome import ChromeDriverManager
import os
import tqdm

# Setting working directory
os.chdir(r'C:\Users\Users\Documents\UBC\ECON 526\Data Project')

# Chromedriver installation (when needed)
chrome_options = ChromiumOptions()
#chrome_options.headless = True
service = Service(ChromeDriverManager().install())

# Opening Chrome
driver = webdriver.Chrome(chrome_options=chrome_options, service=service)


# Opening Correios site
driver.get("https://www2.aneel.gov.br/relatoriosrig/(S(1yv0z3e43octrt4tig1vs4cx))/relatorio.aspx?folder=sfe&report=MunicipiosdecadaDistribuidora")

# Options of the drop in menu
dropdown = driver.find_element(By.CLASS_NAME, 'aspNetDisabled')
options = [x.text for x in dropdown.find_elements(By.TAG_NAME, "option")]

# Loop around each option 
df_results = pd.DataFrame(columns = ["Company", "City"])


for i in tqdm.tqdm(options[1:]):
    
    # Selecting option i 
    select = Select(driver.find_element(By.CLASS_NAME,'aspNetDisabled'))
    select.select_by_visible_text(i)
    
    
    botton = driver.find_element(By.ID,'ReportViewer1_ctl04_ctl00')
    botton.click()
    
    #Waiting until the website loads complety 
    wait = WebDriverWait(driver,15).until(
         EC.presence_of_element_located((By.ID, "VisibleReportContentReportViewer1_ctl10")))
            
    time.sleep(10)
    # Finding table
    frame = driver.find_element(By.ID, "VisibleReportContentReportViewer1_ctl10")
      
    # Finding table  
    table = frame.find_element(By.XPATH, '/html/body/form/div[3]/div/div/span/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td[3]/table')

    # Finding rows of the table
    rows = table.find_elements(By.TAG_NAME, "tr") 
    
    for row in rows[1:]:
        # Get the columns         
        col1 = row.find_elements(By.TAG_NAME, "td")[1] 
        col2 = row.find_elements(By.TAG_NAME, "td")[2]
        city = col1.text + " - " + col2.text #prints text from the element
        
        # Row
        row = pd.DataFrame([i, city]).T
        row.columns = ["Company", "City"]

        # appending
        df_results = pd.concat([df_results, row],'rows')

driver.quit()



# Saving file
df_results.to_excel('Outputs/Companies and Municipalities.xlsx', index = False)