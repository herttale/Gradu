#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 10:51:21 2018

@author: hertta
"""

import xxx, xxx, xxx


class SchoolDistr: 
    """ todo: selitä attribuutit ja luokan tarkoitus, ehkä metodit
    
    
    """
    
    def __init__(self, blocks, studentlimit: int, ttmatrix):
        
        # tietää omat ruutunsa, muutetaan heti dict-muotoon makeDict -metodilla
        self.blocks = make_dict(blocks)

        # tietää oman matka-aikamatriisinsa, muutetaan heti dict-muotoon makeDict -metodilla
        self.ttmatrix = make_dict(ttmatrix)        
        
        # tietää oman polygoninsa, joka lasketaan metodin avulla (voiko sen tehdä tässä initin sisällä?)
        self.geometry = self.calculate_geometry() ### VOIKO TEHDÄ NÄIN?
        
        # tietää oman maksimimatka-aikansa (nyk. maksimikävelyaika * 1.5 ??)
        self.maxttime = self.calculate_maxttime() ### VOIKO TEHDÄ NÄIN?
        
        # tietää oman maksimioppilasmääränsä (tätä ehtoa täytyy hieman löysätä, katsotaan kuinka paljon, nyt kertoimella 1.25)
        self.studentlimit = studentlimit * 1.25
        
        # tietää oman tämän hetken z-arvonsa
        self.zvalue = self.calculate_zvalue()



# Metodit

    # laske geometria
    def calculate_geometry(self):
        
        # yhdistää ruudut yhdeksi polygoniksi ja tallentaa ne muuttujaan self.geometry
        
    # laske maksimimatka-aika
    def calculate_maxttime(self):
        
        # laskee oman matka-aika-maksimiarvonsa, joka toimii myöhemmin hylkäysperiaatteena. 
        # esim. nyk. maksimikävelyaika * 1.5 ??
        # tehdään vain kerran, kun instanssi luodaan
        
    # laske z-arvo 
    def calculate_zvalue(self, block):
        if block, self.zvalue = None:
            xxxx
        else:
            self.zvalue += block.zvalue
             
        # lasketaan yhteen blocks-dictin z-valuet.
        # Tehdään vain kerran alussa
    
    # lisätään z-valueen uusi luku kun otetaan uusi ruutu tai vähennetään z-valuesta luku kun otetaan ruutu pois    
    def update_zvalue(self, x):
        
        # tätä tarkoitus kutsua sisäisesti selectBestBlock -metodissa.
        # tällä lisätään tai vähennetään blockin z-arvosta luku, riippuen x:n etumerkistä
        
    # tee dataframesta dicti
    def makeDict(dataframe):
        
        # tehdään dataframesta dicti. Indeksistä tehdään avain.
        
    # mitä ruutuja instanssi sivuaa (koskee)
    def touchesWhich(self, grid)
    
        # tämä metodi palauttaa ne ruudut, joita self koskee (sivuaa)
        # tämä tehdään joka iteraation joka vuorolla
    
    # hylkäysperiaatteen testaaminen: onko liian kaukana
    def isTooFar(self, block):
        
        # etsii omasta matka-aikamatriisistaan

    # lisää ruutu blocks -dictiin 
    def addBlock(self, block):
        
        # lisää ruudun blocks -dictiin
        # tässä täytyy käsitellä myös "tyhjän" lisääminen ok vaihtoehtona, jolloin ei vaan tapahdu mitään

    # poista ruutu blocks -dictistä 
    def removeBlock(self, block):
        
        # poistaa ruudun blocks -dictistä
        # tässä täytyy käsitellä myös "tyhjän" poistaminen ok vaihtoehtona, jolloin ei vaan tapahdu mitään

    # valitse ruutu syötteen setistä
    def selectBestBlock(self, blockset):
        
        # tässä käydään looppina setissä olevia blockeja. Jokaisen kohdalla tsekataan ensin hylkäysperiaatteet.
        # Mikäli hylkäysperiaatteet ok, tsekataan, onko blockin ja selfin z-valueiden summa itseisarvoltaan 
        # lähempänä 0 kuin aikaisempi paras (alussa tämä paras arvo on selfin z-arvo, jotta turhia liitoksia ei tule)
        # lopuksi palautetaan paras ruutu tai tyhjä arvo
        



class Block:
    
    def __init__(self, Zvalue, studentBase, schoolDistr):

        # tietää omat ruutunsa
        self.Zvalue = Zvalue
        
        # tietää oman ala-asteikäisten lasten määränsä
        self.studentBase = studentBase
        
        # tietää oman tämän hetkisen alueensa
        self.schoolDistr = schoolDistr



Mainissa:

joka iteraation lopussa tallennetaan kouluAlueiden z-arvojen summa listaan. kun tallennettava arvo on 
sama tai isompi kuin edellinen tallennettu arvo, iteraatiot lopetetaan.