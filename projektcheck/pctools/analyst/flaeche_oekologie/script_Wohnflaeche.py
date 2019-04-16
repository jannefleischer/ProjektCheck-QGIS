# -*- coding: utf-8 -*-

import os
import sys
import arcpy
import pctools.utils.chronik as c
from pctools.utils.params import Tool
from pctools.diagrams.diagram_oekologie import Dia_Wohndichte
from pctools.diagrams.diagram_oekologie import Dia_Wohnflaechendichte


def rename_kreistyp(kreistyp):
    if kreistyp == 1:
        return u"Kernstädte (Agglomerationsräume)"
    elif kreistyp == 2:
        return u"Hochverdichtete Kreise (Agglomerationsräume)"
    elif kreistyp == 3:
        return u"Verdichtete Kreise (Agglomerationsräume)"
    elif kreistyp == 4:
        return u"Ländliche Kreise (Agglomerationsräume)"
    elif kreistyp == 5:
        return u"Kernstädte (Verstädtete Räume)"
    elif kreistyp == 6:
        return u"Verdichtete Kreise (Verstädtete Räume)"
    elif kreistyp == 7:
        return u"Ländliche Kreise (Verstädtete Räume)"
    elif kreistyp == 8:
        return u"Kreise höherer Dichte (Ländliche Räume)"
    elif kreistyp == 9:
        return u"Kreise geringerer Dichte (Ländliche Räume)"

