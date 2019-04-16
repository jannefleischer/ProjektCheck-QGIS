# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# REGIOPROJEKTCHECK
# lib_gewerbemodell.py
#
# Description:
# PROJECT URL: http://www.regioprojektcheck.de
#
# Author:
# ILS gGmbH
#
# LICENSE: The MIT License (MIT) Copyright (c) 2014 RPC Consortium
# ---------------------------------------------------------------------------


#Die Betriebsflaechen berechnen
def betriebsflaechenErmitteln(projektname):
    import os, sys, arcpy
    arcpy.AddMessage("Betriebsflaechen ermitteln")
    #ueberpruefen, ob schon Angaben zu den Betriebsstrukturen gemacht wurden
    #pfade anlegen
    base_path = str(sys.path[0]).split("2 Planungsprojekte analysieren")[0]
    tabelle_gewerbe = join(base_path,'3 Benutzerdefinierte Projekte',projektname,'FGDB_11_Definition_Projekt.gdb','Gewerbe_Teilflaechen')
    counter = 0
    gewerbe_teilflaechen = arcpy.SearchCursor(tabelle_gewerbe)
    for flaeche in gewerbe_teilflaechen:
        counter+=1
    del gewerbe_teilflaechen
    if counter == 0:
        arcpy.AddMessage("Es wurden noch keine Angaben zu der Gewerbenutzung gemacht, das Tool '02_Planflaeche beschreiben/05_Gewerbe beschreiben' zum Anlegen verwenden")
        sys.exit()

    #betriebsflaechengroessen berechnen
    #flaechengroessen parameter laden
    betriebgroesse_parameter = join(base_path,'2_Tool','11_Definition_Projekt','FGDB_11_Definition_Projekt_Tool.gdb','gewerbe_betriebsflaechengroesse')
    betriebgroesse_parameter_cursor = arcpy.SearchCursor(betriebgroesse_parameter)
    for parameter in betriebgroesse_parameter_cursor:
        if parameter.Branche == "C":
            parameterC = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "D":
            parameterD = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "E":
            parameterE = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "F":
            parameterF = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "G":
            parameterG = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "H":
            parameterH = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "I":
            parameterI = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "J":
            parameterJ = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "K":
            parameterK = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "L":
            parameterL = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "M":
            parameterM = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "N":
            parameterN = parameter.Betriebsflaechengroesse_ha
        if parameter.Branche == "S":
            parameterS = parameter.Betriebsflaechengroesse_ha


    gewerbe_teilflaechen = arcpy.UpdateCursor(tabelle_gewerbe)
    for row in gewerbe_teilflaechen:
        if row.gewerbetyp.split(" -")[0] == "C":
            betriebsflaeche = row.anzahlBetriebe * parameterC
        if row.gewerbetyp.split(" -")[0] == "D":
            betriebsflaeche = row.anzahlBetriebe * parameterD
        if row.gewerbetyp.split(" -")[0] == "E":
            betriebsflaeche = row.anzahlBetriebe * parameterE
        if row.gewerbetyp.split(" -")[0] == "F":
            betriebsflaeche = row.anzahlBetriebe * parameterF
        if row.gewerbetyp.split(" -")[0] == "G":
            betriebsflaeche = row.anzahlBetriebe * parameterG
        if row.gewerbetyp.split(" -")[0] == "H":
            betriebsflaeche = row.anzahlBetriebe * parameterH
        if row.gewerbetyp.split(" -")[0] == "I":
            betriebsflaeche = row.anzahlBetriebe * parameterI
        if row.gewerbetyp.split(" -")[0] == "J":
            betriebsflaeche = row.anzahlBetriebe * parameterJ
        if row.gewerbetyp.split(" -")[0] == "K":
            betriebsflaeche = row.anzahlBetriebe * parameterK
        if row.gewerbetyp.split(" -")[0] == "L":
            betriebsflaeche = row.anzahlBetriebe * parameterL
        if row.gewerbetyp.split(" -")[0] == "M":
            betriebsflaeche = row.anzahlBetriebe * parameterM
        if row.gewerbetyp.split(" -")[0] == "N":
            betriebsflaeche = row.anzahlBetriebe * parameterN
        if row.gewerbetyp.split(" -")[0] == "S":
            betriebsflaeche = row.anzahlBetriebe * parameterS
        arcpy.AddMessage(row.gewerbetyp)
        arcpy.AddMessage(betriebsflaeche)
        row.betriebsflaeche_gewichtet = betriebsflaeche

        gewerbe_teilflaechen.updateRow(row)
    del gewerbe_teilflaechen
        #Alle gewichteten Betriebsflaechen mit dem selben Teilgebiet wie die aktuelle Zeile zusammen addieren
    gewerbe_teilflaechen = arcpy.UpdateCursor(tabelle_gewerbe)
    for row in gewerbe_teilflaechen:
        gebiet = row.teilflaeche
        #arcpy.AddMessage(gebiet)
        summeFlaeche = 0
        gewerbe_teilflaechenSearch = arcpy.SearchCursor(tabelle_gewerbe)
        for row2 in gewerbe_teilflaechenSearch:
            #arcpy.AddMessage(row2.teilflaeche)
            if row2.teilflaeche == gebiet:
                #arcpy.AddMessage(row2.betriebsflaeche_gewichtet)
                summeFlaeche = summeFlaeche + betriebsflaeche
        #Das nettobauland fuer die gesamte Teilflaeche ermitteln
        tabelle_gewerbe = join(base_path,'3 Benutzerdefinierte Projekte',projektname,'FGDB_11_Definition_Projekt.gdb','Gewerbe_Teilflaechen')
        gewerbe_teilflaechen_temp = arcpy.UpdateCursor(tabelle_gewerbe)
        nettoflaeche = 0
        for row3 in gewerbe_teilflaechen_temp:
            if row3.teilflaeche == gebiet:
                nettoflaeche = nettoflaeche + row3.nettobauland
        del gewerbe_teilflaechen_temp
        del gewerbe_teilflaechenSearch
        #Korrektur der gewichteten Betriebsflaeche
        #arcpy.AddMessage(betriebflaecheGewichtetGesamt)
        #arcpy.AddMessage(summeFlaeche)
        #arcpy.AddMessage(nettoflaeche)
        betriebsflaeche_korrigiert = betriebsflaeche / summeFlaeche * nettoflaeche
        row.betriebsflaeche_korrigiert = betriebsflaeche_korrigiert
        gewerbe_teilflaechen.updateRow(row)
    del gewerbe_teilflaechen





