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



# Metodit

    # laske geometria
    def calculate_geometry(self):
        
        geomList = []
        for key, item in self.blocks.items():
            geomList.append(item.geometry)
       
        # yhdistää ruudut yhdeksi polygoniksi ja tallentaa ne muuttujaan self.geometry
        self.geometry = cascaded_union(geomList)
        #return cascaded_union(geomList)
       
        
        
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
        
        self.maxttime = maxt * 2 # 1.5? 2?
        
        
#    # OLD, sum-based
#    laske z-arvo 
#    def calculate_zvalue(self, block, remove = False):
#        
#        #if self.zvalue == None: # jos operaatio tehdään ensimmäistä kertaa
#        if block == None:
#            Zsum = 0
#            for key, value in self.blocks.items():
#                Zsum += value.zvalue
#            self.zvalue = Zsum
#        
#        elif remove == True and block != None:
#            self.zvalue -= block.zvalue
#            
#        elif remove == False and block != None: # kun myöhemmin lisätään tai poistetaan ruutuja
#            self.zvalue += block.zvalue
#             
#        # lasketaan yhteen blocks-dictin z-valuet: Tehdään vain kerran alussa
#        # lisätään z-valueen uusi luku kun otetaan uusi ruutu tai vähennetään z-valuesta luku kun otetaan ruutu pois
         
 

#    # laske z-arvo, average-based
#    def calculate_zvalue(self, block, remove = False):
#        
#        #if self.zvalue == None: # jos operaatio tehdään ensimmäistä kertaa
#        if block == None:
#            Zsum = 0
#            for key, value in self.blocks.items():
#                Zsum += value.zvalue
#            self.zvalue = Zsum/len(self.blocks)*10 # Huom! tämä *100 lisätty **2 kertomista varten
#        
#        elif remove == True and block != None:
#            self.zvalue = (self.zvalue * len(self.blocks) - block.zvalue) / len(self.blocks)
#            
#        elif remove == False and block != None: # kun myöhemmin lisätään ruutuja
#            self.zvalue = (self.zvalue * len(self.blocks) + block.zvalue) / len(self.blocks)
#             
#        # lasketaan yhteen blocks-dictin z-valuet: Tehdään vain kerran alussa
#        # lisätään z-valueen uusi luku kun otetaan uusi ruutu tai vähennetään z-valuesta luku kun otetaan ruutu pois    
        
    # laske z-arvo, pure population percentage -based
    def calculate_zvalue(self):
        
        fiSveSum = 0
        otherSum = 0
        for key, value in self.blocks.items():
            
            fiSveSum += value.langFiSve
            otherSum += value.langOther 
                    
        self.zvalue = otherSum/(otherSum + fiSveSum)      

    
    # laskee oppilaiden (6-8 v ?) hetkellisen määrän alueella
    def calculate_studentbase(self):
        
        studentSum = 0
        
        for key, value in self.blocks.items(): 
            studentSum += value.studentBase

        self.students = studentSum
        
  
    def calculate_studentlimit(self):
        
        self.studentlimit = self.students * 3 # 1.5? 2?
    
              
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
            self.calculate_zvalue() 
            self.calculate_geometry()
            self.calculate_studentbase()
            
        
    # poista ruutu blocks -dictistä 
    def remove_block(self, block):
        
        # poistaa ruudun blocks -dictistä
        # päivittää geometrian ja z-valuen
        # tässä täytyy käsitellä myös "tyhjän" poistaminen ok vaihtoehtona, jolloin ei vaan tapahdu mitään
        if block == None:
            return
        else:
            del self.blocks[block.ykrId]
            self.calculate_zvalue()
            self.calculate_geometry()
            self.calculate_studentbase()
    
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
        del blocks_copy[block.ykrId]
        
        geomList = []
        for key, item in blocks_copy.items():
            geomList.append(item.geometry)
            
        geom2 = cascaded_union(geomList)
        
        # palauttaa True jos tietotyyppi muuttuu poiston seurauksena
        return type(geom1) != type(geom2)
            
        
