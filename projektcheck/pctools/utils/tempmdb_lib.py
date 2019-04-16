# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# REGIOPROJEKTCHECK
# tempmdb_lib.py
#
# Description:
# PROJECT URL: http://www.regioprojektcheck.de
#
# Author:
# GGR Planung
#
# LICENSE: The MIT License (MIT) Copyright (c) 2014 RPC Consortium
# ---------------------------------------------------------------------------

import arcpy
import pyodbc
import shutil
import gc
import os
import sys
from os.path import join

def temp_mdb(eingangstabellen,sql,ausgabetabelle):
    # funktionsweise: kopiere tabellen aus einer gegebenen liste in eine temporäre PGDB, fuere sql-code auf diesen tabellen aus und kopiere das ergebnis zurueck


    arcpy.env.overwriteOutput = True

    # Create Temp Folder
    base_path = str(sys.path[0]).split("2 Planungsprojekte analysieren")[0] # Pfad zum Basisverzeichnis RPC
    out_folder_path = join(base_path,'2_Tool',"Projektverwaltung","temp") # Pfad zur temporaeren mdb inkl.
    temp_mdb_path =  join(out_folder_path,"PGDB_Temp.mdb")

    if not os.path.exists(out_folder_path):
        os.makedirs(out_folder_path)

    # Create Temp MDB File
    out_name = "PGDB_Temp.mdb"
    out_version = "10.0"
    try:
        arcpy.CreatePersonalGDB_management(out_folder_path, out_name, out_version)
    except:
        shutil.rmtree(out_folder_path)
        os.makedirs(out_folder_path)

    # Copy given tables to Temporary MDB File
    for eingangstabelle in eingangstabellen:
        eingangstabelle_pfad = join(eingangstabelle[0], eingangstabelle[1])
        temptabelle_pfad = join(temp_mdb_path, eingangstabelle[1].replace(' ','_'))

        arcpy.CopyRows_management(eingangstabelle_pfad, temptabelle_pfad, "")

    # run SQL code on imported tables in PGDB
    connectionstring = 'DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+temp_mdb_path # create connection string

    conn = pyodbc.connect(connectionstring)
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
    except Exception as e:
        arcpy.AddMessage("sql-fehlerhaft \n")
        arcpy.AddMessage(sql)
        sys.exit()

    conn.commit()
    conn.close()

    # Copy resulting table to FGDB
    fgdb_eingangstabelle_pfad = join(temp_mdb_path, ausgabetabelle[1])
    fgdb_ausgabetabelle_pfad = join(ausgabetabelle[0], ausgabetabelle[1])

    arcpy.CopyRows_management(fgdb_eingangstabelle_pfad, fgdb_ausgabetabelle_pfad, "")

    # Delete Temp Folder
    try:
        shutil.rmtree(out_folder_path)
    except:
        pass

    # Collect Garbage
    gc.collect()