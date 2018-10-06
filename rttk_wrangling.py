#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 11:25:28 2018

@author: hertsy

Preparing the rttk language grid data. This is data wrangling with test data, used in development.
coordinate reference system: etrs-tm35fin

"""
#ruudut_fp = "/home/hertta/Documents/Kandi/Kandiaineisto/13rttk060_rttk2012/rttk2012_250m.shp"
#alueet_fp = "/home/hertta/Documents/Gradu/oppilasalueet2018/schoolAreas2018.shp"

def buildRTTK(ruudut_fp, alueet_fp):

    import pandas as pd
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
    
    ruudut = gpd.read_file(ruudut_fp)
    ruudut.crs
    ruudut = ruudut.to_crs('+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs')
    
    
    
    alueet = gpd.read_file(alueet_fp, encoding = 'UTF-8')
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
    ruudut_nan = ruudut_joined.loc[np.isnan(ruudut_joined['ID'])]
    ruudut_nan.plot()
    
    # drop the nan rows
    ruudut_joined = ruudut_joined.loc[~np.isnan(ruudut_joined['ID'])]
    
    # tarkastetaan plottaamalla että kaikki ok
    ruudut_joined.plot()
    
    # asetetaan geometria takaisin ruuduiksi
    ruudut_joined = ruudut_joined.set_geometry('geometry_left')
    
    # pudotetaan centroidicolumni
    ruudut_joined = ruudut_joined.drop(['centroid', 'KUNTA_left','ALUEJAKO', 'KUNTA_right', 'NIMI_SE', 'YHTLUONTIP', 
                                        'YHTDATANOM', 'PAIVITETTY'], axis = 1)
    
    
    # korvataan nan -arvot -1:llä
    ruudut_joined = ruudut_joined.fillna(-1)
    
    # rename columns
    ruudut_joined = ruudut_joined.rename(columns = {'index_right': "index_alue", "geometry_left" : "geometry"})
    
    
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
    
    
    ############ join YKR IDs to rttk 
    
    # read the file and set crs
    ykrgrid = gpd.read_file("/home/hertta/Documents/Gradu/ttmatrices/MetropAccess_YKR_grid/MetropAccess_YKR_grid_EurefFIN.shp")
    ykrgrid = ykrgrid.to_crs('+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs')
    
    # calculate centroid for ykr_grid
    ykrgrid['centroid'] = ykrgrid.centroid
    
    # set geometry to centroid column in ykr grid
    ykrgrid = ykrgrid.set_geometry('centroid')
    
    # make spatial join
    ruudut_joined_ykr = gpd.sjoin(ruudut_joined, ykrgrid, how = 'left', op = 'contains')
    
    # make the dataframe geo again
    ruudut_joined_ykr = gpd.GeoDataFrame(ruudut_joined_ykr, geometry = "geometry_left", crs = ykrgrid.crs)
    
#    # plot nan rows
#    ruudut_joined_ykr_nan = ruudut_joined_ykr.loc[np.isnan(ruudut_joined_ykr['x'])]
#    ruudut_joined_ykr_nan.plot()
    
    # drop nan rows
    ruudut_joined_ykr = ruudut_joined_ykr.loc[~np.isnan(ruudut_joined_ykr['x'])]
    
    # drop unnecessary columns
    ruudut_joined_ykr = ruudut_joined_ykr.drop(['index_right', 'geometry_right'], axis = 1)
    
#    ruudut_joined_ykr.plot(column = 'z-value', linewidth=0.5, cmap =  'plasma_r')
    
    # change the series data type to int
    
    ruudut_joined_ykr['ID'] = ruudut_joined_ykr['ID'].astype(int)
    
    ## asetetaan ykrID indexiksi ja splitataan ruudut alueid:n mukaan. Tehdään splitatuista taulukoista dictejä indeksi key-arvona  
    
    # set new index
    ruudut_ykrindex = ruudut_joined_ykr.set_index(keys = 'YKR_ID', drop = False)
    
    # save the data and also return it
    ruudut_ykrindex.to_file("/home/hertta/Documents/Gradu/oppilasalueet2018/wrangled_rttk.shp")
    
    return ruudut_ykrindex

#ruudut_grouped = ruudut_ykrindex.groupby(by = 'ID')

#for key, group in ruudut_grouped:
#    
#    print(key)


