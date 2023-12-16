clear all

* Defining matsize
set matsize 1000
set maxvar 32767

* Importing dataset
use "C:\Users\femdi\Documents\UBC\ECON 526\Data Project\Outputs\Complete_dataset_Stata.dta", clear 

* Defining working directory 
cd "C:\Users\femdi\Documents\UBC\ECON 526\Data Project"


***** IV regressions 

*** IV = Ln_Precipitation_per_km2
ivreghdfe ln_GDP_Industry_pc (ln_Electricity_Price = ln_Precipitation_per_km2) , absorb(Code Year) cluster(Code)

weakivtest  
*Effective F statistic: 88.989



*** IV = Precipitation_per_km2  + Precipitation_per_km2_sqrt
ivreghdfe ln_GDP_Industry_pc (ln_Electricity_Price = Precipitation_per_km2 Precipitation_per_km2_sqrt), absorb(Code Year) cluster(Code)

weakivtest  
*Effective F statistic:  




*** IV = Precipitation_per_km2 
ivreghdfe ln_GDP_Industry_pc (ln_Electricity_Price = Precipitation_per_km2), absorb(Code Year) cluster(Code)

weakivtest  
*Effective F statistic:  




*** IV = ln_Precipitation_per_km2_lag
ivreghdfe ln_GDP_Industry_pc (ln_Electricity_Price = ln_Precipitation_per_km2_lag), absorb(Code Year) cluster(Code Year)

weakivtest  
*Effective F statistic:  