#    # GLOBAL version
#    # valitse paras ruutu syötteen setistä
#    def select_best_block(self, blockset, districts, globalMean, globalStDev):
#        
#        # tässä käydään looppina blocksetissä olevia blockeja. Jokaisen kohdalla tsekataan ensin hylkäysperiaatteet.
#        # Mikäli hylkäysperiaatteet ok, tsekataan, onko blockin ja selfin z-valueiden summa itseisarvoltaan 
#        # lähempänä 0 kuin aikaisempi paras (alussa tämä paras arvo on selfin z-arvo, jotta turhia liitoksia ei tule)
#        # lopuksi palautetaan paras ruutu tai tyhjä arvo
#        
#        bestBlock = None
#        
#        # calculate the current global zvalue
#        zdict = {}
#        
#        current_zfactor = 0
#        bestblock_zfactor = 0
#        fiSveSum = 0
#        otherSum = 0
#        
#        for key, value in districts.items(): 
#            
#            zdict[key] = value.zvalue
#            current_zfactor += abs((value.zvalue-globalMean)/ globalStDev)    
#            
#        for key, value in self.blocks.items():
#            
#            fiSveSum += value.langFiSve
#            otherSum += value.langOther
#                
#        for block in blockset:
#            
#            # testataan hylkäysperiate 1
#            if (block.studentBase + self.students) <= self.studentlimit:
#                
#                # testataan hylkäysperiaate 2
#                if self.is_too_far(block) == False:
#                    
#                    # haetaan muuttujaan blockin districti
#                    oldDistr = districts[block.schoolID]
#                
#                    
#                    # testataan tietotyypin muuttumista, hylkäysperiaate 3
#                    if oldDistr.break_contiguity(block) == False:
#                        
#                        oldD_fiSveSum = 0
#                        oldD_otherSum = 0
#                        
#                        for key, value in oldDistr.blocks.items():
#                
#                            oldD_fiSveSum += value.langFiSve
#                            oldD_otherSum += value.langOther
#                        
#                    
#                        # testataan onko z-arvojen summa parempi kuin tämänhetkinen self -z-arvo
#                        
#                        # kun bestBlock on tyhjä, verrataan alueen self.zvalueen
#                        if bestBlock == None:
#                           
#                            # jos block.zvalue ja self.zvalue -summan itseisarvo on pienempi tai yhtäsuuri kuin self.zvalue yksin, block = bestBlock FIXME
#                            #if abs(block.zvalue + self.zvalue) <= abs(self.zvalue):
#                            #value = (self.zvalue * len(self.blocks) + block.zvalue) / len(self.blocks)
#                            
#                            #if abs(value)  < abs(self.zvalue):
#                            
#                            # kokeile globaali laskenta
#
#
#                            zcopy = deepcopy(zdict)
#                            
#                            zcopy[self.schoolID] = (otherSum + block.langOther) / (otherSum + block.langOther + fiSveSum + block.langFiSve)
#                            zcopy[block.schoolID] = (oldD_otherSum - block.langOther) / (oldD_otherSum - block.langOther + oldD_fiSveSum - block.langFiSve)
#                            
#                            zfactor1 = 0
#                            for key, value in zcopy.items():
#                                zfactor1 += abs((value-globalMean)/ globalStDev)
#                                
#                            if zfactor1  < current_zfactor:
#                                bestBlock = block
#                                bestblock_zfactor = zfactor1
#                        
#                        ## kun bestBlock ei ole tyhjä, verrataan bestblockin zvaluen ja self.zvaluen keskiarvon itseisarvoon
#                        else:
#                            
#                            #value =  (self.zvalue * len(self.blocks) + block.zvalue) / len(self.blocks) 
#                            #if abs(value) < abs((self.zvalue * len(self.blocks) + bestBlock.zvalue) / len(self.blocks)) :
#                            zcopy = deepcopy(zdict)
#                            
#                            zcopy[self.schoolID] = (otherSum + block.langOther) / (otherSum + block.langOther + fiSveSum + block.langFiSve)
#                            zcopy[block.schoolID] = (oldD_otherSum - block.langOther) / (oldD_otherSum - block.langOther + oldD_fiSveSum - block.langFiSve)
#                            
#                            zfactor2 = 0
#                            for key, value in zcopy.items():
#                                zfactor1 += abs((value-globalMean)/ globalStDev)
#                                
#                            if zfactor2  < bestblock_zfactor:
#                                bestBlock = block
#                                bestblock_zfactor = zfactor2                                
#                                
#                                
#                        
#        return bestBlock
    
