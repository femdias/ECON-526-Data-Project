# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 10:09:18 2023

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
os.chdir(r'C:\Users\femdi\Documents\UBC\ECON 526\Data Project')

# Chromedriver installation (when needed)
chrome_options = ChromiumOptions()
#chrome_options.headless = True
#service = Service(ChromeDriverManager().install())

# Opening Chrome
driver = webdriver.Chrome(options=chrome_options)

# Opening Aneel site
driver.get("https://www2.aneel.gov.br/relatoriosrig/(S(ups43g14ydgfufgqvvbv5un3))/relatorio.aspx?folder=sfe&report=DistribuidoradecadaMunicipio")


#### Function to reload the page if a problem happens
def reload_page():
    driver.get("https://www2.aneel.gov.br/relatoriosrig/(S(ups43g14ydgfufgqvvbv5un3))/relatorio.aspx?folder=sfe&report=DistribuidoradecadaMunicipio")
    time.sleep(5)
    
    # Selecting option i
    select = Select(driver.find_element(By.CLASS_NAME,'aspNetDisabled'))
    select.select_by_visible_text(i)
    
    # Wait 15 seconds
    time.sleep(15)
    
    # Selecting option j
    select = Select(driver.find_elements(By.CLASS_NAME, 'aspNetDisabled')[1])
    select.select_by_visible_text(j)



# Options of the drop in menu os States
dropdown = driver.find_element(By.CLASS_NAME, 'aspNetDisabled')
options_states = [x.text for x in dropdown.find_elements(By.TAG_NAME, "option")]

# Loop around each option 
df_results = pd.DataFrame(columns = ["Company", "City", "Treated Unities"])
#df_results = pd.read_excel('Outputs/Comp_Munic_Qty_Houses.xlsx')


for i in tqdm.tqdm(options_states):
    
    # Selecting option i
    select = Select(driver.find_element(By.CLASS_NAME,'aspNetDisabled'))
    select.select_by_visible_text(i)
    
    # Wait 2 seconds
    time.sleep(2)
    
    # Options of the drop in menu of Cities
    dropdown_munic = driver.find_elements(By.CLASS_NAME, 'aspNetDisabled')[1]
    options_munic = [x.text for x in dropdown_munic.find_elements(By.TAG_NAME, "option")]
    
    
    for j in tqdm.tqdm(options_munic):
        
        # big try except with reloading the page
        try:
                
            try:
                # Selecting option j
                select = Select(driver.find_elements(By.CLASS_NAME, 'aspNetDisabled')[1])
                select.select_by_visible_text(j)
            except:
                time.sleep(15)
                # Selecting option j
                select = Select(driver.find_elements(By.CLASS_NAME, 'aspNetDisabled')[1])
                select.select_by_visible_text(j)
                
            # Click on the search buttom
            botton = driver.find_element(By.ID,'ReportViewer1_ctl04_ctl00')
            botton.click()
            
            #Waiting until the website loads complety 
            wait = WebDriverWait(driver,15).until(
                 EC.presence_of_element_located((By.ID, "VisibleReportContentReportViewer1_ctl10")))
                    
            try:
                time.sleep(5)
    
                # Finding table
                frame = driver.find_element(By.ID, "VisibleReportContentReportViewer1_ctl10")
                  
                # Finding table  
                table = frame.find_element(By.XPATH, '/html/body/form/div[3]/div/div/span/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td[3]/table')
            
                # Finding rows of the table
                rows = table.find_elements(By.TAG_NAME, "tr") 
            except:
                # Waiting more 10 seconds
                time.sleep(10)
    
                # Finding table
                frame = driver.find_element(By.ID, "VisibleReportContentReportViewer1_ctl10")
                  
                # Finding table  
                table = frame.find_element(By.XPATH, '/html/body/form/div[3]/div/div/span/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td[3]/table')
            
                # Finding rows of the table
                rows = table.find_elements(By.TAG_NAME, "tr")
                
    
            for row in rows[2:len(rows)-1]:
                # Get the columns         
                col1 = row.find_elements(By.TAG_NAME, "td")[1] 
                col2 = row.find_elements(By.TAG_NAME, "td")[2]
                company = col1.text
                qty_households = col2.text
                city = j + " - " + i #prints text from the element
                
                # Row
                row = pd.DataFrame([company, city, qty_households]).T
                row.columns = ["Company", "City", "Treated Unities"]
        
                # appending
                df_results = pd.concat([df_results, row],'rows')
       
        
       # if some error happen, lets reload the page and try again
        except:
            reload_page()
            try:
                # Selecting option j
                select = Select(driver.find_elements(By.CLASS_NAME, 'aspNetDisabled')[1])
                select.select_by_visible_text(j)
            except:
                time.sleep(15)
                # Selecting option j
                select = Select(driver.find_elements(By.CLASS_NAME, 'aspNetDisabled')[1])
                select.select_by_visible_text(j)
                
            # Click on the search buttom
            botton = driver.find_element(By.ID,'ReportViewer1_ctl04_ctl00')
            botton.click()
            
            #Waiting until the website loads complety 
            wait = WebDriverWait(driver,15).until(
                 EC.presence_of_element_located((By.ID, "VisibleReportContentReportViewer1_ctl10")))
                    
            try:
                time.sleep(5)
    
                # Finding table
                frame = driver.find_element(By.ID, "VisibleReportContentReportViewer1_ctl10")
                  
                # Finding table  
                table = frame.find_element(By.XPATH, '/html/body/form/div[3]/div/div/span/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td[3]/table')
            
                # Finding rows of the table
                rows = table.find_elements(By.TAG_NAME, "tr") 
            except:
                # Waiting more 10 seconds
                time.sleep(10)
    
                # Finding table
                frame = driver.find_element(By.ID, "VisibleReportContentReportViewer1_ctl10")
                  
                # Finding table  
                table = frame.find_element(By.XPATH, '/html/body/form/div[3]/div/div/span/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td[3]/table')
            
                # Finding rows of the table
                rows = table.find_elements(By.TAG_NAME, "tr")
                
    
            for row in rows[1:len(rows)-1]:
                # Get the columns         
                col1 = row.find_elements(By.TAG_NAME, "td")[1] 
                col2 = row.find_elements(By.TAG_NAME, "td")[2]
                company = col1.text
                qty_households = col2.text
                city = j + " - " + i #prints text from the element
                
                # Row
                row = pd.DataFrame([company, city, qty_households]).T
                row.columns = ["Company", "City", "Treated Unities"]
        
                # appending
                df_results = pd.concat([df_results, row], axis = 'rows')

driver.quit()

# Drop duplicates and rows with titles
df_results1 = df_results.drop_duplicates()
df_results1 = df_results1[df_results1['Company'] != 'Distribuidora']


# Saving file
df_results1.to_excel('Outputs/Companies and Munic Qty of Households.xlsx', index = False)
