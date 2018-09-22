#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 11:25:28 2018

@author: hertsy

Preparing the rttk grid data
coordinate reference system: etrs-tm35fin

"""

import geopandas as gpd
import numpy as np


##### Funktiot #####

# fishnetin luomisfunktio
# total_bounds = xmin, ymin, xmax, ymax arrayna
# height = ruudun särmän pituus, ruudut aina tässä neliöitä

def createFishnet(total_bounds, crs, height):
    
    from shapely.geometry import Polygon
    
    rows = int(np.ceil((total_bounds[3]-total_bounds[1]) / height))
    cols = int(np.ceil((total_bounds[2]-total_bounds[0]) / height))
    
    XleftOrigin = total_bounds[0]
    XrightOrigin = total_bounds[0] + height
    YtopOrigin = total_bounds[3]
    YbottomOrigin = total_bounds[3] - height
    polygons = []
    for i in range(cols):
        Ytop = YtopOrigin
        Ybottom = YbottomOrigin
        for j in range(rows):
            polygons.append(Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop), (XrightOrigin, Ybottom), (XleftOrigin, Ybottom)])) 
            Ytop = Ytop - height
            Ybottom = Ybottom - height
        XleftOrigin = XleftOrigin + height
        XrightOrigin = XrightOrigin + height
    
    grid = gpd.GeoDataFrame({'geometry':polygons})
    grid.crs = crs
    return grid


    

# 1. ladataan aineistot: rttk poiminta ja oppilasalueet, muutetaan ne euref-fin koordinaatistoon

ruudut = gpd.read_file("/home/hertsy/Documents/Kandi/Kandiaineisto/13rttk060_rttk2012/rttk2012_250m.shp")
ruudut.crs
ruudut = ruudut.to_crs('+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs')



alueet = gpd.read_file("/home/hertsy/Documents/Kandi/Kandiaineisto/oppilasalueiden rajat/2015/opevooa_2015_16_ala_aste_suomi.tab", encoding = 'UTF-8')
alueet.crs
alueet = alueet.to_crs('+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs')
alueet.plot(facecolor='gray')


# tehdään ruuduista helsingin kokoinen poiminta
ruudut_hki = ruudut.loc[ruudut['KUNTA'] == "091"]
ruudut_hki.plot(facecolor='gray')

# dropataan turhat columnit
ruudut_hki = ruudut_hki.filter(items = ['KUNTA', 'euref_x', 'euref_y', 'ki_vakiy', 'ki_fi', 'ki_sv', 'ki_muu', 'geometry'])

# plotataan alueet ja ruudut päällekkäin testiksi
 
ax = alueet.plot(linewidth=0.5, color =  'green');
ruudut_hki.plot(ax=ax, color='red', alpha=0.5);

### Luodaan rttk:n kanssa yksiin menevä fishnet, poimitaan siitä oppilasalueiden ulkorajojen kokoinen otos, luodaan  
## rttt:kta vastaavat sarakkeet ja annetaan kaikkiin arvoiksi 0. Tämän jälkeen liitetään spatiaalisesti rttk:n ruututieto fishnettiin.

# A. luodaan fishnet


fishnet = createFishnet(total_bounds = ruudut_hki.total_bounds, crs = ruudut_hki.crs, height = 250)

ax = fishnet.plot(linewidth=0.5, color =  'blue');
ruudut_hki.plot(ax=ax, color='red', alpha=0.5);
alueet.plot(ax=ax,linewidth=0.5, color =  'green');
# poimitaan fishnetistä helsingin muotoinen alue oppilasaluepolygonien perusteella TEE TÄSTÄ FUNKTIO

data = []

for index2, ruutu in fishnet.iterrows():    
    for index, alue in alueet.iterrows():
       if ruutu['geometry'].intersects(alue['geometry']):
          data.append({'geometry': ruutu['geometry']})
          break
      
fishnet_hki = gpd.GeoDataFrame(data,columns=['geometry'])
fishnet_hki.crs = alueet.crs


# lasketaan ruuduille centroidit pisteinä

ruudut_hki['centroid'] = ruudut_hki.centroid


# set geometry to centroid column
ruudut_hki = ruudut_hki.set_geometry('centroid')

## joinataan rttk:n tiedot uuteen hki fishnetiin

fn_ruudut_joined = gpd.sjoin(fishnet_hki, ruudut_hki, how = 'left', op = 'contains')

# dropataan index_right -columni jotta voidaan tehdä seuraava liitos
fn_ruudut_joined = fn_ruudut_joined.drop(['index_right', 'geometry_right'], axis = 1)
fn_ruudut_joined = gpd.GeoDataFrame(fn_ruudut_joined, geometry = 'geometry_left', crs = ruudut_hki.crs)

fn_ruudut_joined['centroid'] = fn_ruudut_joined.centroid

# set geometry to centroid column
fn_ruudut_joined = fn_ruudut_joined.set_geometry('centroid')



# 3. joinataan rttk-ruutuihin tieto, mihin oppilasalueeseen kuuluvat (alueID)

ruudut_joined = gpd.sjoin(fn_ruudut_joined, alueet, how = 'left', op = "within")

# check and plot the nan rows
ruudut_nan = ruudut_joined.loc[np.isnan(ruudut_joined['PINTA'])]
ruudut_nan.plot()

# drop the nan rows
ruudut_joined = ruudut_joined.loc[~np.isnan(ruudut_joined['PINTA'])]

# tarkastetaan plottaamalla että kaikki ok
ruudut_joined.plot()

# asetetaan geometria takaisin ruuduiksi
ruudut_joined = ruudut_joined.set_geometry('geometry_left')

# pudotetaan centroidicolumni
ruudut_joined = ruudut_joined.drop(['centroid', 'KUNTA_left','ALUEJAKO', 'KUNTA_right', 'NIMI_SE', 'ALKUPERAKOODI', 'LUONTI_PVM', 'DATA_MUOKKAAJA', 'MUOKKAUS_PVM', 'OMISTAJA', 'HISTORIA_PVM', 'PINTA', 'MITTAUSERA', 'TARKKUUS', 'DATA_LUOJA'], axis = 1)


# korvataan nan -arvot -999:llä
ruudut_joined = ruudut_joined.fillna(-1)




################### THIS SECTION IS ONLY FOR SAVING THE DATA #########################
# change data types from bytes and numpy floats and ints to python basic objects

# print the current data types for cols
for col in ruudut_joined:
    print(type(ruudut_joined.loc[2, col]))

# change the types for cols
ruudut_joined1 = ruudut_joined.astype('object')

# check the types for row 5
for col in ruudut_joined1:
    print(type(ruudut_joined1.loc[5, col]))

### muuta string-columnit byteistä str-muotoon tallentamista varten
for col in ruudut_joined1:
    if (type(ruudut_joined1.loc[5, col]) == str):
        ruudut_joined1[col] = ruudut_joined1[col].astype(str)
    
# tallennetaan varmuuskopio shapefilena
ruudut_joined1.to_file("/home/hertsy/Documents/Gradu/oppilasalueet2018/ruudut_kieli_final.shp")

#############################################################################################



# 5. lasketaan kaikille ruuduille oma pos.diskriminaation indeksinsä. Jaetaan se kaikkien ruutujen keskihajonnalla jotta saadaan z-arvo.


# muutetaan salatut ruudut luvuksi, joka vastaa keskimääräistä indeksiarvoa (ruutujen arvojen keskiarvo)


ruudut_joined["ki_muu_osuus"] = -1.0

# lasketaan uusi sarake muunkielisten osuudesta kyseisessä ruudussa
for index, row in ruudut_joined.iterrows():
    if row["ki_muu"] > -1:
        ruudut_joined.at[index,"ki_muu_osuus"] = row["ki_muu"]/row["ki_vakiy"]
        

muunki_mean = ruudut_joined.loc[ruudut_joined["ki_muu_osuus"] > -1,"ki_muu_osuus"].mean()


for index, row in ruudut_joined.iterrows():
    if row["ki_muu"] == -1:
        ruudut_joined.at[index,"ki_muu_osuus"] = muunki_mean

# lasketaan muunkielisten osuuden keskihajonta omaan sarakkeeseen
muunki_std = np.std(ruudut_joined["ki_muu_osuus"], ddof = 0)    

# lasketaan z-arvo
ruudut_joined["z-value"] = (ruudut_joined["ki_muu_osuus"]-muunki_mean) / muunki_std

# Now the z-value is 0 for blocks that have no residents or are protected