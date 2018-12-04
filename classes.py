#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 10:51:21 2018

@author: hertta
"""
from shapely.ops import cascaded_union
from copy import deepcopy
import random
from shapely.geometry import LineString



class SchoolDistr: 
    """ todo: selitä attribuutit ja luokan tarkoitus, ehkä metodit.
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
        self.geometry = None
        
        # tietää oman maksimimatka-aikansa (nyk. maksimikävelyaika * 1.5 ??)
        self.maxttime = None
        
        # tietää oman tämänhetkisen oppilasmääränsä
        self.students = None
        
        # tietää oman maksimioppilasmääränsä, joka lasketaan vain alussa (kertoimella 1.25?)
        self.studentlimit = None
        
        # tietää oman tämän hetken z-arvonsa
        self.zvalue = None
        
        # tietää oman piirinsä pituuden
        self.perimeter = None
        
        self.initiate_distr_attrs()


# Metodit

    # Method for initializing  
    def initiate_distr_attrs(self):
        
        self.geometry = self.calculate_geometry()
        #self.meanttime = self.calculate_meanttime()
        self.maxttime = self.calculate_maxttime()
        self.students = self.calculate_studentbase()
        self.studentlimit = self.students*2
        self.zvalue = self.calculate_zvalue()
        self.perimeter = self.calculate_perimeter()

    # Method for updating  
    def update_distr(self):
        
        self.geometry = self.calculate_geometry()
        #self.meanttime = self.calculate_meanttime()        
        self.students = self.calculate_studentbase()
        self.zvalue = self.calculate_zvalue()
        self.perimeter = self.calculate_perimeter()    

    # laske geometria
    def calculate_geometry(self):
        
        geomList = []
        for key, item in self.blocks.items():
            geomList.append(item.geometry)
       
        # yhdistää ruudut yhdeksi polygoniksi ja tallentaa ne muuttujaan self.geometry
        return cascaded_union(geomList)
    

   # laske diameter-area -suhde
    def calculate_perimeter(self):
        
        if self.geometry == None:
            self.calculate_geometry()
            
        perimeter = self.geometry.boundary.length
        return perimeter
        
        
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
        
        return maxt * 1.25 # 1.5? 2?
        
        
    # laske z-arvo, pure population percentage -based
    def calculate_zvalue(self):
        
        fiSveSum = 0
        otherSum = 0
        for key, value in self.blocks.items():
            
            fiSveSum += value.langFiSve
            otherSum += value.langOther 
                    
        return otherSum/(otherSum + fiSveSum)      

    
    # laskee oppilaiden (6-8 v ?) hetkellisen määrän alueella
    def calculate_studentbase(self):
        
        studentSum = 0
        
        for key, value in self.blocks.items(): 
            studentSum += value.studentBase

        return studentSum
        
    
              
    # mitä ruutuja instanssi sivuaa (koskee). Palauttaa LISTAN
    def touches_which(self, blocks_dict):
        
        # grid  = kaikista block-luokan instansseista koostuva lista
        # tämä metodi palauttaa ne ruudut, joita self koskee (sivuaa)
        # tämä tehdään joka iteraation joka vuorolla
        # mieti, onko queen contiguity ongelma .touches() -metodissa
        # TÄYTYY OLLA OK JOS PALAUTUSARVO ON TYHJÄ, ELI EI KOSKETETA MITÄÄN
        neighbors = []
        
        for key, block in blocks_dict.items():
            if type(self.geometry.intersection(block.geometry)) == LineString:
                neighbors.append(block)
        
        return neighbors
    
    
    # hylkäysperiaatteen testaaminen: onko liian kaukana
    def is_too_far(self, block):
        
        # etsii omasta matka-aikamatriisistaan, onko kyseisen ruudun matka-aika suurempi kuin self.maxttime.
        # Palauttaa True jos ruutu on liian kaukana ja hylkäysperiaate toteutuu
        dist = self.ttmatrix[block.ykrId]['walk_d']
        return dist >= self.maxttime


    # lisää ruutu blocks -dictiin 
    def add_block(self, block):
        
        # lisää ruudun blocks -dictiin
        # päivittää geometrian ja z-valuen
        # tässä täytyy käsitellä myös "tyhjän" lisääminen ok vaihtoehtona, jolloin ei vaan tapahdu mitään
        if block == None:
            return
        else:
            block.schoolID = self.schoolID
            
            self.blocks[block.ykrId] = block
            
        
    # poista ruutu blocks -dictistä 
    def remove_block(self, block):
        
        # poistaa ruudun blocks -dictistä
        # päivittää geometrian ja z-valuen
        # tässä täytyy käsitellä myös "tyhjän" poistaminen ok vaihtoehtona, jolloin ei vaan tapahdu mitään
        if block == None:
            return
        else:
            del self.blocks[block.ykrId]

    
    # Tämä tehdään aina sille distrille, jolta ruutua oltaisiin ottamassa. Testataan, että distrin 
    # geometrian tietotyyppi pysyy samana, mikäli yksi ruutu poistetaan (ettei polygonista tule multipolygon - lisättäessä tietotyyppi voi kuitenkin muuttua toiseen suuntaan)       
    # palauttaa true jos contiguity rikkoutuu
    def break_contiguity(self, block):
        #kopioidaan self.blocks
        blocks_copy = deepcopy(self.blocks)
        
        geomList = []
        for key, item in blocks_copy.items():
            geomList.append(item.geometry)
        
        geom1 = cascaded_union(geomList)
        
        #poistetaan kopiosta ruutu
        del blocks_copy[block.ykrId] # ei ole TÄMÄ
        
        geomList = []
        for key, item in blocks_copy.items():
            geomList.append(item.geometry)
            
        geom2 = cascaded_union(geomList)
        
        
        # palauttaa True jos tietotyyppi muuttuu poiston seurauksena
        return type(geom1) != type(geom2) 



    # LOCAL version with global check 
    def select_best_block(self, blockset, districts, globalMean, globalStDev):
        
        
        fiSveSum = 0
        otherSum= 0
        
        for key, value in self.blocks.items():
            
            fiSveSum += value.langFiSve
            otherSum += value.langOther
        
        bestBlock = None
        
        for block in blockset:
            
            # testataan hylkäysperiaate 0
            if block.containsSchool == False:
            
               # testataan hylkäysperiate 1
                if (block.studentBase + self.students) <= self.studentlimit:
                    
                    # testataan hylkäysperiaate 2
                    if self.is_too_far(block) == False:
                        
                        # haetaan muuttujaan blockin districti
                        oldDistr = districts[block.schoolID]
                    
                        # testataan tietotyypin muuttumista, hylkäysperiaate 3
                        if oldDistr.break_contiguity(block) == False:
                            
                            old_fiSveSum = 0
                            old_otherSum= 0
                            
                            for key, value in oldDistr.blocks.items():
                                
                                old_fiSveSum += value.langFiSve
                                old_otherSum += value.langOther
                                
                            old_newZ = (old_otherSum - block.langOther) / (old_otherSum - block.langOther + old_fiSveSum - block.langFiSve)
                            old_currentZ = (old_otherSum) / (old_otherSum + old_fiSveSum)
                            
    
                            # testataan onko uusi parempi kuin tämänhetkinen self -z-arvo
                            
                            # kun bestBlock on tyhjä, verrataan alueen self.zvalueen
                            if bestBlock == None:       
                            
                                newZ_1 = (otherSum + block.langOther) / (otherSum + block.langOther + fiSveSum + block.langFiSve)
                                    
                                # jos vanhan distrin uusi z-arvo on pienempi tai yhtäsuuri kuin vanha tai vanhan distrin vanhan z-arvon ja uuden distrin vanhan z-arvon itseisarvonjen erotus on suurempi kuin vastaava uusilla
                                #if (((old_newZ - globalMean) / globalStDev) <= ((old_currentZ - globalMean) / globalStDev)) or abs(((old_currentZ - globalMean) / globalStDev) - ((self.zvalue - globalMean) / globalStDev)) > abs(((old_newZ - globalMean) / globalStDev) - ((newZ_1 - globalMean) / globalStDev)):
                                if abs(old_newZ - globalMean) <= abs(old_currentZ - globalMean) or abs((old_currentZ - globalMean)  - (self.zvalue - globalMean)) > abs((old_newZ - globalMean) - (newZ_1 - globalMean)):
                                    
                                     
                                     
                                     if abs(newZ_1 - globalMean) < abs(self.zvalue - globalMean):
                                     
                                        
                                         bestBlock = block
                                        #return block
                                    
                            else:
                                
                                newZ_2 = (otherSum + block.langOther) / (otherSum + block.langOther + fiSveSum + block.langFiSve)
                                current_best = (otherSum + bestBlock.langOther) / (otherSum + bestBlock.langOther + fiSveSum + bestBlock.langFiSve)
                                
                                # jos vanhan distrin uusi z-arvo on pienempi tai yhtäsuuri kuin vanha tai vanhan distrin vanhan z-arvon ja uuden distrin vanhan z-arvon itseisarvonjen erotus on suurempi kuin vastaava uusilla
                                #if (((old_newZ - globalMean) / globalStDev) <= ((old_currentZ - globalMean) / globalStDev)) or abs(((old_currentZ - globalMean) / globalStDev) - ((self.zvalue - globalMean) / globalStDev)) > abs(((old_newZ - globalMean) / globalStDev) - ((newZ_2 - globalMean) / globalStDev)):
                                if abs(old_newZ - globalMean) <= abs(old_currentZ - globalMean) or abs((old_currentZ - globalMean)  - (self.zvalue - globalMean)) > abs((old_newZ - globalMean) - (newZ_1 - globalMean)):
                                    
                                    if abs(newZ_2 - globalMean) < abs(current_best - globalMean):
                                    
                                        
                                        bestBlock = block 
                                    
        return bestBlock
    
                                

    # valitse random ruutu syötteen setistä. blockset on LISTA, jonka touches() palauttaa
    def select_random_block(self, blockset, districts):
        
        blocklist = []
        
        for block in blockset:
            
            # testataan hylkäysperiaate 0
            if block.containsSchool == False:
            
                # testataan hylkäysperiate 1
                if (block.studentBase + self.students) <= self.studentlimit:
                    
                    # testataan hylkäysperiaate 2
                    if self.is_too_far(block) == False:

                        # haetaan muuttujaan blockin districti
                        oldDistr = districts[block.schoolID]
                        
                        # testataan tietotyypin muuttumista, hylkäysperiaate 3
                        if oldDistr.break_contiguity(block) == False:
                            
                            # lisätään blocklistiin
                            blocklist.append(block)
        
        if len(blocklist) > 0:
            # generoidaan random numero sopivalta väliltä                
            randomindx = random.randint(0,len(blocklist)-1)
            
            # palautetaan random block
            return blocklist[randomindx]


