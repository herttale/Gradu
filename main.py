#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 18:33:29 2018

@author: hertta
"""
import numpy as np
import geopandas as gpd
import pandas as pd
import math
import statistics as st
import random
from classes import Block
from classes import SchoolDistr

rttk = gpd.read_file("/home/hertta/Documents/Gradu/oppilasalueet2018/wrangled_rttk.shp", encoding = "UTF-8")
schools = gpd.read_file("/home/hertta/Documents/Gradu/oppilasalueet2018/koulut_euref_ykr.shp", encoding = "UTF-8")





rttk_filtered = rttk.loc[rttk['ki_muu'] > -1, :]
globalZ = sum(rttk_filtered['ki_muu'])/sum(rttk_filtered['ki_vakiy'])
rttk.loc[rttk['ki_muu'] == -1, 'ki_muu'] = 0
rttk.loc[rttk['ki_fi'] == -1, 'ki_fi'] = 0
rttk.loc[rttk['ki_sv'] == -1, 'ki_sv'] = 0
#rttk.loc[rttk['ki_vakiy'] == -1, 'ki_vakiy'] = 0

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
        block = Block(geometry = row['geometry'], ykrId = row['YKR_ID'], studentBase = row['pupils'], langFiSve = row['ki_fi'] + row['ki_sv'], langOther = row['ki_muu'], schoolID = row_schoolID)
        blocks[row['YKR_ID']] = block
        blocks_dict[row['YKR_ID']] = block
    
    # now create district and add it to dict "districts"
    distr = SchoolDistr(row_schoolID, blocks, ttdict)
    distr.calculate_geometry()
    distr.calculate_maxttime()
    distr.calculate_studentbase()
    distr.calculate_zvalue()
    distr.calculate_studentlimit()
    districts[row_schoolID] = distr
    

    
################# Data is ready  
# Ylemmässä loopissa: lähdetään uudelleen alkuperäisistä blockseista ja blockdictistä liikkeelle, eli edellisen iteraation tulosdicti ja Z täytyy tallentaa
# ennen kuin ne ylikirjoitetaan uudella datanlukemisella. Iteraation tulosdicti kirjoitetaan edellisen päälle vain, jos se on edellistä parempi (lähempänä 
# globaalia optimia). Seurataan Z-arvojen muutosta myös kirjaamalla ne aina listaan iteraation lopussa. Looppi pidetään käynnissä kiinteän määrän kertoja (esim. 20-100))
#Upper_Zfactor = []
#Upper_iteration = 0
#
#while True:
    
    
    
    

# luodaan lista Zfactor, joka seuraa sdDictin z-arvojen muutosta.
Zfactor = []

# luodaan kierroksia laskeva muuttuja. Sitä käytetään mm. määrittämään, milloin Zfactorin kehitystä aletaan tarkkailla ja suoritus voidaan pysäyttää.
mainiteration = 0
subiteration = 0

# alustetaan todennäköisyyshomman kattoarvo
ceil = 50

# lasketaan globaali muunkielisten osuuden keskiarvo ja keskihajonta alueilla

stdev_list = []

for key, item in districts.items():
    stdev_list.append(item.zvalue)

# keskiarvo
globalMean = sum(stdev_list)/len(districts)

# keskihajonta
globalStDev = np.std(stdev_list, ddof = 0)
 
# Iteroidan sdDictiä kunnes iteration on vähintään raja-arvo ja Zfactor ei enää muutu juurikaan pienemmäksi, jolloin palautetaan viimeinen tilanne ja break
while True:
    
    
    # calculate and append Zfactor, with sums of district's z-values' absolute values 
    Z = 0
    
    for key, value in districts.items():
        Z += abs((value.zvalue-globalMean)/ globalStDev)
    
    Zfactor.append(Z)
    
    
    # test for breaking
    if mainiteration >= 12: # huom, testaaminen voi alkaa vasta kun todennäköisyys valita random on ollut 0 jo muutamia kierroksia
         
        checkvalue = st.mean([Zfactor[mainiteration], Zfactor[mainiteration-1], Zfactor[mainiteration-2], Zfactor[mainiteration-3]]) - Zfactor[mainiteration]
        
        if round(checkvalue, 5) == 0:
            
            # muutetaan break_cond Trueksi
            # myöhemmin tässä palautetaan, kun tehty funktioksi, nyt breakataan ulommassa loopissa (2. while)
            break    

               
    #increase iteration
    mainiteration += 1
    print("mainiteration round:", mainiteration, ', current zvalue:', Z)
    
    
    #Iteroidaan kaikki districtit
    for key in list(districts.keys()):
        
        subiteration += 1
        
        # arvo todennäköisyysluku, jos ceil on suurempi kuin 50, muuten randomint = 0 ja valitaan aina paras
        if ceil >= 50:
            
            randomint = random.randint(0, ceil)
            
        else:
            
            randomint = 0
            
        # check what distr touches
        blist = districts[key].touches_which(blocks_dict)
        
        # select best or random block based on randomint
        if randomint > 50:
            
            block_toadd = districts[key].select_random_block(blist, districts)
            
        else:
            
            block_toadd = districts[key].select_best_block(blist, districts, globalMean, globalStDev)
        
        
        ## FIXME koita tässä muuttaa mainin sisällä block_toadd'in vastaavaan alkuperäiseen blockiin!!! schoolID ja samalla schoolID myös blocks_dictin instansseihin jne! 
        ## tai sitten poista block_toadd muuttujaan julistaminen välistä!!!

        # tässä päivitetään myös blocks_dictiin tieto blockin uudesta disrtictistä, joka dictin ainoa muuttuva tieto


        if block_toadd != None: # tämän myötä tyhjän lisäämistä / poistamista ei tarvitse käsitellä luokkametodissa
           
            # remove block from districts[block.SchoolID]
            districts[block_toadd.schoolID].remove_block(block_toadd)
        
            blocks_dict[block_toadd.ykrId].schoolID = key
            block_toadd.schoolID = key
        
            # add block to original districts -dict
            districts[key].add_block(block_toadd)
        
        
#        l = []
#        for k, item in districts[key].blocks.items(): 
#            l.append(item.schoolID)
#            
#        print(set(l))
#        print('\n')
    
    # joka iteraatiokierroksen lopussa ceiliä vähennetään 
    ceil -= 10




for key, v in districts.items(): print(key, v.zvalue)

import matplotlib.pyplot as plt    

plt.plot(Zfactor)
    
resultframe = gpd.GeoDataFrame(columns= ['key', 'geometry', 'zvalue'], geometry = "geometry")
for key, item in districts.items():
    resultframe = resultframe.append({'key': key, 'geometry' : item.geometry, 'zvalue' : (item.zvalue-globalMean)/ globalStDev}, ignore_index=True)
    print(key, (item.zvalue-globalMean)/ globalStDev)

    
resultframe.plot(column = 'key', linewidth=1.5)
resultframe.plot(column = 'zvalue', linewidth=1.5, cmap = 'plasma')


resultframe = resultframe.set_geometry('geometry')
resultframe.crs = '+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs'

resultframe.to_file("/home/hertta/Documents/Gradu/tuloksia/optimated_districts_rand1.shp") 


origframe = gpd.GeoDataFrame(columns= ['key', 'geometry'], geometry = "geometry")
for key, item in districts.items():
    origframe = origframe.append({'key': key, 'geometry' : item.geometry}, ignore_index=True)
    
origframe.plot(column = 'key', linewidth=1.5)

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

#
# remove toimii
# jostain syystä block.schoolID ei päivity ja siksi blockin lisäämisen jälkeen self.blocksin blockseissa on keskenään eri schoolID:n omaavia blockseja....

# contiguity check ei toimi jostain syystä!





   