#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 18:33:29 2018

@author: hertta
"""

import geopandas as gpd
import pandas as pd
import math
import statistics as st
import random
from classes import Block
from classes import SchoolDistr

rttk = gpd.read_file("/home/hertta/Documents/Gradu/oppilasalueet2018/wrangled_rttk.shp", encoding = "UTF-8")
schools = gpd.read_file("/home/hertta/Documents/Gradu/oppilasalueet2018/koulut_euref_ykr.shp", encoding = "UTF-8")

# for testing purposes, create a new column in rttk including "pupils": 0.2 * ki_vakiy. In next versions this must be done when generating the data (rttk_wrangling)
rttk['pupils'] = rttk['ki_vakiy']*0.15
for key, row in rttk.iterrows():
    if row['pupils'] < 0:
        rttk.loc[key,'pupils'] = 0





# group rttk
rttk = rttk.set_index(keys = 'YKR_ID', drop = False)
rttk_grouped = rttk.groupby(by = 'ID')


######### build blocks, districts and separate dict of blocks

districts = {}
blocks_dict = {}

for key, row in schools.iterrows():
    
    ##### fetch the correct travel time matrix based on school ykrID
    ykrid = row['YKR_ID']
    
    # build correct filepath and read the file
    fourFirst = str(ykrid)[0:4] 
    fp = "/home/hertta/Documents/Gradu/ttmatrices/HelsinkiTravelTimeMatrix2018/" + fourFirst + "xxx/" +"travel_times_to_ " + str(ykrid) + ".txt"
    matrix = pd.read_csv(fp, sep = ";")
    
    # set the starting location as index
    matrix_ind = matrix.set_index("from_id", drop = False)
    
    # replace -1 values with infinity
    matrix_ind = matrix_ind.replace(to_replace= -1, value = math.inf)
    
    # drop unnecessary columns
    matrix_ind = matrix_ind.filter(items = ['from_id', 'to_id', 'walk_d'])
    
    #convert matrix to dict
    ttdict = matrix_ind.to_dict(orient = 'index')
    
    # get the attribute schoolID
    row_schoolID = row['id']
    
    # fetch the right block-group, create blocks iteratively and add them to both "blocks" and global variable blocks_dict
    blocksframe = rttk_grouped.get_group(row_schoolID)
    blocks = {}
    for key, row in blocksframe.iterrows():
        block = Block(geometry = row['geometry'], ykrId = row['YKR_ID'] , zvalue = row['z-value'], studentBase = row['pupils'], schoolID = row_schoolID)
        blocks[row['YKR_ID']] = block
        blocks_dict[row['YKR_ID']] = block
    
    # now create district and add it to dict "districts"
    distr = SchoolDistr(row_schoolID, blocks, ttdict)
    distr.calculate_geometry()
    distr.calculate_maxttime()
    distr.calculate_studentbase()
    distr.calculate_zvalue(block = None)
    distr.calculate_studentlimit()
    districts[row_schoolID] = distr
    
################# Data is ready    



# luodaan lista Zfactor, joka seuraa sdDictin z-arvojen muutosta. Alustetaan se districtsin z-arvojen itseisarvojen summalla.
Zfactor = []

# luodaan kierroksia laskeva muuttuja. Sitä käytetään mm. määrittämään, milloin Zfactorin kehitystä aletaan tarkkailla ja suoritus voidaan pysäyttää.
iteration = 0

# alustetaan todennäköisyyshomman kattoarvo
ceil = 120

# Iteroidan sdDictiä kunnes iteration on vähintään raja-arvo ja Zfactor ei enää muutu juurikaan pienemmäksi, jolloin palautetaan viimeinen tilanne ja break
while True:
    
    
    # calculate and append Zfactor, with sums of district's z-values' absolute values 
    Z = 0
    
    for key, value in districts.items():
        Z += abs(value.zvalue)
    
    Zfactor.append(Z)
    
    
    # test for breaking
    if iteration >= 30: # huom, testaaminen voi alkaa vasta kun todennäköisyys valita random on ollut 0 jo useita kierroksia
         
        checkvalue = st.mean(list(Zfactor[iteration], Zfactor[iteration-1], Zfactor[iteration-2], Zfactor[iteration-3])) - Zfactor[iteration]
        
        if round(checkvalue, 4) == 0:
            
            # muodostetaan palautettavat jutut
            #palautetaan
            break
                       
    #increase iteration
    iteration += 1
    
   
    
    
    #Iteroidaan kaikki districtit
    for distr in districts:
        
        # arvo todennäköisyysluku, jos ceil on suurempi kuin 0
        if ceil > 0:
            
            randomint = random.randint(0, ceil)
            
        # check what distr touches
        
        # select best or random block based on randomint
        
        # add block to distr
        
        # remove block from districts[block.SchoolID]
        
        # calculate geometries for both disttricts
        
        # calculate zvalues for both districts
        
        # calculate studentbase for both districts
        
        
    
    # joka iteraatiokierroksen lopussa ceiliä vähennetään 
    ceil -= 10






#Idealista
#
#Mainissa:
#
#joka iteraation alussa tallennetaan kouluAlueiden z-arvojen summa listaan. kun tallennettava arvo on 
#sama tai isompi kuin edellinen tallennettu arvo, iteraatiot lopetetaan.
#
#
#todennäköisyyden käyttäminen randomin/parhaan valinnassa:
#-muttuja a:n alkuarvoksi esim. 70
#- arvotaan random arvo väliltä 0, 70
#- jos arvo on yli 50, tehdään random valinta, jos alle 50 valitaan paras ruutu
#- joka iteraatiolla vähennetään luvusta 70 luku 1
#
#
#TODO:
#- schoolDistrille funktio randomin ruudun valitsemiseksi
#- contiguityn rikkoutumisen estäminen: täytyy olla oma metodi, joka täytyy aina suorittaa select best block -metodissa hylkäysperiaatteen tarkistamisena.
#












   