#Fuer jede Kombination aus Gewerbetyp und Teilflaeche die Flaechennutzung ermitteln
def flaechebilanzErmitteln(projektname,nameTeilflaeche,gebietstyp):
    import arcpy, sys,os
    arcpy.AddMessage("Flaechenbilanzen berechnen")

    #Pfade festlegen
    base_path = str(sys.path[0]).split("2 Planungsprojekte analysieren")[0]
    #workspace_basis = join(base_path, '1_Basisdaten', 'FGDB_01_Basisdaten_deutschland.gdb')
    workspace_projekt = join(base_path, '3 Benutzerdefinierte Projekte', projektname,
                                 'FGDB_11_Definition_Projekt_' + projektname + '.gdb')


    #Bruttoflaeche aus dem Shapefile ermitteln
    pfad_teilflaeche = join(workspace_projekt,'Teilflaechen_Plangebiet')
    sql = "Name ='"+nameTeilflaeche +"'"
    Plangebiet = arcpy.SearchCursor(pfad_teilflaeche,sql)
    bruttoflaeche = 0
    for flaeche in Plangebiet:
        bruttoflaeche = flaeche.Flaeche_ha
    del Plangebiet

    #Flaechengroessen berechnen
    #Nettoflaeche berechnen
    #aus Parametertabelle gewerbe_flaechenbilanzen die Parameter fuer den Gebietstypen ermitteln
    pfad_flaechenbilanz = join(base_path,'2_Tool','11_Definition_Projekt','FGDB_11_Definition_Projekt_Tool.gdb','gewerbe_flaechenbilanzen')
    #sql = 'Gebietstyp = '+"'"+gebietstyp+"'"
    #arcpy.AddMessage(sql)
    parameter_Anteil_Nettobauland = 0
    parameter_Gruenflaeche = 0
    parameter_Erschliessungsflaeche = 0
    parameter_Sonstige = 0
    parameter_tabelle = arcpy.SearchCursor(pfad_flaechenbilanz)
    for zeile in parameter_tabelle:
        #arcpy.AddMessage(zeile.Gebietstyp)
        #arcpy.AddMessage(gebietstyp)
        if zeile.Gebietstyp == gebietstyp:
            parameter_Anteil_Nettobauland = zeile.Anteil_Nettobauland
            parameter_Erschliessungsflaeche = zeile.Erschliessungsflaeche
            parameter_Gruenflaeche = zeile.Gruenflaeche
            parameter_Sonstige = zeile.Sonstige
    del parameter_tabelle
    nettobauland = bruttoflaeche * parameter_Anteil_Nettobauland
    gruenflaeche = bruttoflaeche * parameter_Gruenflaeche
    erschliessungsflaeche = bruttoflaeche * parameter_Erschliessungsflaeche
    sonstige = bruttoflaeche * parameter_Sonstige
    arcpy.AddMessage("Flaechenbilanz I: Bruttoflaeche: " + str(bruttoflaeche)+" Nettobauland: "+str(nettobauland)+ " Gruenflaeche: "+str(gruenflaeche)+ " Erschliessungsflaeche: "+str(erschliessungsflaeche)+ " Sonstiges: "+str(sonstige))

    resultat = [bruttoflaeche,nettobauland,gruenflaeche,sonstige,erschliessungsflaeche]
    #arcpy.AddMessage(resultat)
    return resultat


