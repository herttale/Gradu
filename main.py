#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 18:33:29 2018

@author: hertta
"""

import geopandas as gpd
import pandas as pd
import math


rttk = gpd.read_file("/home/hertta/Documents/Gradu/oppilasalueet2018/wrangled_rttk.shp", encoding = "UTF-8")
schools = gpd.read_file("/home/hertta/Documents/Gradu/oppilasalueet2018/koulut_euref_ykr.shp", encoding = "UTF-8")

# for testing purposes, create a new column in rttk including "pupils": 0.2 * ki_vakiy. In next versions this must be done when generating the data (rttk_wrangling)
rttk['pupils'] = rttk['ki_vakiy']*0.15
for key, row in rttk.iterrows():
    if row['pupils'] < 0:
        rttk.loc[key,'pupils'] = 0





# groupataan rttk
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
    districts[row_schoolID] = distr
    
    



# luodaan lista Zfactor, joka seuraa sdDictin z-arvojen muutosta. Alustetaan se districtsin z-arvojen itseisarvojen summalla.
Zfactor = []

# luodaan kierroksia laskeva muuttuja. Sitä käytetään mm. määrittämään, milloin Zfactorin kehitystä aletaan tarkkailla ja suoritus voidaan pysäyttää.
iteration = 1

# Iteroidan sdDictiä kunnes iteration on vähintään raja-arvo ja Zfactor ei enää muutu juurikaan pienemmäksi, jolloin palautetaan viimeinen tilanne ja break
while True:

    for distr in sdDict:
        
    




Idealista

Mainissa:

joka iteraation lopussa tallennetaan kouluAlueiden z-arvojen summa listaan. kun tallennettava arvo on 
sama tai isompi kuin edellinen tallennettu arvo, iteraatiot lopetetaan.


todennäköisyyden käyttäminen randomin/parhaan valinnassa:
-muttuja a:n alkuarvoksi esim. 70
- arvotaan random arvo väliltä 0, 70
- jos arvo on yli 50, tehdään random valinta, jos alle 50 valitaan paras ruutu
- joka iteraatiolla vähennetään luvusta 70 luku 1


TODO:
- schoolDistrille funktio randomin ruudun valitsemiseksi
- contiguityn rikkoutumisen estäminen: täytyy olla oma metodi, joka täytyy aina suorittaa select best block -metodissa hylkäysperiaatteena.












################################################ TESTING STUFF ETC #################################################



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
        
#################### SAVING THE DATA, byte error #########################
## change data types from bytes and numpy floats and ints to python basic objects
#
## print the current data types for cols
#for col in ruudut_joined:
#    print(type(ruudut_joined.loc[2, col]))
#
## change the types for cols
#ruudut_joined1 = ruudut_joined.astype('object')
#
## check the types for row 5
#for col in ruudut_joined1:
#    print(type(ruudut_joined1.loc[5, col]))
#
#### muuta string-columnit byteistä str-muotoon tallentamista varten
#for col in ruudut_joined1:
#    if (type(ruudut_joined1.loc[5, col]) == str):
#        ruudut_joined1[col] = ruudut_joined1[col].astype(str)
#    
## tallennetaan varmuuskopio shapefilena
#ruudut_joined1.to_file("/home/hertta/Documents/Gradu/oppilasalueet2018/ruudut_kieli_final.shp")
#
##############################################################################################

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


for key, row in fn_ruudut_joined.iterrows():
    fn_ruudut_joined.loc[key,'centroid'] = row['geometry'].centroid


### testataan touches -metodia
    
howmany = 0
block = ruudut_joined_ykr.loc[1711,'geometry_left']
for key,  row in ruudut_joined_ykr.iterrows():
    block2 = row['geometry_left']
    if block2.touches(block):
        howmany += 1
    
    
# test for equal ids

koulut_uniq = koulut_euref_ykr['id'].unique()
alueet_uniq = ruudut_ykrindex['ID'].unique()        

type(koulut_uniq)
koulut_uniq.dtype
alueet_uniq.dtype
koulut_uniq = np.array(koulut_uniq,dtype='float64') 

koulut_uniq.sort()
alueet_uniq.sort()
   