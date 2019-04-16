# -*- coding: utf-8 -*-

import arcpy, sys
import arcpy, os, inspect, pyodbc, shutil, gc, sys, datetime, xlsxwriter, imp
from xlsxwriter.utility import xl_rowcol_to_cell
from os.path import join, isdir, abspath, dirname, basename
import pctools.utils.chronik as c
from pctools.utils.params import Tool

import pctools.utils.tempmdb_lib as mdb
import pctools.utils.population_lib as pop

class Salden_bearbeiten2(Tool):

    _param_projectname = 'name'
    _workspace = 'FGDB_Einnahmen.gdb'

    def add_outputs(self):
        pass

    def run(self):

        parameters = self.par
        projektname = self.par.name.value
        saldo = self.par.saldo.value
        target_gemeinde = self.par.gemeinde.value
        target_gemeinde_kurz = target_gemeinde.split(" ||")[0]

        workspace_projekt_einnahmen = self.folders.get_db('FGDB_Einnahmen.gdb', projektname)
        wanderungssalden = os.path.join(workspace_projekt_einnahmen, 'Gemeindebilanzen')

        fields = ["GEN", "SvB_Saldo"]
        where_clause = '"GEN"' + "='" + target_gemeinde_kurz + "'"
        cursor = arcpy.da.UpdateCursor(wanderungssalden, fields, where_clause)
        for gemeinde in cursor:
            gemeinde[1] = saldo
            cursor.updateRow(gemeinde)

        # Bestimme AGS der Projektgemeinde
        pfad_rahmendaten = self.folders.get_table(
            tablename='Projektrahmendaten',
            workspace="FGDB_Definition_Projekt.gdb",
            project=projektname)
        cursor = arcpy.da.SearchCursor(pfad_rahmendaten, ["AGS"])
        for projekt in cursor:
            ags_projekt = projekt[0]

        if self.par.kontrolle.value == True:
            fields = ['AGS', 'Gemeindename']
            tablepath_rahmendaten = self.folders.get_table('Projektrahmendaten', "FGDB_Definition_Projekt.gdb")
            cursor = arcpy.da.SearchCursor(tablepath_rahmendaten, fields)
            for row in cursor:
                ags = row[0]
                gemeinde_plangebiet = row[1]

            fields = ['AGS', "SvB_Saldo", "Wanderungsanteil_SvB"]
            cursor = arcpy.da.UpdateCursor(wanderungssalden, fields)

            for x in range(0,3):
                saldo_summe = 0
                fields_saldo = ["SvB_Saldo"]
                cursor_saldo = arcpy.da.SearchCursor(wanderungssalden, fields_saldo)
                for gemeinde in cursor_saldo:
                    saldo_summe += gemeinde[0]
                if saldo_summe  == 0:
                    break
                arcpy.AddMessage("Saldo_Summe: " + str(saldo_summe))

                if saldo_summe < 0:
                    if gemeinde_plangebiet == target_gemeinde_kurz:
                        arcpy.AddMessage("Step 1")
                        for gemeinde in cursor:
                            if gemeinde[0] != ags:
                                gemeinde[1] -= round(saldo_summe * gemeinde[2])
                            cursor.updateRow(gemeinde)
                    else:
                        arcpy.AddMessage("Step 2")
                        for gemeinde in cursor:
                            if gemeinde[0] == ags:
                                gemeinde[1] -= saldo_summe
                            cursor.updateRow(gemeinde)
                elif saldo_summe > 0:
                    if gemeinde_plangebiet == target_gemeinde_kurz:
                        arcpy.AddMessage("Step 3")
                        for gemeinde in cursor:
                            if gemeinde[0] != ags:
                                gemeinde[1] -= round(saldo_summe * gemeinde[2])
                            cursor.updateRow(gemeinde)
                    else:
                        arcpy.AddMessage("Step 4")
                        for gemeinde in cursor:
                            if gemeinde[0] == ags:
                                gemeinde[1] -= saldo_summe
                            cursor.updateRow(gemeinde)

            #Gesamtsumme der Salden auf 0 setzen
            saldo_summe = 0
            cursor_saldo = arcpy.da.SearchCursor(wanderungssalden, fields_saldo)
            for gemeinde in cursor_saldo:
                saldo_summe += gemeinde[0]
            if saldo_summe != 0:
                fields = ["SvB_Saldo", "AGS"]
                cursor = arcpy.da.UpdateCursor(wanderungssalden, fields)
                for gemeinde in cursor:
                    if gemeinde[1] != ags_projekt:
                        gemeinde[0] -= saldo_summe
                        cursor.updateRow(gemeinde)
                        break


        arcpy.RefreshActiveView()
        arcpy.RefreshTOC()

        c.set_chronicle(u"Wanderung Beschäftigte", self.folders.get_table(tablename='Chronik_Nutzung',workspace="FGDB_Einnahmen.gdb",project=projektname))


