#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 14:02:58 2018

@author: hertsy

Haetaan ykr id:t kouluille, ladataan vastaavat matka-aikamatriisit
koordinaattijärjestelmä: etrs-tm35fin
"""
import geopandas as gpd
import pandas as pd

koulut_geocoded = gpd.read_file("/home/hertsy/Documents/Gradu/oppilasalueet2018/koulut_osoitteet_nom2.shp", encoding = "UTF-8")
koulut_euref = koulut_geocoded.to_crs('+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs')

koulut_euref.plot()

ykrgrid = gpd.read_file("/home/hertsy/Documents/Gradu/ttmatrices/MetropAccess_YKR_grid/MetropAccess_YKR_grid_EurefFIN.shp")
ykrgrid = ykrgrid.to_crs('+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs')

## plotataan päällekkäin

ax = ykrgrid.plot(linewidth=0.5, color =  'green');

koulut_euref.plot(ax=ax, color='red', alpha=0.5);

## joinataan kouluihin ykr tieto spatial joinilla

koulut_euref_ykr = gpd.sjoin(koulut_euref, ykrgrid, how = 'left', op = "within")

#luetaan testiksi yksi matriisi
testim = pd.read_csv("/home/hertsy/Documents/Gradu/ttmatrices/HelsinkiTravelTimeMatrix2018/5900xxx/travel_times_to_ 5900227.txt", sep = ";")




# luetaan yksi kerrallaan tt matrixit data framen sarakkeeseen dicteinä
koulut_euref_ykr["ttmatrix"] = None

for index, row in koulut_euref_ykr.iterrows():
    ykrid = row['YKR_ID']
    fourFirst = str(ykrid)[0:4]
    
    fp = "/home/hertsy/Documents/Gradu/ttmatrices/HelsinkiTravelTimeMatrix2018/" + fourFirst + "xxx/" +"travel_times_to_ " + str(ykrid) + ".txt"
    matrix = pd.read_csv(fp, sep = ";")
    matrix_ind = matrix.set_index("from_id")
    
    # tässä pitää käsitellä -1 arvot ja poistaa turhat sarakkeet myöhemmissä versioissa
    # lisäksi pitää miettiä, mikä dictirakenne on kätevin: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_dict.html
    
    ttdict = matrix_ind.to_dict(orient = 'index')
    koulut_euref_ykr.loc[index,"ttmatrix"] = [ttdict]