#    # LOCAL version
#    def select_best_block(self, blockset, districts, globalMean, globalStDev):
#        
#        
#        fiSveSum = 0
#        otherSum= 0
#        
#        for key, value in self.blocks.items():
#            
#            fiSveSum += value.langFiSve
#            otherSum += value.langOther
#        
#        bestBlock = None
#        
#        for block in blockset:
#            
#           # testataan hylkäysperiate 1
#            if (block.studentBase + self.students) <= self.studentlimit:
#                
#                # testataan hylkäysperiaate 2
#                if self.is_too_far(block) == False:
#                    
#                    # haetaan muuttujaan blockin districti
#                    oldDistr = districts[block.schoolID]
#                
#                    
#                    # testataan tietotyypin muuttumista, hylkäysperiaate 3
#                    if oldDistr.break_contiguity(block) == False:
#
#                        # testataan onko uusi parempi kuin tämänhetkinen self -z-arvo
#                        
#                        # kun bestBlock on tyhjä, verrataan alueen self.zvalueen
#                        if bestBlock == None:       
#                        
#                            newZ_1 = (otherSum + block.langOther) / (otherSum + block.langOther + fiSveSum + block.langFiSve)
#                            
#                            if abs((newZ_1 - globalMean) / globalStDev) < abs((self.zvalue - globalMean) / globalStDev):
#                                
#                                bestBlock = block
#                                #return block
#                            
#                        else:
#                            
#                            newZ_2 = (otherSum + block.langOther) / (otherSum + block.langOther + fiSveSum + block.langFiSve)
#                            current_best = (otherSum + bestBlock.langOther) / (otherSum + bestBlock.langOther + fiSveSum + bestBlock.langFiSve)
#                            
#                            if abs((newZ_2 - globalMean) / globalStDev) < abs((current_best - globalMean) / globalStDev):
#                                
#                                bestBlock = block 
#                                
#        return bestBlock


    # LOCAL version with global check FIXME jos alueen itsensä arvo on vielä huonompi kuin alueen, jolta ryöstettäisi, pitäisi vaihdoksen olla mahdollinen!!!
    def select_best_block(self, blockset, districts, globalMean, globalStDev):
        
        
        fiSveSum = 0
        otherSum= 0
        
        for key, value in self.blocks.items():
            
            fiSveSum += value.langFiSve
            otherSum += value.langOther
        
        bestBlock = None
        
        for block in blockset:
            
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
                            if (((old_newZ - globalMean) / globalStDev) <= ((old_currentZ - globalMean) / globalStDev)) or abs(((old_currentZ - globalMean) / globalStDev) - ((self.zvalue - globalMean) / globalStDev)) > abs(((old_newZ - globalMean) / globalStDev) - ((newZ_1 - globalMean) / globalStDev)):
                                    
                                if abs((newZ_1 - globalMean) / globalStDev) < abs((self.zvalue - globalMean) / globalStDev):
                                    
                                    bestBlock = block
                                    #return block
                                
                        else:
                            
                            newZ_2 = (otherSum + block.langOther) / (otherSum + block.langOther + fiSveSum + block.langFiSve)
                            current_best = (otherSum + bestBlock.langOther) / (otherSum + bestBlock.langOther + fiSveSum + bestBlock.langFiSve)
                            
                            # jos vanhan distrin uusi z-arvo on pienempi tai yhtäsuuri kuin vanha tai vanhan distrin vanhan z-arvon ja uuden distrin vanhan z-arvon itseisarvonjen erotus on suurempi kuin vastaava uusilla
                            if (((old_newZ - globalMean) / globalStDev) <= ((old_currentZ - globalMean) / globalStDev)) or abs(((old_currentZ - globalMean) / globalStDev) - ((self.zvalue - globalMean) / globalStDev)) > abs(((old_newZ - globalMean) / globalStDev) - ((newZ_2 - globalMean) / globalStDev)):
                            
                                if abs((newZ_2 - globalMean) / globalStDev) < abs((current_best - globalMean) / globalStDev):
                                    
                                    bestBlock = block 
                                
        return bestBlock
    
                                

    # valitse random ruutu syötteen setistä. blockset on LISTA, jonka touches() palauttaa
    def select_random_block(self, blockset, districts):
        
        blocklist = []
        
        for block in blockset:
            
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
    
    def __init__(self, geometry, ykrId, langFiSve, langOther, studentBase, schoolID):

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
    

        
### DONE:
        
# selecting a new block and removing it from schoolDistr should not be able to break contiguity rule DONE
# in order to find the global optimum, there should be a diminishing chance to choose a random block instead of best block: make method select_random_block DONE
# contiguity check ei toimi jostain syystä! Korjaa!!! -> touches_which ja add tekee yhdessä multipolygoneja?! Touchesiin riittää vain kulmien koskettaminen, ja sen jälkeen kun lasketaan uusi geometria on tuloksena multipolygon..
### https://stackoverflow.com/questions/1960961/polygon-touches-in-more-than-one-point-with-shapely
# corrcted the z-value to be mean-based
        
### TODO:

# inside selectbest/select_random, check that the blocks actually containing the school building itself can not chance the district: block must have a new attribute self.containsSchool
# divide the one multipolygon in the data to two separate entities, also fix the data so that there won't be other multipolys
# make a gif of the process: plot either every 10th or 20th iteration 
# share the execution to multiple prosessors
        
        
        
# corrcted the z-value to be mean-based. The problem now is, that the blocks with 0 -zvalue are attractive. Should change the 0 blocks to none, and only add them as "secondary"?
## there could be a 20% chance that a district will select a secondary block?
## in this case, None values should be handled in calculate z-value
        
# make some kind of a check for polygon diameter / area, to make shapes less weird 
        
# the optimization must be some kind of compromize between local & global optimum

# the optimization cannot base on block's z-values, but the block should have the absolute population variables as parameters. the z-values should be calculated as district-based value, basing on real population values