# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# REGIOPROJEKTCHECK
# sheet_lib.py
#
# Description:
# PROJECT URL: http://www.regioprojektcheck.de
#
# Author:
# ILS gGmbH / HCU Hamburg / GGR Planung
#
# LICENSE: The MIT License (MIT) Copyright (c) 2014 RPC Consortium
# ---------------------------------------------------------------------------


import tools.utils.tempmdb_lib as mdb
from os.path import join
import arcpy, os, imp, sys

def recalcPopulation(projektname):

    #get Paths

    base_path = str(sys.path[0]).split("2 Planungsprojekte analysieren")[0]
    workspace_projekt_definition = join(base_path,'3 Benutzerdefinierte Projekte',projektname,'FGDB_Definition_Projekt.gdb')

    #WOHNEN - EINWOHNERBERECHNUNG

    schrittmeldung = 'Ableitung Einwohnerzahl aus Wohneinheitenzahl \n'
    arcpy.AddMessage(schrittmeldung)
    print schrittmeldung

    # versuche, die EW-Tabellen zu loeschen, bevor sie neu erzeugt werden
    try:
        arcpy.Delete_management(join(workspace_projekt_definition,'Einwohnerzahl'))
    except:
        pass

    # Einwohnerzahl je Jahr und Teilflaeche erzeugen
    # 1. Schritt
    eingangstabellen = [
        (workspace_projekt_definition,'Wohneinheiten_Details'),
        (workspace_projekt_definition,'Projektrahmendaten')
    ]

    ausgabetabelle = (workspace_projekt_definition,'Einwohnerzahl')

    sql = """
    SELECT Wohneinheiten_Details.Jahr, Wohneinheiten_Details.Teilflaeche_Plangebiet,  Sum([Anzahl_WE]*[EW_je_WE]) AS Einwohnerzahl INTO Einwohnerzahl
    FROM Wohneinheiten_Details
    GROUP BY Wohneinheiten_Details.Jahr, Wohneinheiten_Details.Teilflaeche_Plangebiet;
    """
    mdb.temp_mdb(eingangstabellen,sql,ausgabetabelle)

    # 2. Schritt
    eingangstabellen = [
        (workspace_projekt_definition,'Jahre'),
        (workspace_projekt_definition,'Projektrahmendaten')
    ]

    ausgabetabelle = (workspace_projekt_definition,'temp_1')

    sql = """
    SELECT Jahre.Jahr AS BisJahr, Jahre_1.Jahr INTO temp_1
    FROM Jahre, Projektrahmendaten, Jahre AS Jahre_1
    WHERE (((Jahre.Jahr) Between [Beginn_Betrachtungszeitraum] And [Ende_Betrachtungszeitraum]) AND ((Jahre_1.Jahr) Between [Beginn_Betrachtungszeitraum] And [Jahre].[Jahr]));
    """
    mdb.temp_mdb(eingangstabellen,sql,ausgabetabelle)

    # 3. Schritt
    eingangstabellen = [
        (workspace_projekt_definition,'temp_1'),
        (workspace_projekt_definition,'Einwohnerzahl')
    ]

    ausgabetabelle = (workspace_projekt_definition,'Einwohner')

    sql = """
    SELECT temp_1.BisJahr as Jahr, Einwohnerzahl.Teilflaeche_Plangebiet, Sum(Einwohnerzahl.Einwohnerzahl) AS Einwohnerzahl INTO Einwohner
    FROM temp_1 INNER JOIN Einwohnerzahl ON temp_1.Jahr = Einwohnerzahl.Jahr
    GROUP BY temp_1.BisJahr, Einwohnerzahl.Teilflaeche_Plangebiet;
    """
    mdb.temp_mdb(eingangstabellen,sql,ausgabetabelle)

    #delete einwohnerzahl-table and rename einwohner-kum
    arcpy.Delete_management(join(workspace_projekt_definition,'temp_1'))
    arcpy.Delete_management(join(workspace_projekt_definition,'Einwohnerzahl'))

    in_data =  join(workspace_projekt_definition,'Einwohner')
    out_data = join(workspace_projekt_definition,'Einwohnerzahl')
    arcpy.Rename_management(in_data, out_data)
