#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 18:33:29 2018

@author: hertta
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
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

########################## ALKUVALMISTELUT ####################################
    

# 1. ladataan aineistot: rttk poiminta ja oppilasalueet, muutetaan ne euref-fin koordinaatistoon

ruudut = gpd.read_file("/home/hertsy/Documents/Kandi/Kandiaineisto/13rttk060_rttk2012/rttk2012_250m.shp")
ruudut.crs
ruudut = ruudut.to_crs('+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs')



alueet = gpd.read_file("/home/hertsy/Documents/Kandi/Kandiaineisto/oppilasalueiden rajat/2015/opevooa_2015_16_ala_aste_suomi.tab")
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


## joinataan rttk:n tiedot uuteen hki fishnetiin

fn_ruudut_joined = gpd.sjoin(fishnet_hki, ruudut_hki, how = 'left', op = 'within')

# plotataan
fn_ruudut_joined.plot(facecolor='gray')
fn_ruudut_joined.plot(column = 'ki_muu', linewidth=0.5, cmap =  'plasma_r')

# dropataan index_right -columni jotta voidaan tehdä seuraava liitos
fn_ruudut_joined = fn_ruudut_joined.drop("index_right", axis = 1)

# lasketaan ruuduille centroidit pisteinä
fn_ruudut_joined['centroid'] = fn_ruudut_joined.centroid
for key, row in fn_ruudut_joined.iterrows():
    fn_ruudut_joined.loc[key,'centroid'] = row['geometry'].centroid

# set geometry to centroid column
fn_ruudut_joined = fn_ruudut_joined.set_geometry('centroid')


# 3. joinataan rttk-ruutuihin tieto, mihin oppilasalueeseen kuuluvat (alueID)

ruudut_joined = gpd.sjoin(fn_ruudut_joined, alueet_proj, how = 'left', op = "within")

# check and plot the nan rows
ruudut_nan = ruudut_joined.loc[np.isnan(ruudut_joined['PINTA'])]
ruudut_nan.plot()

# drop the nan rows
ruudut_joined = ruudut_joined.loc[~np.isnan(ruudut_joined['PINTA'])]
ruudut_joined.plot()

# tarkastetaan plottaamalla että kaikki ok
ruudut_joined.plot(column = 'ki_fi', linewidth=0.5, cmap =  'plasma_r')

# asetetaan geometria takaisin ruuduiksi
ruudut_joined = ruudut_joined.set_geometry('geometry')

# testataan 
ruudut_joined.geometry

# pudotetaan centroidicolumni
ruudut_joined_fin = ruudut_joined.drop(['centroid'], axis = 1)

# plotataan testiksi
ruudut_joined_fin.plot(column = 'ki_fi', linewidth=0.5, cmap =  'plasma_r')

# korvataan nan -arvot -999:llä
ruudut_joined_fin1 = ruudut_joined_fin.fillna(-999)

# change data types from bytes and numpy floats and ints to python basic objects

# print the current data types for cols
for col in ruudut_joined_fin1:
    print(type(ruudut_joined_fin1.loc[2, col]))

# change the types for cols
ruudut_joined_fin2 = ruudut_joined_fin1.astype('object')

# check the types for row 5
for col in ruudut_joined_fin2:
    print(type(ruudut_joined_fin2.loc[5, col]))

### muuta string-columnit byteistä str-muotoon tallentamista varten
for col in ruudut_joined_fin2:
    if (type(ruudut_joined_fin2.loc[5, col]) == str):
        ruudut_joined_fin2[col] = ruudut_joined_fin2[col].astype(str)
    
# tallennetaan varmuuskopio shapefilena
ruudut_joined_fin2.to_file("/home/hertta/Documents/Gradu/oppilasalueet2018/ruudut_kieli_final.shp")





# 5. lasketaan kaikille ruuduille oma pos.diskriminaation indeksinsä. Jaetaan se kaikkien ruutujen keskihajonnalla 
# jotta saadaan z-arvo. Lasketaan kaikille ruuduille kaikkiin kouluihin myös matkustusaika?
# Matkustusajan laskemisen vaihtoehdot:
# - geokoodataan kaikki ala-asteen koulut osoitteiden perusteella, haetaan matka-aikamatriisit kaikkiin kouluihin 
#

