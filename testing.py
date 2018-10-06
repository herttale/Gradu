#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 20:10:31 2018

@author: hertta
"""

##################### testataan block -ja schooldistr -luokat

import geopandas as gpd
import pandas as pd



rttk = gpd.read_file("/home/hertta/Documents/Gradu/oppilasalueet2018/wrangled_rttk.shp", encoding = "UTF-8")
schools = gpd.read_file("/home/hertta/Documents/Gradu/oppilasalueet2018/koulut_euref_ykr.shp", encoding = "UTF-8")

# for testing purposes, create a new column in rttk including "pupils": 0.2 * ki_vakiy
rttk['pupils'] = rttk['ki_vakiy']*0.15
for key, row in rttk.iterrows():
    if row['pupils'] < 0:
        rttk.loc[key,'pupils'] = 0


testb_attr = rttk.iloc[0,:]
testblock = Block(geometry = testb_attr['geometry'], ykrId = testb_attr['YKR_ID'] , zvalue = testb_attr['z-value'], studentBase = testb_attr['pupils'])


# lisätään ttmatrixit school-tauluun
schools["ttmatrix"] = None

for index, row in schools.iterrows():
    ykrid = row['YKR_ID']
    fourFirst = str(ykrid)[0:4]
    
    fp = "/home/hertta/Documents/Gradu/ttmatrices/HelsinkiTravelTimeMatrix2018/" + fourFirst + "xxx/" +"travel_times_to_ " + str(ykrid) + ".txt"
    matrix = pd.read_csv(fp, sep = ";")
    matrix_ind = matrix.set_index("from_id")
    
    # tässä pitää käsitellä -1 arvot ja poistaa turhat sarakkeet myöhemmissä versioissa
    # lisäksi pitää miettiä, mikä dictirakenne on kätevin: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_dict.html
    
    ttdict = matrix_ind.to_dict(orient = 'index')
    schools.loc[index,"ttmatrix"] = [ttdict]

# groupataan rttk
rttk = rttk.set_index(keys = 'YKR_ID', drop = False)
rttk_grouped = rttk.groupby(by = 'ID')


# build testdistr
for key, row in schools.iterrows():
    schoolID = row['id']
    
    ttmatrix = row['ttmatrix']
    blocksframe = rttk_grouped.get_group(schoolID)
    blocks = {}
    for key, row in blocksframe.iterrows():
        block = Block(geometry = row['geometry'], ykrId = row['YKR_ID'] , zvalue = row['z-value'], studentBase = row['pupils'])
        blocks[row['YKR_ID']] = block
    
    testdistr = SchoolDistr(schoolID, blocks, ttmatrix)
    break