###########################################################           



class Block:
    
    def __init__(self, geometry, ykrId, langFiSve, langOther, studentBase, schoolID, containsSchool):

        # tietää oman geometriansa
        self.geometry = geometry
        
        # tietää oman YKR id:nsä
        self.ykrId = ykrId
        
        # tietää oman suomen- ja ruotsinkielisten määränsä
        self.langFiSve = langFiSve
        
        # tietää oman muunkielisten määränsä
        self.langOther = langOther
        
        # tietää oman ala-asteikäisten lasten määränsä
        self.studentBase = studentBase
        
        # tietää oman tämän hetkisen kouluID:nsä
        self.schoolID = schoolID
    
        # tietää oman tämän hetkisen kouluID:nsä
        self.containsSchool = containsSchool
        
### DONE:
        
# selecting a new block and removing it from schoolDistr should not be able to break contiguity rule DONE
# in order to find the global optimum, there should be a diminishing chance to choose a random block instead of best block: make method select_random_block DONE
# contiguity check ei toimi jostain syystä! Korjaa!!! -> touches_which ja add tekee yhdessä multipolygoneja?! Touchesiin riittää vain kulmien koskettaminen, ja sen jälkeen kun lasketaan uusi geometria on tuloksena multipolygon..
### https://stackoverflow.com/questions/1960961/polygon-touches-in-more-than-one-point-with-shapely
# corrcted the z-value to be mean-based
# the optimization must be some kind of compromize between local & global optimum
# the optimization cannot base on block's z-values, but the block should have the absolute population variables as parameters. the z-values should be calculated as district-based value, basing on real population values
# corrcted the z-value to be mean-based. The problem now is, that the blocks with 0 -zvalue are attractive. Should change the 0 blocks to none, and only add them as "secondary"?
### there could be a 20% chance that a district will select a secondary block?
### in this case, None values should be handled in calculate z-value
# inside selectbest/select_random, check that the blocks actually containing the school building itself can not chance the district: block must have a new attribute self.containsSchool
# divide the one multipolygon in the data to two separate entities, also fix the data so that there won't be other multipolys
# make a gif of the process: plot either every 10th or 20th iteration 
        
### TODO:

# kokeillaan monimuuttujaoptimointia 
# 

# miksi vain 75:sää ruudussa on koulu, vaikka kouluja on 77? 
# make some kind of a check for polygon diameter / area, to make shapes less weird 

# share the execution to multiple processors

        