# muutetaan salatut ruudut luvuksi, joka vastaa keskimääräistä indeksiarvoa (tässä muunkielisten osuutta koko helsingissä)
avg_muunkielisten_osuus = sum(ruudut_joined.loc[ruudut_joined["ki_muu"] > -1,"ki_muu"])/sum(ruudut_joined.loc[ruudut_joined["ki_vakiy"] > -1,"ki_vakiy"])

ruudut_joined["ki_muu_osuus"] = avg_muunkielisten_osuus

# lasketaan uusi sarake muunkielisten osuudesta kyseisessä ruudussa
for index, row in ruudut_joined.iterrows():
    if row["ki_muu"] > -1:
        ruudut_joined.at[index,"ki_muu_osuus"] = row["ki_muu"]/row["ki_vakiy"]

# lasketaan muunkielisten osuuden keskihajonta omaan sarakkeeseen

muunki_std = np.std(ruudut_joined["ki_muu_osuus"], ddof = 0)    
muunki_mean = ruudut_joined["ki_muu_osuus"].mean()
# lasketaan z-arvo
ruudut_joined["z-value"] = (ruudut_joined["ki_muu_osuus"]- muunki_mean)/muunki_std

# (ehkä, jos osoittautuu tarpeelliseksi: luodaan aputaulukko, jossa jokaisen ruudun attribuuttina on lista sen kaikista naapureista 
# (verkko/vieruslistatoteutus))

# 4. tehdään uusi taulukko, jossa polygoneina yhdistetyt oppilasalueruudut, joilla attribuutteina z-arvojen summa.
# tätä käytetään naapuruuden tunnistamisessa, ja muokataan koko ajan vastaamaan kyseistä hetkeä tekemällä merge ruudulle ja
# kohdepolygonille ja symmetric_difference ruudulle ja lähtöpolygonille

ruudut_final = ruudut_joined.loc[:,("ki_vakiy", "ki_fi", "ki_sv", "ki_muu", "geometry", "NIMI", "TOIMIPISTE_ID", "ki_muu_osuus", "z-value")]
koulut_final = ruudut_final.dissolve(by='TOIMIPISTE_ID', aggfunc='sum')
koulut_final.plot(column = 'z-value', linewidth=0.5, cmap =  'plasma_r')
# tehdään sarake jossa z-arvojen itseisarvot
koulut_final["abs_z_value"] = abs(koulut_final["z-value"])

# pohdintaa ja kokeilua sitä, voisiko polygonien piirin ja pinta-alan suhdetta käyttää rajoitteena
(koulut_final.loc[:,"geometry"].length / koulut_final.loc[:,"geometry"].area).mean()
(koulut_final.loc[:,"geometry"].length / koulut_final.loc[:,"geometry"].area).std()
(koulut_final.loc[:,"geometry"].length / koulut_final.loc[:,"geometry"].area).max()
(koulut_final.loc[:,"geometry"].length / koulut_final.loc[:,"geometry"].area).min()

# Määritetään kaikille kouluille (alueille) vakiona pysyvä maksimioppilasmäärä, nykyinen oppilasmäärä(päivitetään joka 
# iteraatiolla) ja keskimääräinen matka-aika kouluun(päivitetään joka iteraatiolla).
piirien maksimietäisyydet alkup.alueiden keskipisteistä * 2 ? sopisiko rajoitteeksi?
uuden ruudun etäisyys siis oltava maks 2 * edellä mainittu. Tämä testataan funktiossa ensin, koska diskauskriteeri


###################### ALKUVALMISTELUT PÄÄTTYY ##############################

# 6. aletaan iteroida alueita yksi kerrallaan käymällä läpi oppilasaluepolygonitaulukkoa 


# Alustetaan vakiomuuttujia
# maxetaisyys = xxx


#  Aloitetaan esim 20 iteraatiolla per polygoni eli for i=0, i <= 20, i++

#     for each polygoni in polys
#           maxoppilaita =  polygoni.loc[maxoppilaita]
#           id = polygoni.loc[alueID]
#           z = polygoni.loc[z_arvo]
#           if z != 0
#               
#               naapurit = ruudut.touches(polygoni)
#               liitettävä_ruutu = nan
#               parasluku = z
#               for ruutu in naapurit:
#                   if |z + ruutu.loc[z]| < |parasluku| and :
#                       parasluku = z + ruutu.loc[z]
#                       liitettävä_ruutu = ruutu

