# -*- coding: utf-8 -*-

import os
import sys

import arcpy
import tools.utils.chronik as c
from tools.utils.params import Tool
import tools.utils.layer_einnahmen as lib_einnahmen

class Familienleistungsausgleich(Tool):
    """FLA-Tool"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Einnahmen.gdb'

    def add_outputs(self):
        self.output.delete_output("FamLeistAusgl")

        gemeinde_werte = lib_einnahmen.get_values(["FamLeistAusgl"], self.projectname)

        symbology = lib_einnahmen.get_symbology(gemeinde_werte, 1)

        self.output.add_layer(
            groupname = "einnahmen",
            featureclass = "Gemeindebilanzen",
            template_layer = symbology,
            template_folder = "einnahmen",
            name = "FamLeistAusgl in €",
            disable_other = True,
            symbology = {'valueField': "FamLeistAusgl"},
            label_replace = {'Einw_Saldo': 'FamLeistAusgl'}
        )

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

    def run(self):
        """run FLA Tool"""

        params = self.par
        projektname = self.projectname


        tablepath_bilanz = self.folders.get_table('Gemeindebilanzen', "FGDB_Einnahmen.gdb")
        fields = ['FamLeistAusgl', 'ESt', 'AGS']

        tablepath_landesfaktor = self.folders.get_base_table("FGDB_Einnahmen_Tool.gdb", "FLA_Landesfaktoren")
        fields2 = ['AGS_Land', 'FLA_Faktor']

        cursor = arcpy.da.UpdateCursor(tablepath_bilanz, fields)
        for gemeinde in cursor:
            ags2 = gemeinde[2][0:2]
            where = '"AGS_Land"' + "='" + ags2 + "'"
            cursor2 = arcpy.da.SearchCursor(tablepath_landesfaktor, fields2, where)
            for land in cursor2:
                landesfaktor = land[1]
            FLA_Gemeindebilanz = gemeinde[1] * landesfaktor
            gemeinde[0] = FLA_Gemeindebilanz
            cursor.updateRow(gemeinde)

        c.set_chronicle("Familienleistungsausgleich", self.folders.get_table(tablename='Chronik_Nutzung',workspace="FGDB_Einnahmen.gdb",project=projektname))

