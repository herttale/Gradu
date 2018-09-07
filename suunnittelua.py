#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 10:51:21 2018

@author: hertta
"""

class SchoolDistr: 

    def __init__(self, squares, ):

        # tietää omat ruutunsa
        self.squares = squares
        
        # tietää oman polygoninsa, joka lasketaan metodin avulla (voiko sen tehdä tässä initin sisällä?)
        self.geometry = None
        

- tietää oman tämän hetken z-arvonsa
- tietää oman maksimimatka-aikansa
- tietää oman maksimioppilasmääränsä
- attribuuttina myös dict-muodossa oma matka-aikamatriisi, josta aina tarkistetaan että voidaanko ottaa uusi ruutu

metodit
- getterit
- setterit
- mitä ruutuja oma polygoni sivuaa .touchesWho(rttk)
- mikä on tarkasteltavan ruudun matka-aika kävellen koululle, joudutaanko hylkäämään? .isCloseEnough(ruutu)
- laske z-arvo
- laske geometria
- poista ruutu
- lisää ruutu

asuinRuutu

- tietää oman z-arvonsa
- tietää oman ala-asteikäisten lasten määränsä
- tietää oman alueensa

metodit
- getterit
- setterit

joka iteraation lopussa tallennetaan kouluAlueiden z-arvojen summa listaan. kun tallennettava arvo on 
sama tai isompi kuin edellinen tallennettu arvo, iteraatiot lopetetaan.