# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# REGIOPROJEKTCHECK
# sheet_lib.py
#
# Description: Export fact sheet for every RPC project
# PROJECT URL: http://www.regioprojektcheck.de
#
# Author:
# ILS gGmbH / HCU Hamburg / GGR Planung
#
# LICENSE: The MIT License (MIT) Copyright (c) 2014 RPC Consortium
# ---------------------------------------------------------------------------

import pctools.utils.tempmdb_lib as mdb
from os.path import join
import arcpy, os, sys, datetime, imp
from pctools.utils.config import Folders


def infosheet(projektname, wirkungsfeld, wb):
    folders = Folders()
    # Pfade setzen
    base_path = folders.BASE_PATH
    workspace_factsheet = folders.get_db(workspace='FGDB_Definition_Projekt.gdb', project=projektname)
    tablepath_vor = join(workspace_factsheet,'Vornutzungen_Details_Prozent')
    tablepath_teil = join(workspace_factsheet,'Teilflaechen_Plangebiet')
    tablepath_neu  = join(workspace_factsheet,'Flaechenbilanz_gruppiert')

    tablepath_rahmendaten = join(workspace_factsheet,'Projektrahmendaten')
    tablepath_WE = join(workspace_factsheet,'Wohnen_WE_in_Gebaeudetypen')
    tablepath_Gewerbe = join(workspace_factsheet,'Gewerbe_Beschaeftigte')
    tablepath_EZH = join(workspace_factsheet,'Versorgung_Verkaufsflaechen_Max')
    logo = join(folders.BASE_DBS, u"Erläuterungstexte", "logo_rpc.png")

    ####################################################################
    # erstelle Diverse Tabellen zur Erzeugung des Uebersichtsdatenblattes
    ####################################################################


    # Tabelle "Teilflaechen_Flaechenbilanz_gruppiert" erzeugen, falls noch nicht vorhanden
    eingangstabellen = [(workspace_factsheet,'Flaechenbilanz')]
    ausgabetabelle = (workspace_factsheet,'Flaechenbilanz_gruppiert')

    sql = """SELECT Flaechenbilanz.Teilflaeche_Plangebiet, Flaechenbilanz.Startjahr, Flaechenbilanz.Flaechennutzung_S1, Flaechenbilanz.Flaechennutzung_S2, Sum(Flaechenbilanz.Flaeche_ha) AS Flaeche_ha INTO Flaechenbilanz_gruppiert
    FROM Flaechenbilanz
    GROUP BY Flaechenbilanz.Teilflaeche_Plangebiet, Flaechenbilanz.Startjahr, Flaechenbilanz.Flaechennutzung_S1, Flaechenbilanz.Flaechennutzung_S2;
    """
    #if not os.path.exists(join(workspace_factsheet,'Flaechenbilanz_Planung_gruppiert')):
    mdb.temp_mdb(eingangstabellen,sql,ausgabetabelle)


    #Tabelle: "Gewerbe_Beschaeftigte_Max" erzeugen, falls noch nicht vorhanden
    eingangstabellen = [(workspace_factsheet,'Gewerbe_Beschaeftigte')]
    ausgabetabelle = (workspace_factsheet,'Gewerbe_Beschaeftigte_Max')

    sql = """SELECT Gewerbe_Beschaeftigte.Teilflaeche_Plangebiet, Max(Gewerbe_Beschaeftigte.Anzahl) AS [Max] INTO Gewerbe_Beschaeftigte_Max
    FROM Gewerbe_Beschaeftigte
    GROUP BY Gewerbe_Beschaeftigte.Teilflaeche_Plangebiet;
    """
    #if not os.path.exists(join(workspace_factsheet,'Gewerbe_Beschaeftigte_Max')):
    mdb.temp_mdb(eingangstabellen,sql,ausgabetabelle)

    Gewerbe_Beschaeftigte_Max = join(workspace_factsheet,'Gewerbe_Beschaeftigte_Max')

    #Tabelle: "Versorgung_Verkaufsflaechen_Max" erzeugen, falls noch nicht vorhanden
    eingangstabellen = [(workspace_factsheet,'Versorgung_Verkaufsflaechen')]
    ausgabetabelle = (workspace_factsheet,'Versorgung_Verkaufsflaechen_Max')

    sql = """SELECT Versorgung_Verkaufsflaechen.Teilflaeche_Plangebiet, Max(Versorgung_Verkaufsflaechen.Verkaufsflaeche) AS MaxvonVerkaufsflaeche INTO Versorgung_Verkaufsflaechen_Max
    FROM Versorgung_Verkaufsflaechen
    GROUP BY Versorgung_Verkaufsflaechen.Teilflaeche_Plangebiet;
    """
    #if not os.path.exists(join(workspace_factsheet,'Versorgung_Verkaufsflaechen_Max')):
    mdb.temp_mdb(eingangstabellen,sql,ausgabetabelle)


    ####################################################################
    # Workbook und Tabellenblätter anlegen
    ws1 = wb.add_worksheet('Projektrahmendaten'.decode('utf-8'))

    #Spaltenbreiten anpassen
    ws1.set_column(0, 0, 8)
    ws1.set_column(1, 1, 26)
    ws1.set_column(8, 8, 4)

    # Styles anlegen
    head = wb.add_format({'bold': True, 'font_size': '20', 'align': 'left','valign': 'vcenter', 'bg_color': 'white', 'border': '0'})
    normal = wb.add_format({'font_size': '14', 'bg_color': 'white', 'border': '0'})
    rechts = wb.add_format({'font_size': '14', 'align' : 'right', 'bg_color': 'white', 'border': '0'})
    bold = wb.add_format({'bold': True, 'font_size': '14', 'bg_color': 'white', 'border': '0'})
    percent = wb.add_format({'num_format': '0.0%', 'bg_color': 'white', 'border': '0'})
    background = wb.add_format({'bg_color': 'white', 'border': '0'})

    # Hintergrund weiß färben
    for x in range(0,200):
        for y in range(0,200):
            ws1.write(x,y,"", background)

    # Uhrzeit des Datenzugriffs festhalten
    now = datetime.datetime.now()


    ######## 2. Daten aus bestehenden Tabellen einlesen und in neue Kategorien umbrechen ########

    # Angelegte Teilflächen einlesen
    teilgebiete = dict()
    rows = arcpy.SearchCursor(tablepath_teil)
    for row in rows:
        name = row.getValue("Name")
        flaeche = row.getValue("Flaeche_ha")
        teilgebiete[name] = flaeche
    gesamtflaeche_vor = sum([i for i in teilgebiete.values()])
    del rows

    # Flächenbilanz der neuen Nutzung ermitteln, für Balkendiagramm auf neue Kategorien umlegen
    rows = arcpy.SearchCursor(tablepath_neu)
    land_neu, brach_neu, laerm_neu, gewerbe_neu, erschlie_neu, sozial_neu, ezh_neu, wohnen_neu, gruen_neu, natur_neu, sonstige_neu = 0,0,0,0,0,0,0,0,0,0,0

    gesamtflaeche_neu = 0
    for row in rows:
        gesamtflaeche_neu = gesamtflaeche_neu + row.getValue("Flaeche_ha")
    del rows

    rows = arcpy.SearchCursor(tablepath_neu)
    for row in rows:
        typ = row.getValue("Flaechennutzung_S2")
        wert = row.getValue("Flaeche_ha")
        anteil = wert / gesamtflaeche_neu
        if typ == 'Gewerbeflaeche': gewerbe_neu = gewerbe_neu + anteil
        if typ == 'Laermschutzanlagen': laerm_neu = laerm_neu + anteil
        if typ == 'Oeffentlich - Innere Erschliessung' or typ == 'Oeffentlich - Aeussere Erschliessung' or typ == 'Privat - Innere Erschliessung': erschlie_neu = erschlie_neu + anteil
        if typ == 'Gemeinbedarfsflaeche' or typ == 'Spielplaetze': sozial_neu = sozial_neu + anteil
        if typ == 'Einzelhandel': ezh_neu = ezh_neu + anteil
        if typ == 'Nettowohnbauland': wohnen_neu = wohnen_neu + anteil
        if typ == 'Allgemeine Gruenflaechen' or typ == 'Strassenbegleitgruen': gruen_neu = gruen_neu + anteil
        if typ == 'Ausgleichs- und Ersatzflaechen': natur_neu = natur_neu + anteil
        if typ == 'Sonstige Flaechen': sonstige_neu = sonstige_neu + anteil
    del rows

    # Gemeindename einesen
    rows = arcpy.SearchCursor(tablepath_rahmendaten)
    for row in rows:
        stadt = row.getValue("Gemeindename")

    # Realisierungszeitraum einlesen
    rows = arcpy.SearchCursor(tablepath_rahmendaten)
    for row in rows:
        start = row.getValue("Beginn_Betrachtungszeitraum")
        end = row.getValue("Ende_Betrachtungszeitraum")

    # Zahl der Wohneinheiten einlesen
    rows = arcpy.SearchCursor(tablepath_WE)
    WE = 0
    for row in rows:
        WE_teil = row.getValue("Anzahl_WE")
        if WE_teil == None:
            WE_teil = 0
        WE = WE + int(WE_teil)
    del rows

    # Zahl der Beschäftigen einlesen
    rows = arcpy.SearchCursor(Gewerbe_Beschaeftigte_Max)
    Besch = 0
    for row in rows:
        Besch_teil = row.getValue("Max")
        Besch = Besch + Besch_teil
    del rows
    Besch = 'ca. ' + "%.0f" % Besch

    # Verkaufsfläche einlesen
    rows = arcpy.SearchCursor(tablepath_EZH)
    EZH = 0
    for row in rows:
        # try/except-Schleifen, da Benennung der Quell-Tabellen momentan uneinheitlich
        try:
            EZH_teil = row.getValue("Max")
            EZH = EZH + EZH_teil
        except:
            try:
                EZH_teil = row.getValue("MaxvonVerkaufsflaeche")
                EZH = EZH + EZH_teil
            except:
                EZH_teil = 0
    del rows


    ######## 3. Textfelder in Datenblatt schreiben ########

    #Rohdaten in Tabellenblatt schreiben
    ws1.merge_range('C2:J4', projektname + ' in ' + stadt + '', head) #verbundene Zellen für die Überschrift
    ws1.write(6, 1, 'REGIOPROJEKTCHECK', bold)
    ws1.write(7, 1, 'Folgeabschätzung von Bauprojekten'.decode('utf-8'), normal)
    ws1.write(8, 1, 'Exportdatum', normal)
    ws1.write(8, 8, now.strftime("%Y-%m-%d %H:%M"), rechts)
    ws1.write(9, 1, 'Thema', normal)
    ws1.write(9, 8, str(wirkungsfeld).decode('utf-8'), rechts)
    ws1.write(11, 1, 'RAHMENDATEN', bold)
    ws1.write(12, 1, 'Fläche des Plangebiets'.decode('utf-8'), normal)
    ws1.write(12, 7, gesamtflaeche_vor, rechts)
    ws1.write(12, 8, 'ha', rechts)
    ws1.write(13, 1, 'Realisierungszeitraum', normal)
    ws1.write(13, 8, str(start) + ' - ' + str(end), rechts)
    ws1.write(15, 1, 'Wohnnutzung (Wohneinheiten)', normal)
    ws1.write(15, 7, WE, rechts)
    ws1.write(15, 8, 'WE', rechts)
    ws1.write(16, 1, 'Gewerbe (Arbeitsplätze)'.decode('utf-8'), normal)
    ws1.write(16, 8, Besch, rechts)
    ws1.write(17, 1, 'Einzelhandel (Verkaufsfläche)'.decode('utf-8'), normal)
    ws1.write(17, 7, EZH, rechts)
    ws1.write(17, 8, 'm²'.decode('utf-8'), rechts)


    ######## 4. Daten für Flächenbilanz in temporäres Arbeitsblatt schreiben (Notwendig für die Diagrammerstellung) ########

    data_neu = [land_neu, brach_neu, laerm_neu, gewerbe_neu, erschlie_neu, sozial_neu, ezh_neu, wohnen_neu, gruen_neu, natur_neu, sonstige_neu]
    #data_vor = [land_vor, brach_vor, laerm_vor, gewerbe_vor, erschlie_vor, sozial_vor, ezh_vor, wohnen_vor, gruen_vor, natur_vor, sonstige_vor]
    category_names = ['Landwirtschaft', 'Brachfläche'.decode('utf-8'), 'Lärmschutzanlage'.decode('utf-8'), 'Gewerbe', 'Erschließung'.decode('utf-8'), 'Soziale Infrastruktur', 'Einzelhandel', 'Wohnen', 'Grünflaeche'.decode('utf-8'), 'Natur', 'Sonstige']
    category_colors = ['#73583d', '#7f7f7f', '#595959', '#c4bd97', '#ffc000', '#e46c0a', '#b3a2c7', '#953735', '#c3d69b', '#4f6228', '#f2f2f2']

    ws2 = wb.add_worksheet('raw_data')
    #ws2.write(0,2,'Vornutzung')
    ws2.write(0,1,'Neue Nutzung')
    ws2.write_column('A2', category_names)

    for n,i in enumerate(data_neu):
        if i > 0:
            ws2.write(n+1,1,data_neu[n], percent) # nur Werte >0 in die Tabelle schreiben um Labels mit 0,0% zu vermeiden


    ######## 5. Diagramm Flächenbilanz erstellen ########

    # Chartobjekt erstellen, Diagramm formatieren
    chart = wb.add_chart({'type': 'bar', 'subtype': 'percent_stacked'})
    chart.set_size({'width': 1170, 'height': 200})
    chart.set_chartarea({'border': {'none': True}})
    chart.set_title({
        'name': 'FLÄCHENBILANZ'.decode('utf-8'),
            'name_font': {
                'size': 14
                    },
            'layout': {
                'x': 0.003,
                    'y': 0.05,
            }
    })

    chart.set_x_axis({
        'num_font': {
                'color': '#7f7f7f',
                    },
            'major_gridlines': {
                'visible': True,
                    'line': {
                        'width': 0.75,
                            'dash_type': 'dash',
                            'color': '#bfbfbf',
                    }
            }
    })

    chart.set_y_axis({
        'num_font': {
                'color': '#7f7f7f',
            }
    })

    chart.set_legend({'position': 'bottom'})

    # Datenbezüge definieren
    for i in range(0, 10):
        chart.add_series({
                'name':         '=raw_data!$A$'+str(i+2)+'',
                    'categories':   '=raw_data!$A$1:$A$1',
                    'values':       '=raw_data!$B$'+str(i+2)+':$B$'+str(i+2)+'',
                    'fill': 		{'color': ''+category_colors[i]+''},
                    'num_font':     {'color': 'white'},
                    'data_labels': 	{'value':  True},
                    'gap':        40,
            })
    ws1.insert_chart('B21', chart)

    # Datenblatt mit Rohdaten ausblenden
    ws2.hide()


    ######## 6. Miniaturkarte und Logo einfügen ########

    # Karte in Excelmappe einfuegen

    minimap = join(join(base_path,'3 Benutzerdefinierte Projekte',projektname,'Ergebnisausgabe','Abbildungen', 'Minimap.jpg'))
    if os.path.isfile(minimap):
        ws1.insert_image('L5', minimap, {'x_scale': 0.29, 'y_scale': 0.25}) #Korrigiert Verzerrung die bei 1x1 auftritt
    else:
        pass

    ws1.write(3, 11, 'ÜBERSICHTSKARTE'.decode('utf-8'), bold)

    # Logo einfuegen
    ws1.insert_image('B2', logo, {'x_scale': 1, 'y_scale': 0.93}) #Korrigiert Verzerrung die bei 1x1 auftritt

    print "Ausgabe beendet"

