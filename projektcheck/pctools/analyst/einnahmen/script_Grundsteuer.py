# -*- coding: utf-8 -*-

import os
import sys

import arcpy
import pctools.utils.layer_einnahmen as lib_einnahmen
from pctools.utils.params import Tool
import pctools.utils.chronik as c

class Grundsteuer(Tool):
    """Grundsteuer-Tool"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Einnahmen.gdb'

    def add_outputs(self):
        self.output.delete_output("GrSt")

        gemeinde_werte = lib_einnahmen.get_values(["GrSt"], self.projectname)

        symbology = lib_einnahmen.get_symbology(gemeinde_werte, 1)

        self.output.add_layer(
            groupname = "einnahmen",
            featureclass = "Gemeindebilanzen",
            template_layer = symbology,
            template_folder = "einnahmen",
            name = "Grundsteuer in €",
            disable_other = True,
            symbology = {'valueField': "GrSt"},
            label_replace = {'Einw_Saldo': 'GrSt'}
        )

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

    def run(self):

        params = self.par
        projektname = self.projectname

        lib_einnahmen.create_gemeindebilanzen(self, projektname)

        fields = ['AGS', 'Gemeindetyp']
        tablepath_rahmendaten = self.folders.get_table('Projektrahmendaten', "FGDB_Definition_Projekt.gdb")
        cursor = arcpy.da.SearchCursor(tablepath_rahmendaten, fields)
        for row in cursor:
            ags = row[0]
            gemeindetyp = row[1]

        tablepath_gemeinden = self.folders.get_base_table("FGDB_Basisdaten_deutschland.gdb", "bkg_gemeinden")
        tablepath_einkommen = self.folders.get_db("FGDB_Einnahmen.gdb", params.name.value)
        tablepath_hebesteuer = os.path.join(tablepath_einkommen, "GrSt_Hebesatz_B")
        fields = ["Hebesatz_GrStB"]
        if arcpy.Exists(tablepath_hebesteuer):
            cursor = arcpy.da.UpdateCursor(tablepath_hebesteuer, fields)
            for row in cursor:
                row[0] = params.slider1.value
                cursor.updateRow(row)
        else:
            arcpy.CreateTable_management(self.folders.get_db("FGDB_Einnahmen.gdb", params.name.value), "GrSt_Hebesatz_B")
            arcpy.AddField_management(tablepath_hebesteuer, "Hebesatz_GrStB", "LONG")
            cursor = arcpy.da.InsertCursor(tablepath_hebesteuer, fields)
            cursor.insertRow([params.slider1.value])

        fields = ["EFH_Rohmiete", 'DHH_Rohmiete', 'RHW_Rohmiete', 'MFH_Rohmiete', 'Bodenwert_Sachwertverfahren', 'qm_Grundstueck_pro_WE_EFH', 'BGF_Buero', 'BGF_Halle']
        tablepath_basisdaten = self.folders.get_table('GrSt_Basisdaten', "FGDB_Einnahmen.gdb")
        cursor = arcpy.da.UpdateCursor(tablepath_basisdaten, fields)
        for row in cursor:
                cursor.deleteRow()
        cursor = arcpy.da.InsertCursor(tablepath_basisdaten, fields)
        cursor.insertRow(   [params.slider2.value,
                            params.slider3.value,
                            params.slider4.value,
                            params.slider5.value,
                            params.slider6.value,
                            params.slider7.value,
                            params.slider8.value,
                            params.slider9.value]
                            )

        einheitswert_efh = 0
        einheitswert_dh = 0
        einheitswert_rh = 0
        einheitswert_mfh = 0

        wohnflaeche_efh = 0
        wohnflaeche_dh = 0
        wohnflaeche_rh = 0
        wohnflaeche_mfh = 0

        rohmiete_efh = 0
        rohmiete_dh = 0
        rohmiete_rh = 0
        rohmiete_mfh = 0

        garagen_efh = 0
        garagen_dh = 0
        garagen_rh = 0
        garagen_mfh = 0

        multiplikator_efh = 0
        multiplikator_dh = 0
        multiplikator_rh = 0
        multiplikator_mfh = 0

        table_wohnflaeche = self.folders.get_base_table("FGDB_Einnahmen_Tool.gdb", "GrSt_Wohnflaeche_und_Steuermesszahlen")
        fields = ["IDGebaeudetyp", "Mittlere_Wohnflaeche", "Aufschlag_Garagen_Carport"]
        cursor = arcpy.da.SearchCursor(table_wohnflaeche, fields)
        for row in cursor:
            if row[0] == 1:
                wohnflaeche_efh = row[1]
                garagen_efh = row[2]
            if row[0] == 2:
                wohnflaeche_dh = row[1]
                garagen_dh = row[2]
            if row[0] == 3:
                wohnflaeche_rh = row[1]
                garagen_rh = row[2]
            if row[0] == 4:
                wohnflaeche_mfh = row[1]
                garagen_mfh = row[2]

        if int(ags) <= 10999999:
            rohmiete_efh = params.slider2.value / 100.0
            rohmiete_dh = params.slider3.value / 100.0
            rohmiete_rh = params.slider4.value / 100.0
            rohmiete_mfh = params.slider5.value / 100.0
        else:
            rohmiete_efh, rohmiete_dh, rohmiete_rh, rohmiete_mfh = 0.46


        fields = ["AGS", "GemGroessKlass64"]
        where_clause = '"AGS"' + "='" + ags + "'"
        cursor = arcpy.da.SearchCursor(tablepath_gemeinden, fields, where_clause)
        for row in cursor:
            gemeinde_klasse = row[1]

        table_wohnflaeche = self.folders.get_base_table("FGDB_Einnahmen_Tool.gdb", "GrSt_Vervielfaeltiger")
        where_clause = '"Gemeindegroessenklasse64"' + "='" + gemeinde_klasse + "'"
        fields = ["Gemeindegroessenklasse64", "IDGebaeudetyp", "Vervielfaeltiger"]
        cursor = arcpy.da.SearchCursor(table_wohnflaeche, fields, where_clause)
        for row in cursor:
            if row[1] == 1:
                multiplikator_efh = row[2]
            if row[1] == 2:
                multiplikator_dh = row[2]
            if row[1] == 3:
                multiplikator_rh = row[2]
            if row[1] == 4:
                multiplikator_mfh = row[2]

        einheitswert_efh = (12 * rohmiete_efh * wohnflaeche_efh + garagen_efh) * multiplikator_efh
        einheitswert_dh = (12 * rohmiete_dh * wohnflaeche_dh + garagen_dh) * multiplikator_dh
        einheitswert_rh = (12 * rohmiete_rh * wohnflaeche_rh + garagen_rh) * multiplikator_rh
        einheitswert_mfh = (12 * rohmiete_mfh * wohnflaeche_mfh + garagen_mfh) * multiplikator_mfh


        if int(ags) >= 11000000:
            table_wohnflaeche = self.folders.get_base_table("FGDB_Einnahmen_Tool.gdb", "GrSt_Wohnflaeche_und_Steuermesszahlen")
            where_clause = '"IDGebaeudetyp"' + "='" + 1 + "'"
            fields = ["IDGebaeudetyp", "Umbauter_Raum_m3"]
            cursor = arcpy.da.SearchCursor(table_wohnflaeche, fields, where_clause)
            for row in cursor:
                    umbauter_raum_m3 = row[1]

            einheitswert_efh = 24/1.95583 * umbauter_raum_m3 + 550 + params.slider7.value * (params.slider6.value / 100.0)

        if params.slider8.value != 0 or params.slider9.value != 0:
            einheitswert_gewerbe = (1685 * params.slider8.value + 800 * params.slider9.value) * 0.1554
        else:
            einheitswert_gewerbe = 0

        we_efh = 0
        we_dh = 0
        we_rh = 0
        we_mfh = 0

        fields = ['IDGebaeudetyp', 'WE']
        tablepath_wohnen = self.folders.get_table('Wohnen_WE_in_Gebaeudetypen', "FGDB_Definition_Projekt.gdb")
        cursor = arcpy.da.SearchCursor(tablepath_wohnen, fields)
        for row in cursor:
            if row[0] == 1:
                we_efh += row[1]
            if row[0] == 2:
                we_dh += row[1]
            if row[0] == 3:
                we_rh += row[1]
            if row[0] == 4:
                we_mfh += row[1]

        arcpy.AddMessage("Einheitswert EFH = {}".format(einheitswert_efh))


        if einheitswert_efh <= 38346:
            einheitswert_bis_38346_EUR_efh = einheitswert_efh
            einheitswert_ab_38346_EUR_efh = 0
        else:
            einheitswert_bis_38346_EUR_efh = 38346
            einheitswert_ab_38346_EUR_efh = einheitswert_efh - 38346

        if einheitswert_dh <= 38346:
            einheitswert_bis_38346_EUR_dh = einheitswert_dh
            einheitswert_ab_38346_EUR_dh = 0
        else:
            einheitswert_bis_38346_EUR_dh = 38346
            einheitswert_ab_38346_EUR_dh = einheitswert_dh - 38346

        if einheitswert_rh <= 38346:
            einheitswert_bis_38346_EUR_rh = einheitswert_rh
            einheitswert_ab_38346_EUR_rh = 0
        else:
            einheitswert_bis_38346_EUR_rh = 38346
            einheitswert_ab_38346_EUR_rh = einheitswert_rh - 38346

        if einheitswert_mfh <= 38346:
            einheitswert_bis_38346_EUR_mfh = einheitswert_mfh
            einheitswert_ab_38346_EUR_mfh = 0
        else:
            einheitswert_bis_38346_EUR_mfh = 38346
            einheitswert_ab_38346_EUR_mfh = einheitswert_mfh - 38346

        table_wohnflaeche = self.folders.get_base_table("FGDB_Einnahmen_Tool.gdb", "GrSt_Wohnflaeche_und_Steuermesszahlen")
        fields = ["IDGebaeudetyp", "Steuermesszahl_bis_38346_EUR", "Steuermesszahl_ab_38346_EUR"]
        cursor = arcpy.da.SearchCursor(table_wohnflaeche, fields)
        for row in cursor:
            if row[0] == 1:
                steuermesszahl_bis_38346_EUR_efh = row[1]
                steuermesszahl_ab_38346_EUR_efh = row[2]
            if row[0] == 2:
                steuermesszahl_bis_38346_EUR_dh =row[1]
                steuermesszahl_ab_38346_EUR_dh = row[2]
            if row[0] == 3:
                steuermesszahl_bis_38346_EUR_rh =row[1]
                steuermesszahl_ab_38346_EUR_rh = row[2]
            if row[0] == 4:
                steuermesszahl_bis_38346_EUR_mfh = row[1]
                steuermesszahl_ab_38346_EUR_mfh = row[2]

        messbetrag_efh = we_efh * (einheitswert_bis_38346_EUR_efh * steuermesszahl_bis_38346_EUR_efh + einheitswert_ab_38346_EUR_efh * steuermesszahl_ab_38346_EUR_efh)
        messbetrag_dh = we_dh * (einheitswert_bis_38346_EUR_dh * steuermesszahl_bis_38346_EUR_dh + einheitswert_ab_38346_EUR_dh * steuermesszahl_ab_38346_EUR_dh)
        messbetrag_rh = we_rh * (einheitswert_bis_38346_EUR_rh * steuermesszahl_bis_38346_EUR_rh + einheitswert_ab_38346_EUR_rh * steuermesszahl_ab_38346_EUR_rh)
        messbetrag_mfh = we_mfh * (einheitswert_bis_38346_EUR_mfh * steuermesszahl_bis_38346_EUR_mfh + einheitswert_ab_38346_EUR_mfh * steuermesszahl_ab_38346_EUR_mfh)

        messbetrag_gewerbe = einheitswert_gewerbe * 0.0035


        def roundup(number, multiple):
            num = number + (multiple - 1)
            return num - (num % multiple)

        GRUNDSTEUERAUFKOMMEN = (messbetrag_efh + messbetrag_dh + messbetrag_rh + messbetrag_mfh + messbetrag_gewerbe) * params.slider1.value / 100.0

        table_bilanzen = self.folders.get_table("Gemeindebilanzen", "FGDB_Einnahmen.gdb")
        fields = ["AGS", "GrSt"]
        cursor = arcpy.da.UpdateCursor(table_bilanzen, fields)
        for row in cursor:
            if row[0] == ags:
                row[1] = GRUNDSTEUERAUFKOMMEN
            else:
                row[1] = 0
            cursor.updateRow(row)

        c.set_chronicle("Grundsteuer", self.folders.get_table(tablename='Chronik_Nutzung',workspace="FGDB_Einnahmen.gdb",project=projektname))