def nutzungsstruktur(projektname):

#fuer jede angelegte Gewerbenutzung weitere Parameter berechnen
    #pfade anlegen
    import sys, os, arcpy
    arcpy.AddMessage("Nutzungstruktur berechnen")
    base_path = str(sys.path[0]).split("2 Planungsprojekte analysieren")[0]
    tabelle_gewerbe = join(base_path,'3 Benutzerdefinierte Projekte',projektname,'FGDB_11_Definition_Projekt.gdb','Gewerbe_Teilflaechen')
    tabelle_gewerbe_update = arcpy.UpdateCursor(tabelle_gewerbe)
    for row in tabelle_gewerbe_update:
        branche = row.gewerbetyp.split(" -")[0]
        nettobauland = row.nettobauland

        tabelle_flaechenkenziffer = join(base_path,'2_Tool','11_Definition_Projekt','FGDB_11_Definition_Projekt_Tool.gdb','gewerbe_flaechenkennziffern')
        sql = "Branche = '" + branche+"'"
        #arcpy.AddMessage(sql)
        #Flaechenkennziffer vorbereiten
        tabelle_flaechenkenziffer_search = arcpy.SearchCursor(tabelle_flaechenkenziffer,sql)
        for row2 in tabelle_flaechenkenziffer_search:
            flaechenkennziffer = row2.Beschaeftigte_je_Hektar
        del tabelle_flaechenkenziffer, row2
        #Parameter Flaechengroesse Hallen und Verwaltung vorbereiten
        tabelle_gewerbe_verhaeltnis_hallen_verwaltung = join(base_path,'2_Tool','11_Definition_Projekt','FGDB_11_Definition_Projekt_Tool.gdb','gewerbe_verhaeltnis_hallen_verwaltung')
        tabelle_gewerbe_verhaeltnis_hallen_verwaltung_Search = arcpy.SearchCursor(tabelle_gewerbe_verhaeltnis_hallen_verwaltung,sql)
        for row3 in tabelle_gewerbe_verhaeltnis_hallen_verwaltung_Search:
            parameter_hallen = row3.Hallen
            parameter_verwaltung = row3.Verwaltung
        del row3, tabelle_gewerbe_verhaeltnis_hallen_verwaltung_Search
        #Parameter Volumen vorbereiten
        gewerbe_gebaeudehoehen_tabelle = join(base_path,'2_Tool','11_Definition_Projekt','FGDB_11_Definition_Projekt_Tool.gdb','gewerbe_verhaeltnis_hallen_verwaltung')
        gewerbe_gebaeudehoehen_tabelle_Search = arcpy.SearchCursor(gewerbe_gebaeudehoehen_tabelle,sql)
        for row4 in gewerbe_gebaeudehoehen_tabelle_Search:
            parameter_hallen_hoehe = row4.Hallen
            parameter_verwaltung_hoehe = row4.Verwaltung
        del row4, gewerbe_gebaeudehoehen_tabelle_Search
        beschaeftigte = round(nettobauland * flaechenkennziffer,2)
        row.beschaeftigte = beschaeftigte
        row.flaeche_hallen = round(row.betriebsflaeche_korrigiert * parameter_hallen, 2)
        row.flaeche_verwaltung = round(row.betriebsflaeche_korrigiert + parameter_verwaltung, 2)
        tabelle_gewerbe_update.updateRow(row)
    del tabelle_gewerbe_update
    tabelle_gewerbe_update = arcpy.UpdateCursor(tabelle_gewerbe)
    for row in tabelle_gewerbe_update:
        row.volumen_hallen = round(row.flaeche_hallen * parameter_hallen_hoehe * 10000,2)
        row.volumen_verwaltung = round(row.flaeche_verwaltung * parameter_verwaltung_hoehe * 10000,2)
        row.ueberbaute_Flaeche = row.flaeche_hallen+row.flaeche_verwaltung
        #flaechenbedeckung ermittelen
        #parametertabelle laden
        gewerbe_flaechennutzung = join(base_path,'2_Tool','11_Definition_Projekt','FGDB_11_Definition_Projekt_Tool.gdb','gewerbe_flaechennutzungNettobaulandAllgemein')
        tabelle_gewerbe_flaechennutzung = arcpy.SearchCursor(gewerbe_flaechennutzung,sql)
        for row5 in tabelle_gewerbe_flaechennutzung:
            parameter_flaeche_asphalt_beton = row5.Asphalt_Beton
            parameter_flaeche_kleinpflaster = row5.Kleinpflaster
            parameter_flaeche_platten = row5.Platten
            parameter_flaeche_wasser_decke_rasengitter = row5.Wassergebundene_Decke_Rasengittersteine
            parameter_flaeche_offener_boden_acker = row5.Offener_Boden_Acker
            parameter_flaeche_rasen = row5.Rasen
            parameter_flaeche_baeume_straeucher = row5.Baeume_Straeucher
            parameter_flaeche_stauden = row5.Stauden
            parameter_flaeche_wiese = row5.Wiese
            parameter_flaeche_wasser = row5.Natuerliche_Wasserflaeche
        del tabelle_gewerbe_flaechennutzung, row5
        row.flaeche_asphalt_beton = round(row.nettobauland * parameter_flaeche_asphalt_beton, 2)
        row.flaeche_kleinpflaster = round(row.nettobauland * parameter_flaeche_kleinpflaster, 2)
        row.flaeche_platten = round(row.nettobauland * parameter_flaeche_platten, 2)
        row.flaeche_wasser_decke_rasengitter = round(row.nettobauland * parameter_flaeche_wasser_decke_rasengitter, 2)
        row.flaeche_offener_boden_acker = round(row.nettobauland * parameter_flaeche_offener_boden_acker, 2)
        row.flaeche_rasen = round(row.nettobauland * parameter_flaeche_rasen, 2)
        row.flaeche_baeume_straeucher = round(row.nettobauland * parameter_flaeche_baeume_straeucher, 2)
        row.flaeche_stauden = round(row.nettobauland * parameter_flaeche_stauden, 2)
        row.flaeche_wiese = round(row.nettobauland * parameter_flaeche_wiese,2)
        row.flaeche_wasser = round(row.nettobauland * parameter_flaeche_wasser, 2)
        tabelle_gewerbe_update.updateRow(row)
    del tabelle_gewerbe_update


