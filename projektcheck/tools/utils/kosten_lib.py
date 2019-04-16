# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# REGIOPROJEKTCHECK
# kosten_lib.py
#
# Description: Erstellung der Bevölkerungsprognose für das zu untersuchende Projekt
# PROJECT URL: http://www.regioprojektcheck.de
#
# Author:
# GGR Planung
#
# LICENSE: The MIT License (MIT) Copyright (c) 2014 RPC Consortium
# ---------------------------------------------------------------------------


#
# Allgemeine Funktionen
#

import sys, arcpy
from os.path import join

def kostenregel_anlegen(name, gemeinden, kreis, private,
                        kostenaufteilungsregel_tabelle):

    #gemeinden
    rows = arcpy.InsertCursor(kostenaufteilungsregel_tabelle)
    row = rows.newRow()
    row.Kostenregelname = name
    row.Kostentraeger = 1
    row.Anteil = gemeinden
    row.Vorgabewert = 0
    rows.insertRow(row)

    #kreis
    rows = arcpy.InsertCursor(kostenaufteilungsregel_tabelle)
    row = rows.newRow()
    row.Kostenregelname = name
    row.Kostentraeger = 2
    row.Anteil = kreis
    row.Vorgabewert = 0
    rows.insertRow(row)

    #private
    rows = arcpy.InsertCursor(kostenaufteilungsregel_tabelle)
    row = rows.newRow()
    row.Kostenregelname = name
    row.Kostentraeger = 3
    row.Anteil = private
    row.Vorgabewert = 0
    rows.insertRow(row)

    #text = gemeinden,kreis,private
    #arcpy.AddMessage(text)

    # Delete cursor and row objects to remove locks on the data
    #
    del row
    del rows


def kostenregel_bearbeiten(name,gemeinden,kreis,private,
                           kostenaufteilungsregel_tabelle):

    # Step 1 - delete rule
    rows = arcpy.UpdateCursor(kostenaufteilungsregel_tabelle)

    for row in rows:
        # Delete all rows that have a roads type of 4
        if row.Kostenregelname == name:
            rows.deleteRow(row)

    del row, rows

    # Step 2 - create rule

    #gemeinden
    rows = arcpy.InsertCursor(kostenaufteilungsregel_tabelle)
    row = rows.newRow()
    row.Kostenregelname = name
    row.Kostentraeger = 1
    row.Anteil = gemeinden
    row.Vorgabewert = 0
    rows.insertRow(row)

    #kreis
    rows = arcpy.InsertCursor(kostenaufteilungsregel_tabelle)
    row = rows.newRow()
    row.Kostenregelname = name
    row.Kostentraeger = 2
    row.Anteil = kreis
    row.Vorgabewert = 0
    rows.insertRow(row)

    #private
    rows = arcpy.InsertCursor(kostenaufteilungsregel_tabelle)
    row = rows.newRow()
    row.Kostenregelname = name
    row.Kostentraeger = 3
    row.Anteil = private
    row.Vorgabewert = 0
    rows.insertRow(row)

    # Delete cursor and row objects to remove locks on the data
    #
    del row, rows

def kostenregel_loeschen(name, kostenaufteilungsregel_tabelle):
    rows = arcpy.UpdateCursor(kostenaufteilungsregel_tabelle)
    for row in rows:
        # Delete all rows that have a roads type of 4
        if row.Kostenregelname == name:
            rows.deleteRow(row)