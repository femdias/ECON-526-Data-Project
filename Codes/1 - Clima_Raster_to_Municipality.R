

#################################################################
############ Code for merging raster and shapefiles #############
#################################################################


# install.packages('exactextractr')
# Package guide: https://github.com/isciences/exactextractr
# CRAN with summary of spatial libraries: https://cran.r-project.org/web/views/Spatial.html

# install.packages("exactextractr")

library(raster)
library(sf)
library(exactextractr)
library(stringr)
library(readxl)
library(dplyr)
library(writexl)
library(tidyverse)

### Setting directory...
setwd("C:\\Users\\Users\\Documents\\UBC\\ECON 526\\Data Project")

# Measuring time
start <- Sys.time()



########## Reading and formatting shapefile

# Reading Municipalities shapefile 
shape_Munic <- sf::st_read("Inputs\\Shapefile Munic\\BR_Municipios_2022.shp")

# This shapefile is in CRS SIRGAS 2000, so we convert it to WGS 84
shape_Munic <- st_transform(shape_Munic, crs = 4326)


# Selecting and Renaming
shape_Munic <- shape_Munic[,c("CD_MUN", "geometry")]
names(shape_Munic) <- c("Code_Munic", "geometry")





########## Adding Clima data from Xavier, A. C., Scanlon, B. R., King, C. W., & Alves, A. I. (2022)

#Source: https://sites.google.com/site/alexandrecandidoxavierufes/brazilian-daily-weather-gridded-data


###### Precipitation

# Reading raster of precipitation ("+proj=longlat +datum=WGS84 +no_defs")
#NC_rain_1961 <- raster::stack("Inputs\\Clima Data\\pr_19610101_19801231_BR-DWGD_UFES_UTEXAS_v_3.2.1.nc")
NC_rain_1981 <- raster::stack("Inputs\\Clima Data\\pr_19810101_20001231_BR-DWGD_UFES_UTEXAS_v_3.2.1.nc")
NC_rain_2001 <- raster::stack("Inputs\\Clima Data\\pr_20010101_20200731_BR-DWGD_UFES_UTEXAS_v_3.2.1.nc")

#Crossing raster with shapefile, calculating values for each polygon
#df_rain_1961 <- exact_extract(NC_rain_1961, shape_Munic, 'mean')
df_rain_1981 <- exact_extract(NC_rain_1981, shape_Munic, 'mean')
df_rain_2001 <- exact_extract(NC_rain_2001, shape_Munic, 'mean')

# Trasnforming to DataFrames, adding columns with Municipalities codes and binding all together
#DF_rain_1961 = as.data.frame(df_rain_1961, xy=TRUE)
DF_rain_1981 = as.data.frame(df_rain_1981, xy=TRUE)
DF_rain_2001 = as.data.frame(df_rain_2001, xy=TRUE)

Munic = as.data.frame(shape_Munic$Code_Munic)
names(Munic) <- c("Code_Munic")

DF_rain_final <- cbind(Munic, DF_rain_1981, DF_rain_2001) #DF_rain_1961,

# Fixing names
names(DF_rain_final) = append(append(names(Munic), #gsub("[.]", "-",  gsub("X", "", names(NC_rain_1961)))), 
                         gsub("[.]", "-", gsub("X", "", names(NC_rain_1981)))), 
                         gsub("[.]", "-", gsub("X", "", names(NC_rain_2001))))

# Pivoting df
DF_rain_final_pivot <- pivot_longer(DF_rain_final, cols = names(DF_rain_final)[2:length(DF_rain_final)],
                                    names_to = "Date", values_to = "Precipitation")
                                                                   
# Exporting
write.csv(DF_rain_final_pivot, "Outputs\\Precipitation_Munic.csv", row.names=FALSE)



# Ending timer
end <- Sys.time()
end - start # Takes about 2:40
