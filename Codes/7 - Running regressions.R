
# In this code, we use the complete dataset that was created with the Python
# scripts to estimate the impact of energy prices on GDP, using rain as an IV

# libraries
library(tidyverse)
library(readxl)
library(plm)
library(texreg)
library(stargazer)
library(writexl)
library(data.table)
library(modelsummary)
library(stringr)
library(fixest)
library(foreign)

# Defining work directory  
setwd('C:\\Users\\femdi\\Documents\\UBC\\ECON 526\\Data Project')
      
# Importing data with rain, companies, prices of eletricity and GDP
df <- read_excel('Outputs\\Complete_dataset.xlsx')  

# Convert to panel
df <- pdata.frame(df, index = c("Code", "Year"))

# Check if panel is balanced
is.pbalanced(df) # it is
#length(unique(df$Year))
#length(unique(df$Code))

# Creating lag variable of rain and rain squared
df <- cbind(df, setNames(data.frame(lag(df$Precipitation_per_km2, k = c(1), shift = 'time')),c('Precipitation_per_km2_lag')))
df <- df %>% mutate(Precipitation_per_km2_sqrt = sqrt(Precipitation_per_km2),
                    Precipitation_per_km2_sqrt_lag = sqrt(Precipitation_per_km2_lag))
                    
# Creating variable of GDP of industry and agriculture per capita
df <- df %>% mutate(GDP_Industry_pc = Share_Industry * GDP_pc,
                    GDP_Agriculture_pc = Share_Agriculture * GDP_pc)

# Creating log variables (first sum 1 to the number and then take the log)
df <- df %>% mutate(ln_Precipitation_per_km2 = log(1 + Precipitation_per_km2),
                    ln_Precipitation_per_km2_lag = log(1 + Precipitation_per_km2_lag), 
                    ln_GDP_Industry_pc = log(1 + GDP_Industry_pc),
                    ln_GDP_Agriculture_pc = log(1 + GDP_Agriculture_pc),
                    ln_Electricity_Price = log(1 + Electricity_Price))


# Removing 2020 from the analysis
df <- df %>% filter(!Year %in% c(2020))


# Descriptive Statistcs
x <- data.frame(df)
stargazer(x, type = 'text')
stargazer(x, type = 'latex')

# Exporting as Stata file for running regressions on Stata
write.dta(df, "Outputs\\Complete_dataset_Stata.dta")




# Plot some data
ggplot(df, aes(x=Precipitation_per_km2)) + geom_histogram(binwidth=1) + xlim(c(0, 100))
hist(df$Electricity_Price)
ggplot(df, aes(x=GDP_Industry_pc)) + geom_histogram(binwidth=100) + xlim(c(0, 10000))

hist(df$ln_Precipitation_per_km2)
hist(df$ln_Electricity_Price)
ggplot(df, aes(x=ln_GDP_Industry_pc)) + geom_histogram(binwidth=1) + xlim(c(0, 25))



#################### RUNNING REGRESSIONS ####################

#### Model 1: OLS

Model_OLS <- fixest::feols(ln_GDP_Industry_pc ~ ln_Electricity_Price,
                           data = df, 
                           cluster = c("City"))

# Regression table
etable(Model_OLS, digits = 4)

#### Model 2: OLS with FE (year and cities)

Model_FE <- fixest::feols(ln_GDP_Industry_pc ~ ln_Electricity_Price | # Dependent variable ~ controls
                           City + Year, # Fixed Effects
                           data = df, 
                           cluster = c("City"))

# Regression table
etable(Model_FE, digits = 4)




####################### Instrumental variables

# Testing instruments
IV_precip <- fixest::feols(ln_GDP_Industry_pc ~ 1 | # Dependent variable ~ controls
                           City + Year | #FE
                          ln_Electricity_Price ~ Precipitation_per_km2, # Endogenous variables ~ instruments
                           data = df,
                           cluster = c("City"))

fixest::fitstat(IV_precip, ~ ivf1 + ivwald1)

IV_precip_ln <- fixest::feols(ln_GDP_Industry_pc ~ 1 | # Dependent variable ~ controls
                             City + Year | #FE
                               ln_Electricity_Price ~ ln_Precipitation_per_km2, # Endogenous variables ~ instruments
                           data = df,
                           cluster = c("City"))

fixest::fitstat(IV_precip_ln, ~ ivf1 + ivwald1)


IV_precip_sqrt <- fixest::feols(ln_GDP_Industry_pc ~ 1 | # Dependent variable ~ controls
                             City + Year | #FE
                               ln_Electricity_Price ~ Precipitation_per_km2_sqrt, # Endogenous variables ~ instruments
                           data = df,
                           cluster = c("City"))

fixest::fitstat(IV_precip_sqrt, ~ ivf1 + ivwald1)



IV_precip_and_sqrt <- fixest::feols(ln_GDP_Industry_pc ~ 1 | # Dependent variable ~ controls
                             City + Year | #FE
                             ln_Electricity_Price ~ Precipitation_per_km2 + Precipitation_per_km2_sqrt, # Endogenous variables ~ instruments
                           data = df,
                           cluster = c("City"))

etable(summary(IV_precip_and_sqrt, stage = 1))
fixest::fitstat(IV_precip_and_sqrt, ~ ivf1 + ivwald1 + sargan)

### All together
etable(summary(IV_precip, stage = 1), summary(IV_precip_sqrt, stage = 1), 
       summary(IV_precip_ln, stage = 1), summary(IV_precip_and_sqrt, stage = 1),
       fitstat = ~ n + r2 + ivf1 + ivwald1 + sargan + my)





# "Best" specification  ---> Higher Wald test

#### Model 3: IV