def betriebsstruktur(projektname):
    import sys,os,arcpy
    #Pfade festlegen
    base_path = str(sys.path[0]).split("2 Planungsprojekte analysieren")[0]
    workspace_projekt = join(base_path, '3 Benutzerdefinierte Projekte', projektname,'FGDB_11_Definition_Projekt_' + projektname + '.gdb')

    tabelle_gewerbe_teilflaechen = join(workspace_projekt, "Gewerbe_Teilflaechen")
    tabelle_gewerbe_betriebsstruktur = join(workspace_projekt, "Gewerbe_Betriebsstruktur")
    tabelle_parameter_aufsiedlungsdauer = join(base_path,'2_Tool','11_Definition_Projekt','FGDB_11_Definition_Projekt_Tool.gdb','gewerbe_aufsiedlungsdauer')

    tabelle_gewerbe_teilflaechen_Search = arcpy.SearchCursor(tabelle_gewerbe_teilflaechen)
    tabelle_gewerbe_betriebsstruktur_Insert = arcpy.InsertCursor(tabelle_gewerbe_betriebsstruktur)


    for row in tabelle_gewerbe_teilflaechen_Search:
        anzahl_betriebe_start = row.anzahlBetriebe
        aufsiedlungsdauer = row.aufsiedlungsdauer

        sql = "Dauer_Jahre = " + str(aufsiedlungsdauer)

        tabelle_parameter_aufsiedlungsdauer_Search = arcpy.SearchCursor(tabelle_parameter_aufsiedlungsdauer, sql)
        for row2 in tabelle_parameter_aufsiedlungsdauer_Search:
            parameter_jahr1 = row2.Jahr1
            parameter_jahr2 = row2.Jahr2
            parameter_jahr3 = row2.Jahr3
            parameter_jahr4 = row2.Jahr4
            parameter_jahr5 = row2.Jahr5
            parameter_jahr6 = row2.Jahr6
            parameter_jahr7 = row2.Jahr7
            parameter_jahr8 = row2.Jahr8
            parameter_jahr9 = row2.Jahr9
            parameter_jahr10 = row2.Jahr10
            parameter_jahr11 = row2.Jahr11
            parameter_jahr12 = row2.Jahr12
            parameter_jahr13 = row2.Jahr13
            parameter_jahr14 = row2.Jahr14
            parameter_jahr15 = row2.Jahr15
            parameter_jahr16 = row2.Jahr16
            parameter_jahr17 = row2.Jahr17
            parameter_jahr18 = row2.Jahr18
            parameter_jahr19 = row2.Jahr19
            parameter_jahr20 = row2.Jahr20
            parameter_jahr21 = row2.Jahr21
            parameter_jahr22 = row2.Jahr22
            parameter_jahr23 = row2.Jahr23
            parameter_jahr24 = row2.Jahr24
            parameter_jahr25 = row2.Jahr25
            parameter_jahr26 = row2.Jahr26
            parameter_jahr27 = row2.Jahr27
            parameter_jahr28 = row2.Jahr28
            parameter_jahr29 = row2.Jahr29
            parameter_jahr30 = row2.Jahr30
        del row2, tabelle_parameter_aufsiedlungsdauer_Search
        #Ergebnisse berechnen und einfuegen
        row3 = tabelle_gewerbe_betriebsstruktur_Insert.newRow()

        row3.anzahl_betriebe_jahr_1 = anzahl_betriebe_start * parameter_jahr1
        row3.anzahl_betriebe_jahr_2 = anzahl_betriebe_start * parameter_jahr2
        row3.anzahl_betriebe_jahr_3 = anzahl_betriebe_start * parameter_jahr3
        row3.anzahl_betriebe_jahr_4 = anzahl_betriebe_start * parameter_jahr4
        row3.anzahl_betriebe_jahr_5 = anzahl_betriebe_start * parameter_jahr5
        row3.anzahl_betriebe_jahr_6 = anzahl_betriebe_start * parameter_jahr6
        row3.anzahl_betriebe_jahr_7 = anzahl_betriebe_start * parameter_jahr7
        row3.anzahl_betriebe_jahr_8 = anzahl_betriebe_start * parameter_jahr8
        row3.anzahl_betriebe_jahr_9 = anzahl_betriebe_start * parameter_jahr9
        row3.anzahl_betriebe_jahr_10 = anzahl_betriebe_start * parameter_jahr10
        row3.anzahl_betriebe_jahr_11 = anzahl_betriebe_start * parameter_jahr11
        row3.anzahl_betriebe_jahr_12 = anzahl_betriebe_start * parameter_jahr12
        row3.anzahl_betriebe_jahr_13 = anzahl_betriebe_start * parameter_jahr13
        row3.anzahl_betriebe_jahr_14 = anzahl_betriebe_start * parameter_jahr14
        row3.anzahl_betriebe_jahr_15 = anzahl_betriebe_start * parameter_jahr15
        row3.anzahl_betriebe_jahr_16 = anzahl_betriebe_start * parameter_jahr16
        row3.anzahl_betriebe_jahr_17 = anzahl_betriebe_start * parameter_jahr17
        row3.anzahl_betriebe_jahr_18 = anzahl_betriebe_start * parameter_jahr18
        row3.anzahl_betriebe_jahr_19 = anzahl_betriebe_start * parameter_jahr19
        row3.anzahl_betriebe_jahr_20 = anzahl_betriebe_start * parameter_jahr20
        row3.anzahl_betriebe_jahr_21 = anzahl_betriebe_start * parameter_jahr21
        row3.anzahl_betriebe_jahr_22 = anzahl_betriebe_start * parameter_jahr22
        row3.anzahl_betriebe_jahr_23 = anzahl_betriebe_start * parameter_jahr23
        row3.anzahl_betriebe_jahr_24 = anzahl_betriebe_start * parameter_jahr24
        row3.anzahl_betriebe_jahr_25 = anzahl_betriebe_start * parameter_jahr25
        row3.anzahl_betriebe_jahr_26 = anzahl_betriebe_start * parameter_jahr26
        row3.anzahl_betriebe_jahr_27 = anzahl_betriebe_start * parameter_jahr27
        row3.anzahl_betriebe_jahr_28 = anzahl_betriebe_start * parameter_jahr28
        row3.anzahl_betriebe_jahr_29 = anzahl_betriebe_start * parameter_jahr29
        row3.anzahl_betriebe_jahr_30 = anzahl_betriebe_start * parameter_jahr30
        row3.projekt = projektname
        row3.teilflaeche = row.teilflaeche
        row3.branche = row.gewerbetyp


        tabelle_gewerbe_betriebsstruktur_Insert.insertRow(row3)














##Bodenbedeckung berechnen
#    #Parameter extrahieren
#    bodenbedeckung_pfad = join(base_path,'2_Tool','11_Definition_Projekt','FGDB_11_Definition_Projekt_Tool.gdb','gewerbe_flaechennutzungNettobaulandAllgemein')
#    bodenbedeckung_cursor = arcpy.SearchCursor(bodenbedeckung_pfad)
#    for row in bodenbedeckung_cursor:
#        if row.Branche == "C":
#            C = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "D":
#            D = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "E":
#            E = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "F":
#            F = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "G":
#            G = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "H":
#            H = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "I":
#            I = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "J":
#            J = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "K":
#            K = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "L":
#            L = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "M":
#            M = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "N":
#            N = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]
#        if row.Branche == "S":
#            S = [row.Uberbaute_Flaechen,row.Asphalt_Beton,row.Platten,row.Kleinpflaster,row.Wassergebundene_Decke_Rasengittersteine,row.Offener_Boden_Acker,row.Rasen,row.Baeume_Straeucher,row.Stauden,row.Wiese,row.Natuerliche_Wasserflaeche]