#           # tässä merkataan aluetta vaihtavaan ruutuun sen uusi alue
#           ruudut.loc[liitettävä_ruutu.loc[alueID]] = id
#           
# kun kaikki alueet on kertaalleen käyty läpi, muodostetaan uusi polygoniyhdiste ruuduista, ja korvataan edellinen polys 
# sillä. samalla päivitetään kaikki tunnusluvut. 
#  
    koulut_temp = ruudut_final.dissolve(by='TOIMIPISTE_ID', aggfunc='sum') 

    if(sum(koulut_temp["abs_z_value"])) >= (sum(koulut_final["abs_z_value"])):
        # stop function
        # return the last koulut_final
    else:
        koulut_final = koulut_temp

# tämän jälkeen         
        
############################ TESTAUSTA YMS. ############################

# Changing matplotlib backend
 
import matplotlib
gui_env = ['TKAgg','GTKAgg','Qt4Agg','WXAgg']
for gui in gui_env:
    try:
        print ("testing", gui)
        matplotlib.use(gui,warn=False, force=True)
        from matplotlib import pyplot as plt
        break
    except:
        continue
print( "Using:",matplotlib.get_backend())
        
        
x, y = geomtest.exterior.coords.xy
fig = plt.figure(1, figsize=(5,5), dpi=90)
ax = fig.add_subplot(111)
ax.plot(x, y, color='#6699cc', alpha=0.7,
    linewidth=3, solid_capstyle='round', zorder=2)
plt.show()

op_alueet2018 = gpd.read_file("/home/hertta/Documents/Gradu/oppilasalueet2018/Hki_ooa_alaaste_suomi.shp")

op_alueet2018.plot(facecolor='gray')
    
hiidenkivi1 = op_alueet2018.loc[(op_alueet2018["id"] == 114329) | (op_alueet2018["id"] == 114404) ,:] 
hiidenkivet = cascaded_union(hiidenkivi1['geometry']) 
op_alueet2018.at[13, 'geometry'] = hiidenkivet



hiidenkivi2 = op_alueet2018.loc[op_alueet2018["id"] == 114329]
hiidenkivi2.plot()

op_alueet2018.index[op_alueet2018["id"] == 114404] # 48

op_new = op_alueet2018.drop(48, axis = 0)

op_new.to_file("/home/hertta/Documents/Gradu/oppilasalueet2018/schoolAreas2018.shp")


for key, row in ruudut_joined.iterrows():
    ruudut_joined.loc[key] = row 
    

import pandas as pd
from geopandas.tools import geocode
koulut_osoitteet = pd.read_csv("/home/hertsy/Documents/Gradu/oppilasalueet2018/koulut_osoitteet.csv", sep = ",", encoding = "UTF-8")
koulut_geocoded = geocode(koulut_osoitteet['address'], provider = 'Nominatim', user_agent="hertsy")



from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="hertsy")
coordinates = []
for value in koulut_osoitteet['address']:
    location = geolocator.geocode(value)
    coordinates.append((location.latitude, location.longitude))
    
koulut_geocoded = gdp.read_file("/home/hertsy/Documents/Gradu/oppilasalueet2018/koulut_osoitteet_nom2.shp", encoding = "UTF-8")    
schoolareas = gdp.read_file("/home/hertsy/Documents/Gradu/oppilasalueet2018/schoolAreas2018.shp", encoding = "UTF-8") 
ruudut_final = gdp.read_file("/home/hertsy/Documents/Gradu/oppilasalueet2018/ruudut_kieli_final.shp", encoding = "UTF-8")

koulut_geocoded = koulut_geocoded.to_crs(schoolareas.crs)
ruudut_final = ruudut_final.to_crs(schoolareas.crs)

ax = ruudut_final.plot(column = 'ki_fi', linewidth=0.5, cmap =  'plasma_r');

schoolareas.plot(ax=ax, color='red', alpha=0.5);

ruudut_final['ID'] = ruudut_final['ID'].astype(int)
ruudut_final.plot(column = 'ID', linewidth=0.5, cmap =  'plasma_r')


koulut_geocoded = koulut_geocoded.drop(43, axis = 0)

epaonnistuneet = pd.read_csv("/home/hertsy/Documents/Gradu/oppilasalueet2018/notfound_nom.csv")