Model_Final <- fixest::feols(ln_GDP_Industry_pc ~ 1 | # Dependent variable ~ controls
                            City + Year| #FE
                              ln_Electricity_Price ~ ln_Precipitation_per_km2, # Endogenous variables ~ instruments
                          data = df,
                          cluster = c("City"))

# Regression table
etable(Model_Final, digits = 4)

# Two stages reg table
etable(summary(Model_Final, stage = 1:2), fitstat = ~ . + ivfall + ivwaldall + sargan)

# Tests for Weak instruments
fixest::fitstat(Model_Final, ~ ivf1 + ivwald1 + sargan)



########## Creating Summary Tables in LaTeX


# Table 1: IV 1st stage (ln_precipitation and Precipitation + Precipitation_sqrt)
title1 = "Impact of precipitation on the price of electricity, 2010 to 2019"
notes1 = paste0("Notes: All regressions use a panel of 5566 counties per ",
                "month from 2010 to 2019. ",
                "Precipitation per km2 refers to total monthly rainfall in millimeters divided by the county area. ",
                "All regressions include year and county fixed effects. ",
                "Column 1, 2, 3 and 4 denotes the results of the regression ",
                "of the log of electricity price on precipitation, ",
                "precipitation squared, the 1 + natural log of precipitation,  ",
                "and precipitation and precipitation squared, respectively. ",
                "Standard errors are clustered by County. ",
                "P-Values: ***: 0.01, **: 0.05, *: 0.1")

etable(summary(IV_precip, stage = 1), summary(IV_precip_sqrt, stage = 1), 
       summary(IV_precip_ln, stage = 1), summary(IV_precip_and_sqrt, stage = 1),       # Models
       fitstat = ~ n + r2 + ivf1 + ivwald1 + sargan + my,                              # Stats on the bottom
       digits = "r5", digits.stats = "r4",                                      # Number of digits in output
       keep = c('Precipitation', '%ln_Precipitation', '%Precipitation_sqrt'),                                           # Which Variables to Display
       #group=list("-Other covariates"=c("Max_Temperature", "Min_Temperature")), # Add line that identify if there are those covariates in the model
       dict = c('Precipitation_sqrt' = 'Precipitation$^2$', 
                'ln_Precipitation' = 'ln(Precipitation)',
                'ln_Electricity_Price' = 'ln(Electricity Price)'),                      # Changing the name of variables
       #depvar = FALSE,                                                          # Don't show Dependent variable
       title = title1,                                                          # Add title
       notes = notes1,                                                          # Add notes
       tpt = TRUE,                                                              # Using LaTeX's threeparttable environment 
       se.row = TRUE,                                                           # Add S.E. row
       tex = TRUE,                                                              # Exporting to LaTeX
       style.tex = style.tex(main = "base",
                             model.title = "",                                  # Remove "Model"
                             var.title = "",                                    # Remove "Variables"
                             fixef.title = "\\midrule \\emph{Controls}",        # Rename FE title                                    # Remove "Variables"
                             yesNo = c("X", ""),                                # Changing the Yes or No representations
                             notes.tpt.intro = "\\footnotesize",                # Changing size of footnote
                             tablefoot = FALSE))                                # Remove 'Significante level explanation' from notes




# Table 2: IV 2nd stage  
title1 = "Impact of the price of electricity on Manufacturing GDP per capita, 2010 to 2019"
notes1 = paste0("Notes: All regressions use a panel of 5566 counties per ",
                "month from 2010 to 2019. ",
                "Precipitation per km2 refers to total monthly rainfall in millimeters divided by the county area. ",
                "All regressions include year and county fixed effects. ",
                "Column 1 denotes the OLS results of the regression ",
                "of the crime rate on the natural log of precipitation. ",
                "Column 2 reports the results of the regression of the crime rate ",
                "on precipitation and precipitation squared. ",
                "Standard errors are Conley standard errors for spatial correlation ",
                "and all regressions are weighted by the weighting area's adult population. ",
                "P-Values: ***: 0.01, **: 0.05, *: 0.1")

etable(summary(Model_OLS), summary(Model_FE), summary(Model_Final, stage = 2),          # Models
       headers = c("OLS", "FE", "IV"),
       fitstat = ~ n + r2 + ivwald1 + sargan + my,                              # Stats on the bottom
       digits = "r5", digits.stats = "r4",                                      # Number of digits in output
       #keep = c('ln_Precipitation', 'Precipitation', '%Precipitation_sqrt'),   # Which Variables to Display
       #group=list("-Other covariates"=c("Max_Temperature", "Min_Temperature")), # Add line that identify if there are those covariates in the model
       dict = c('Precipitation_sqrt' = 'Precipitation$^2$', 
                'Weighting_Area' = 'Weighting area',
                'ln_Precipitation' = 'ln(Precipitation)',
                'ln_Electricity_Price' = 'ln(Electricity Price)',
                'ln_GDP_Industry_pc' = 'ln(Manufacturing GDP per capita)'),                      # Changing the name of variables
       #depvar = FALSE,                                                          # Don't show Dependent variable
       title = title1,                                                          # Add title
       notes = notes1,                                                          # Add notes
       tpt = TRUE,                                                              # Using LaTeX's threeparttable environment 
       se.row = TRUE,                                                           # Add S.E. row
       tex = TRUE,                                                              # Exporting to LaTeX
       style.tex = style.tex(main = "base",
                             model.title = "",                                  # Remove "Model"
                             var.title = "",                                    # Remove "Variables"
                             fixef.title = "\\midrule \\emph{Controls}",        # Rename FE title                                    # Remove "Variables"
                             yesNo = c("X", ""),                                # Changing the Yes or No representations
                             notes.tpt.intro = "\\footnotesize",                # Changing size of footnote
                             tablefoot = FALSE))                                # Remove 'Significante level explanation' from notes










