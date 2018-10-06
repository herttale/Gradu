#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 10:51:21 2018

@author: hertta
"""
from shapely.ops import cascaded_union
import pandas as pd 



class SchoolDistr: 
    """ todo: selitä attribuutit ja luokan tarkoitus, ehkä metodit
    blocks & ttmatrix täytyy olla dictejä
    
    
    """
    
    def __init__(self,schoolID, blocks, ttmatrix):
        
        # tietää oman kouluID:nsä
        self.schoolID = schoolID
        
        # tietää omat ruutunsa, dictiavaimen täytyy olla sama kuin ttmatrixissa
        self.blocks = blocks

        # tietää oman matka-aikamatriisinsa, Dictin avainten täytyy olla sama kuin blocksissa
        self.ttmatrix = ttmatrix        
        
        # tietää oman polygoninsa, joka lasketaan metodin avulla 
        self.geometry = self.calculate_geometry()
        
        # tietää oman maksimimatka-aikansa (nyk. maksimikävelyaika * 1.5 ??)
        self.maxttime = self.calculate_maxttime()
        
        # tietää oman tämänhetkisen oppilasmääränsä
        self.students = self.calculate_studentbase()
        
        # tietää oman maksimioppilasmääränsä, joka lasketaan vain alussa (kertoimella 1.25?)
        self.studentlimit = self.students * 1.25 # tai tähän calculate_studentbase metodi tilalle
        
        # tietää oman tämän hetken z-arvonsa
        self.zvalue = self.calculate_zvalue(block = None)



# Metodit

    # laske geometria
    def calculate_geometry(self):
        
        geomList = []
        for key, item in self.blocks.items():
            geomList.append(item.geometry)
        # yhdistää ruudut yhdeksi polygoniksi ja tallentaa ne muuttujaan self.geometry
        #blockFrame = pd.DataFrame.from_dict(data = self.blocks, orient='index')
        #geomList = blockFrame['geometry'].tolist()
        return cascaded_union(geomList)
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
        
        return maxt * 1.5
        
        
    # laske z-arvo 
    def calculate_zvalue(self, block, remove = False):
        
        #if self.zvalue == None: # jos operaatio tehdään ensimmäistä kertaa
        if hasattr(self, 'zvalue') == False:
            Zsum = 0
            for key, value in self.blocks.items():
                Zsum += value.zvalue
            return Zsum
        
        elif remove == True:
            return self.zvalue - block.zvalue
            
        else: # kun myöhemmin lisätään tai poistetaan ruutuja
            return self.zvalue + block.zvalue
             
        # lasketaan yhteen blocks-dictin z-valuet.
        # Tehdään vain kerran alussa
        # lisätään z-valueen uusi luku kun otetaan uusi ruutu tai vähennetään z-valuesta luku kun otetaan ruutu pois
    
    
    # laskee oppilaiden (6-8 v ?) hetkellisen määrän alueella
    def calculate_studentbase(self):
        
        studentSum = 0
        
        for key, value in self.blocks.items(): 
            studentSum += value.studentBase
                 
        #self.students =  studentSum
        # TODO kysy Samuelilta, miksi tässä täytyy palauttaa eikä voi viitata vain itseensä
        return studentSum
    
              
    # mitä ruutuja instanssi sivuaa (koskee)
    def touches_which(self, grid, geometry_column):
        
        # grid  = kaikista block-luokan instansseista koostuva lista
        # tämä metodi palauttaa ne ruudut, joita self koskee (sivuaa)
        # tämä tehdään joka iteraation joka vuorolla
        # mieti, onko queen contiguity ongelma .touches() -metodissa
        # MAINISSA TÄYTYY OLLA OK JOS PALAUTUSARVO ON TYHJÄ, ELI EI KOSKETETA MITÄÄN
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
            block.schoolDistr = self.shoolID
            self.blocks[block.ykrId] = block
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
            del self.blocks[block.ykrId]
            self.zvalue = self.calculate_zvalue(block, remove = True)
            self.geometry = self.calculate_geometry()

    # valitse ruutu syötteen setistä
    def select_best_block(self, blockset):
        
        # tässä käydään looppina blocksetissä olevia blockeja. Jokaisen kohdalla tsekataan ensin hylkäysperiaatteet.
        # Mikäli hylkäysperiaatteet ok, tsekataan, onko blockin ja selfin z-valueiden summa itseisarvoltaan 
        # lähempänä 0 kuin aikaisempi paras (alussa tämä paras arvo on selfin z-arvo, jotta turhia liitoksia ei tule)
        # lopuksi palautetaan paras ruutu tai tyhjä arvo
        
        bestBlock = None
                
        for block in blockset:
            
            # testataan hylkäysperiate 1
            if (block.studentBase + self.students) <= self.studentlimit:
                
                # testataan hylkäysperiaate 2
                if self.is_too_far(block) == False:
                    
                    # testataan onko z-arvojen summa parempi kuin tämänhetkinen self -z-arvo
                    
                    # kun bestBlock on tyhjä, verrataan alueen self.zvalueen
                    if bestBlock == None:
                       
                        # jos block.zvalue ja self.zvalue -summan itseisarvo on pienempi tai yhtäsuuri kuin self.zvalue yksin, block = bestBlock
                        if abs(block.zvalue + self.zvalue) <= abs(self.zvalue):
                            
                            bestBlock = block
                    
                    # kun bestBlock ei ole tyhjä, verrataan bestblockin zvaluen ja self.zvaluen summan itseisarvoon
                    else:
                        
                        if abs(block.zvalue + self.zvalue) < abs(bestBlock.zvalue + self.zvalue):
                            
                            bestBlock = block
                    
        return bestBlock
 



###########################################################           



class Block:
    
    def __init__(self, geometry, ykrId, zvalue, studentBase):

        # tietää oman geometriansa
        self.geometry = geometry
        
        # tietää oman YKR id:nsä
        self.ykrId = ykrId
        
        # tietää oman z-arvonsa
        self.zvalue = zvalue
        
        # tietää oman ala-asteikäisten lasten määränsä
        self.studentBase = studentBase
        
        
    # tietää oman tämän hetkisen kouluID:nsä
    def set_schooldistr(self, schoolDistr):
        
        self.schoolDistr = schoolDistr

### TODO:
# selecting a new block and removing it from schoolDistr should not be able to break contiguity rule
# in order to find the global optimum, there should be a diminishing chance to choose a random block instead of best block: make method select_random_block