class Wohnflaechendichte(Tool):
    """Wohnflaechendichte-Tool"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Flaeche_und_Oekologie.gdb'

    def add_outputs(self):
        par = self.par
        diagram = Dia_Wohnflaechendichte(projectname=self.par.name.value)
        self.output.add_diagram(diagram)

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

    def run(self):
        """run Wohnflaechendichte Tool"""

        par = self.par
        projektname = self.projectname
        tablepath_wohnflaeche = self.folders.get_table('Wohnflaechendichte', "FGDB_Flaeche_und_Oekologie.gdb")
        tablepath_wohngebaeude = self.folders.get_table('Wohnen_WE_in_Gebaeudetypen', "FGDB_Definition_Projekt.gdb")
        table_teilflaechen = self.folders.get_table("Teilflaechen_Plangebiet", "FGDB_Definition_Projekt.gdb")
        tablepath_rahmendaten = self.folders.get_table("Projektrahmendaten", "FGDB_Definition_Projekt.gdb")

        mean_wohnflaeche_efh = par.flaeche_efh.value
        mean_wohnflaeche_dh = par.flaeche_dh.value
        mean_wohnflaeche_rh = par.flaeche_rh.value
        mean_wohnflaeche_mfh = par.flaeche_mfh.value

        cursor = arcpy.da.UpdateCursor(tablepath_wohnflaeche, ["*"])
        for row in cursor:
            cursor.deleteRow()

        we_efh = 0
        we_dh = 0
        we_rh = 0
        we_mfh = 0

        cursor = arcpy.da.SearchCursor(tablepath_wohngebaeude, ["IDTeilflaeche", "IDGebaeudetyp", "WE"])
        for gebaeude in cursor:
            if gebaeude[0] == self.parent_tbx.id_teilflaeche:
                if gebaeude[1] == 1:
                    we_efh += gebaeude[2]
                elif gebaeude[1] == 2:
                    we_dh += gebaeude[2]
                elif gebaeude[1] == 3:
                    we_rh += gebaeude[2]
                elif gebaeude[1] == 4:
                    we_mfh += gebaeude[2]

        wohnflaeche_efh_qm = mean_wohnflaeche_efh * we_efh
        wohnflaeche_dh_qm = mean_wohnflaeche_dh * we_dh
        wohnflaeche_rh_qm = mean_wohnflaeche_rh * we_rh
        wohnflaeche_mfh_qm = mean_wohnflaeche_mfh * we_mfh

        wohnflaeche_gesamt_qm = wohnflaeche_efh_qm + wohnflaeche_dh_qm + wohnflaeche_rh_qm + wohnflaeche_mfh_qm

        teilflaeche_gesamt_qm = 0
        cursor = arcpy.da.SearchCursor(table_teilflaechen, ["id_teilflaeche", "Flaeche_ha", "Shape_Area"])
        for teilflaeche in cursor:
            if teilflaeche[0] == self.parent_tbx.id_teilflaeche:
                teilflaeche_gesamt_qm = teilflaeche[2] / 10000.0 * (1 - par.nettoflaeche.value / 100.0)

        wohnflaechendichte_projekt = round((wohnflaeche_gesamt_qm / teilflaeche_gesamt_qm))
        self.wohnflaechendichte_projekt = int(wohnflaechendichte_projekt)

        ags_projekt = ""
        cursor = arcpy.da.SearchCursor(tablepath_rahmendaten, "AGS")
        for row in cursor:
            ags_projekt = row[0]
            ags_kreis = ags_projekt[0:5]

        wohnflaechendichte_kreis = 0
        kreistyp = 0
        fields = ["AGS5", "Siedlungsstruktureller_Kreistyp", "Wohnflaechendichte_qm_Wohnfl_pro_ha_Nettowohnbauland", "Kreis_kreisfreie_Stadt"]
        where = '"AGS5"' + "='" + ags_kreis  + "'"
        table_kreis = self.folders.get_base_table("FGDB_Flaeche_und_Oekologie_Tool.gdb", "Wohndichte_Wohnflaechendichte_Kreise")
        cursor = arcpy.da.SearchCursor(table_kreis, fields, where)
        for kreis in cursor:
            kreistyp = kreis[1]
            wohnflaechendichte_kreis = round(kreis[2])
            kreis_name = u"Kreis: " + kreis[3].split(u", ")[0]
        self.wohnflaechendichte_kreis = int(wohnflaechendichte_kreis)

        where = '"Siedlungsstruktureller_Kreistyp"' + "=" + str(kreistyp)
        table_kreistyp = self.folders.get_base_table("FGDB_Flaeche_und_Oekologie_Tool.gdb", "Wohndichte_Wohnflaechendichte_RaumTypen")
        fields = ["Siedlungsstruktureller_Kreistyp", "Wohnflaechendichte_qm_Wohnfl_pro_ha_Nettowohnbauland", "Bezeichnung"]
        cursor = arcpy.da.SearchCursor(table_kreistyp, fields, where)
        for kreistyp in cursor:
            wohnflaechendichte_kreistyp = round(kreistyp[1])
            kreistyp_name = u"Typ: " + kreistyp[2]
            kreistyp_name = rename_kreistyp(kreistyp[0])
        self.wohnflaechendichte_kreistyp = int(wohnflaechendichte_kreistyp)

        column_values = {"Typ": [u"Teilfläche im Plangebiet", kreis_name, kreistyp_name],
                                "Wohnflaechendichte": [self.wohnflaechendichte_projekt, self.wohnflaechendichte_kreis, self.wohnflaechendichte_kreistyp]}
        self.parent_tbx.insert_rows_in_table("Wohnflaechendichte", column_values)



class Wohndichte(Tool):
    """Wohndichte-Tool"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Flaeche_und_Oekologie.gdb'

    def add_outputs(self):
        par = self.par
        diagram = Dia_Wohndichte(projectname=self.par.name.value)
        self.output.add_diagram(diagram)

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()


    def run(self):
        """run Wohndichte Tool"""

        par = self.par
        projektname = self.projectname
        tablepath_wohndichte = self.folders.get_table('Wohndichte', "FGDB_Flaeche_und_Oekologie.gdb")
        tablepath_wohngebaeude = self.folders.get_table('Wohnen_WE_in_Gebaeudetypen', "FGDB_Definition_Projekt.gdb")
        table_teilflaechen = self.folders.get_table("Teilflaechen_Plangebiet", "FGDB_Definition_Projekt.gdb")
        tablepath_rahmendaten = self.folders.get_table("Projektrahmendaten", "FGDB_Definition_Projekt.gdb")

        cursor = arcpy.da.UpdateCursor(tablepath_wohndichte, ["*"])
        for row in cursor:
            cursor.deleteRow()

        anzahl_we = 0
        cursor = arcpy.da.SearchCursor(tablepath_wohngebaeude, ["IDTeilflaeche", "IDGebaeudetyp", "WE"])
        for gebaeude in cursor:
            if gebaeude[0] == self.parent_tbx.id_teilflaeche:
                anzahl_we += gebaeude[2]

        nettwowohnbauland = 0
        cursor = arcpy.da.SearchCursor(table_teilflaechen, ["id_teilflaeche", "Flaeche_ha", "Shape_Area"])
        for teilflaeche in cursor:
            if teilflaeche[0] == self.parent_tbx.id_teilflaeche:
                nettwowohnbauland = teilflaeche[2] / 10000.0 * (1 - par.nettoflaeche.value / 100.0)

        wohndichte_projekt = round((anzahl_we / nettwowohnbauland))
        self.wohndichte_projekt = int(wohndichte_projekt)

        ags_projekt = ""
        cursor = arcpy.da.SearchCursor(tablepath_rahmendaten, "AGS")
        for row in cursor:
            ags_projekt = row[0]
            ags_kreis = ags_projekt[0:5]

        wohndichte_kreis = 0
        kreistyp = 0
        fields = ["AGS5", "Siedlungsstruktureller_Kreistyp", "Wohndichte_WE_pro_ha_Nettowohnbauland", "Kreis_kreisfreie_Stadt"]
        where = '"AGS5"' + "='" + ags_kreis  + "'"
        table_kreis = self.folders.get_base_table("FGDB_Flaeche_und_Oekologie_Tool.gdb", "Wohndichte_Wohnflaechendichte_Kreise")
        cursor = arcpy.da.SearchCursor(table_kreis, fields, where)
        for kreis in cursor:
            kreistyp = kreis[1]
            wohndichte_kreis = round(kreis[2])
            kreis_name = u"Kreis: " + kreis[3].split(u", ")[0]
        self.wohndichte_kreis = int(wohndichte_kreis)

        where = '"Siedlungsstruktureller_Kreistyp"' + "=" + str(kreistyp)
        table_kreistyp = self.folders.get_base_table("FGDB_Flaeche_und_Oekologie_Tool.gdb", "Wohndichte_Wohnflaechendichte_RaumTypen")
        fields = ["Siedlungsstruktureller_Kreistyp", "Wohndichte_WE_pro_ha_Nettowohnbauland", "Bezeichnung"]
        cursor = arcpy.da.SearchCursor(table_kreistyp, fields, where)
        for kreistyp in cursor:
            wohndichte_kreistyp = round(kreistyp[1])
            kreistyp_name = rename_kreistyp(kreistyp[0])
        self.wohndichte_kreistyp = int(wohndichte_kreistyp)



        column_values = {"Typ": [u"Teilfläche im Plangebiet", kreis_name, kreistyp_name],
                                "Wohndichte": [self.wohndichte_projekt, self.wohndichte_kreis, self.wohndichte_kreistyp]}
        self.parent_tbx.insert_rows_in_table("Wohndichte", column_values)

