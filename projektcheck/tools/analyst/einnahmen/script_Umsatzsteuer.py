# -*- coding: utf-8 -*-

import os
import sys

import arcpy
import tools.utils.chronik as c
from tools.utils.params import Tool
import tools.utils.layer_einnahmen as lib_einnahmen

class Umsatzsteuer(Tool):
    """Umsatzsteuer-Tool"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Einnahmen.gdb'

    def add_outputs(self):
        self.output.delete_output("Umsatzsteuer")

        gemeinde_werte = lib_einnahmen.get_values(["USt"], self.projectname)

        symbology = lib_einnahmen.get_symbology(gemeinde_werte, 1)

        self.output.add_layer(
            groupname = "einnahmen",
            featureclass = "Gemeindebilanzen",
            template_layer = symbology,
            template_folder = "einnahmen",
            name = "Umsatzsteuer in €",
            disable_other = True,
            symbology = {'valueField': "USt"},
            label_replace = {'Einw_Saldo': 'USt'}
        )

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

    def run(self):
        """run Umsatzsteuer Tool"""

        params = self.par
        projektname = self.projectname


        tablepath_bilanz = self.folders.get_table('Gemeindebilanzen', "FGDB_Einnahmen.gdb")
        fields = ['USt', 'GewSt', 'SvB_Saldo']

        tablepath_kennwerte = self.folders.get_base_table("FGDB_Einnahmen_Tool.gdb", "USt_Kennwerte")
        fields2 = ['GemAnt_USt_EUR_pro_EUR_GewSt', 'GemAnt_USt_EUR_pro_SvB']

        cursor_kennwerte = arcpy.da.SearchCursor(tablepath_kennwerte, fields2)
        for row in cursor_kennwerte:
            GemAnt_GewSt = row[0]
            GemAnt_SvB = row[1]

        cursor_bilanz = arcpy.da.UpdateCursor(tablepath_bilanz, fields)
        for gemeinde in cursor_bilanz:
            gemeinde[0] = GemAnt_GewSt * gemeinde[1] + GemAnt_SvB * gemeinde[2]
            cursor_bilanz.updateRow(gemeinde)

        c.set_chronicle("Umsatzsteuer", self.folders.get_table(tablename='Chronik_Nutzung',workspace="FGDB_Einnahmen.gdb",project=projektname))

