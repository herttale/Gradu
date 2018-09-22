#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 10:51:21 2018

@author: hertta
"""
from shapely.ops import cascaded_union
import xxx, xxx, xxx


class SchoolDistr: 
    """ todo: selitä attribuutit ja luokan tarkoitus, ehkä metodit
    blocks & ttmatrix täytyy olla dictejä
    
    
    """
    
    def __init__(self, blocks, studentlimit: int, ttmatrix):
        
        # tietää omat ruutunsa, muutetaan heti dict-muotoon makeDict -metodilla. Avaimen täytyy olla sama kuin ttmatrixissa
        self.blocks = blocks

        # tietää oman matka-aikamatriisinsa, muutetaan heti dict-muotoon makeDict -metodilla. Dictin avainten täytyy olla sama kuin blocksissa
        self.ttmatrix = ttmatrix        
        
        # tietää oman polygoninsa, joka lasketaan metodin avulla 
        self.geometry = self.calculate_geometry()
        
        # tietää oman maksimimatka-aikansa (nyk. maksimikävelyaika * 1.5 ??)
        self.maxttime = self.calculate_maxttime()
        
        # tietää oman maksimioppilasmääränsä (tätä ehtoa täytyy hieman löysätä, katsotaan kuinka paljon, nyt kertoimella 1.25)
        self.studentlimit = studentlimit * 1.25
        
        # tietää oman tämän hetken z-arvonsa
        self.zvalue = self.calculate_zvalue(block = None)



# Metodit

    # laske geometria
    def calculate_geometry(self):
        
        # yhdistää ruudut yhdeksi polygoniksi ja tallentaa ne muuttujaan self.geometry
        blockFrame = pd.DataFrame.from_dict(data= self.blocks, orient='index')
        geomList = blockFrame['geometry'].tolist()
        self.geometry = cascaded_union(geomList)
        ## testattu, toimii itsenäisesti
        
        
    # laske maksimimatka-aika
    def calculate_maxttime(self):
        
        # laskee oman matka-aika-maksimiarvonsa, joka toimii myöhemmin hylkäysperiaatteena. 
        # esim. nyk. maksimikävelyaika * 1.5 ??
        # lasketaan vain kerran, kun instanssi luodaan
        maxt = 0
        for key, value in self.blocks.items(): 
            ttime = self.ttmatrix[key]['walk_d']
            if ttime > maxt:
                maxt = ttime
        
        self.maxttime = maxt * 1.5
        
        
    # laske z-arvo 
    def calculate_zvalue(self, block, remove = False):
        
        if self.zvalue == None: # jos operaatio tehdään ensimmäistä kertaa
            Zsum = 0
            for key, value in self.blocks.items():
                Zsum += value.Zvalue
            self.zvalue = Zsum
        
        elif remove == True:
            self.zvalue -= block.zvalue
            
        else: # kun myöhemmin lisätään tai poistetaan ruutuja
            self.zvalue += block.zvalue
             
        # lasketaan yhteen blocks-dictin z-valuet.
        # Tehdään vain kerran alussa
        # lisätään z-valueen uusi luku kun otetaan uusi ruutu tai vähennetään z-valuesta luku kun otetaan ruutu pois
    
              
    # mitä ruutuja instanssi sivuaa (koskee)
    def touches_which(self, grid, geometry_column):
        
        # grid  = kaikista block-luokan instansseista koostuva lista
        # tämä metodi palauttaa ne ruudut, joita self koskee (sivuaa)
        # tämä tehdään joka iteraation joka vuorolla
        # mieti, onko queen contiguity ongelma .touches() -metodissa
        neighbors = []
        
        for block in grid:
            bGeo = block.geometry
            if bGeo.touches(self.geometry):
                neighbors.append(block)
        
        return neighbors
    
    
    # hylkäysperiaatteen testaaminen: onko liian kaukana
    def is_too_far(self, block):
        
        # etsii omasta matka-aikamatriisistaan, onko kyseisen ruudun matka-aika suurempi kuin self.maxttime.
        # Palauttaa True jos ruutu on liian kaukana ja hylkäysperiaate toteutuu
        dist = self.ttmatrix[block.ykrId]['walk_d']
        if dist <= self.maxttime:
            return False
        else:
            return True


    # lisää ruutu blocks -dictiin 
    def add_block(self, block):
        
        # lisää ruudun blocks -dictiin
        # päivittää geometrian ja z-valuen
        # tässä täytyy käsitellä myös "tyhjän" lisääminen ok vaihtoehtona, jolloin ei vaan tapahdu mitään
        if block == None:
            return
        else:
            self.blocks[block.rttkId] = block
            self.zvalue = self.calculate_zvalue(block)
            self.geometry = self.calculate_geometry()
        
    # poista ruutu blocks -dictistä 
    def remove_block(self, block):
        
        # poistaa ruudun blocks -dictistä
        # päivittää geometrian ja z-valuen
        # tässä täytyy käsitellä myös "tyhjän" poistaminen ok vaihtoehtona, jolloin ei vaan tapahdu mitään
        if block == None:
            return
        else:
            del self.blocks[block.rttkId]
            self.zvalue = self.calculate_zvalue(block, remove = True)
            self.geometry = self.calculate_geometry()

    # valitse ruutu syötteen setistä
    def select_best_block(self, blockset):
        
        # tässä käydään looppina setissä olevia blockeja. Jokaisen kohdalla tsekataan ensin hylkäysperiaatteet.
        # Mikäli hylkäysperiaatteet ok, tsekataan, onko blockin ja selfin z-valueiden summa itseisarvoltaan 
        # lähempänä 0 kuin aikaisempi paras (alussa tämä paras arvo on selfin z-arvo, jotta turhia liitoksia ei tule)
        # lopuksi palautetaan paras ruutu tai tyhjä arvo
        



class Block:
    
    def __init__(self, geometry, ykrId, Zvalue, studentBase, schoolDistr):

        # tietää oman geometriansa
        self.geometry = geometry
        
        # tietää oman YKR id:nsä
        self.ykrId = ykrId
        
        # tietää oman z-arvonsa
        self.Zvalue = Zvalue
        
        # tietää oman ala-asteikäisten lasten määränsä
        self.studentBase = studentBase
        
        # tietää oman tämän hetkisen alueensa
        self.schoolDistr = schoolDistr



Mainissa:

joka iteraation lopussa tallennetaan kouluAlueiden z-arvojen summa listaan. kun tallennettava arvo on 
sama tai isompi kuin edellinen tallennettu arvo, iteraatiot lopetetaan.