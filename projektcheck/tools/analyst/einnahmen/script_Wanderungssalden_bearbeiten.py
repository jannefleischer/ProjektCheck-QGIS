# -*- coding: utf-8 -*-

import arcpy, sys
import arcpy, os, inspect, pyodbc, shutil, gc, sys, datetime, xlsxwriter, imp
from xlsxwriter.utility import xl_rowcol_to_cell
from os.path import join, isdir, abspath, dirname, basename
import tools.utils.chronik as c
from tools.utils.params import Tool

import tools.utils.tempmdb_lib as mdb
import tools.utils.population_lib as pop

class Salden_bearbeiten(Tool):

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

        fields = ["GEN", self.parent_tbx._saldo_field]
        for key in self.parent_tbx.gemeinden_dict:
            where_clause = '"GEN"' + "='" + key + "'"
            cursor = arcpy.da.UpdateCursor(wanderungssalden, fields, where_clause)
            for gemeinde in cursor:
                    gemeinde[1] = self.parent_tbx.gemeinden_dict[key]
                    cursor.updateRow(gemeinde)

        if self.parent_tbx._saldo_field == "SvB_Saldo":
            zuzugsstatistik = "Zuzugsstatistik_SvB"
        else:
            zuzugsstatistik = "Zuzugsstatistik_Ew"
        table_zuzugsstatistik = self.folders.get_table(zuzugsstatistik, 'FGDB_Einnahmen.gdb')
        where_zuzug = 'NOT "Kategorie"' + "='" + 'Projektgemeinde/Region' + "'"
        fields_zuzug = ["Kategorie", "Anzahl"]
        cursor = arcpy.da.UpdateCursor(table_zuzugsstatistik, fields_zuzug, where_zuzug)
        for row in cursor:
            row[1] = abs(self.parent_tbx.gemeinden_dict[row[0]])
            cursor.updateRow(row)

        # Bestimme AGS der Projektgemeinde
        if self.par.kontrolle.value == True:
            fields = ['AGS', 'Gemeindename']
            tablepath_rahmendaten = self.folders.get_table('Projektrahmendaten', "FGDB_Definition_Projekt.gdb")
            cursor = arcpy.da.SearchCursor(tablepath_rahmendaten, fields)
            for row in cursor:
                ags = row[0]
                gemeinde_plangebiet = row[1]

            if self.parent_tbx.gemeinden_dict[gemeinde_plangebiet] == self.parent_tbx.gemeinden_dict_initial[gemeinde_plangebiet]:
                plangebiet_saldo_changed = False
            else:
                plangebiet_saldo_changed = True

            if self.parent_tbx._saldo_field == "SvB_Saldo":
                wanderungsanteil = "Wanderungsanteil_SvB"
            else:
                wanderungsanteil = "Wanderungsanteil_Ew"
            fields = ['AGS', self.parent_tbx._saldo_field, wanderungsanteil]
            cursor = arcpy.da.UpdateCursor(wanderungssalden, fields)

            for x in range(0,2):
                saldo_summe = 0.0

                fields_saldo = [self.parent_tbx._saldo_field]
                cursor_saldo = arcpy.da.SearchCursor(wanderungssalden, fields_saldo)
                for gemeinde in cursor_saldo:
                    saldo_summe += gemeinde[0]
                cursor_zuzug = arcpy.da.SearchCursor(table_zuzugsstatistik, fields_zuzug, where_zuzug)
                for row in cursor_zuzug:
                    saldo_summe -= row[1]

                arcpy.AddMessage("Saldo_Summe: " + str(saldo_summe))
                if saldo_summe  == 0:
                    break

                if saldo_summe < 0:
                    if plangebiet_saldo_changed == True:
                        for gemeinde in cursor:
                            if gemeinde[0] != ags:
                                gemeinde[1] -= saldo_summe * gemeinde[2]
                            cursor.updateRow(gemeinde)
                    else:
                        for gemeinde in cursor:
                            if gemeinde[0] == ags:
                                gemeinde[1] -= saldo_summe
                            cursor.updateRow(gemeinde)
                elif saldo_summe > 0:
                    if plangebiet_saldo_changed == True:
                        for gemeinde in cursor:
                            if gemeinde[0] != ags:
                                gemeinde[1] -= saldo_summe * gemeinde[2]
                            cursor.updateRow(gemeinde)
                    else:
                        for gemeinde in cursor:
                            if gemeinde[0] == ags:
                                gemeinde[1] -= saldo_summe
                            cursor.updateRow(gemeinde)

            #Restsumme verteilen
            saldo_summe = 0.0
            cursor_saldo = arcpy.da.SearchCursor(wanderungssalden, fields_saldo)
            for gemeinde in cursor_saldo:
                saldo_summe += gemeinde[0]
            cursor_zuzug = arcpy.da.SearchCursor(table_zuzugsstatistik, fields_zuzug, where_zuzug)
            for row in cursor_zuzug:
                saldo_summe -= row[1]
            if saldo_summe != 0:
                fields = [self.parent_tbx._saldo_field, "AGS"]
                cursor = arcpy.da.UpdateCursor(in_table = wanderungssalden, field_names = fields, sql_clause=(None, 'ORDER BY {} ASC'.format(self.parent_tbx._saldo_field)))
                for gemeinde in cursor:
                    if gemeinde[1] != ags:
                        gemeinde[0] -= saldo_summe
                        cursor.updateRow(gemeinde)
                        break

            del cursor, cursor_saldo, cursor_zuzug

        arcpy.RefreshActiveView()
        arcpy.RefreshTOC()

        if self.parent_tbx._saldo_field == "SvB_Saldo":
            c.set_chronicle(u"Wanderung Beschäftigte", self.folders.get_table(tablename='Chronik_Nutzung',workspace="FGDB_Einnahmen.gdb",project=projektname))
        else:
            c.set_chronicle(u"Wanderung Einwohner", self.folders.get_table(tablename='Chronik_Nutzung',workspace="FGDB_Einnahmen.gdb",project=projektname))


