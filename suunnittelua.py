#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 10:51:21 2018

@author: hertta
"""

class SchoolDistr: 

    def __init__(self, blocks, studentlimit, ttmatrix):

        # tietää omat ruutunsa
        self.blocks = blocks

        # tietää oman matka-aikamatriisinsa, initissä se muutetaan dict-muotoon makeDict -metodilla
        self.ttmatrix = makeDict(ttmatrix)        
        
        # tietää oman polygoninsa, joka lasketaan metodin avulla (voiko sen tehdä tässä initin sisällä?)
        self.geometry = self.calculateGeometry() ### VOIKO TEHDÄ NÄIN?
        
        # tietää oman maksimimatka-aikansa (nyk. maksimikävelyaika * 1.5 ??)
        self.maxttime = self.calculateMaxttime() ### VOIKO TEHDÄ NÄIN?
        
        # tietää oman maksimioppilasmääränsä (tätä ehtoa täytyy hieman löysätä, katsotaan kuinka paljon, nyt kertoimella 1.25)
        self.studentlimit = studentlimit * 1.25
        
        # tietää oman tämän hetken z-arvonsa
        self.zvalue = self.calculateZvalue()



# Metodit

    # laske geometria
    def calculateGeometry(self):
        
    # laske maksimimatka-aika
    def calculateMaxttime(self):
        # nyk. maksimikävelyaika * 1.5 ??
    # laske z-arvo 
    def calculateZvalue(self):
        
    # tee matriisista dicti
    def __makeDict(ttmatrix):
        
    # mitä ruutuja instanssi sivuaa (koskee)
    def touchesWhich(self, grid)
    
    # hylkäysperiaatteen testaaminen: onko liian kaukana
    def isTooFar(self, block)

    # lisää ruutu blocks -dictiin 
    def addBlock(self, block):
        # tässä täytyy käsitellä myös "tyhjän" lisääminen ok vaihtoehtona, jolloin ei vaan tapahdu mitään

    # poista ruutu blocks -dictistä 
    def removeBlock(self, block)

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