# -*- coding: utf-8 -*-

import os
import sys

import arcpy
import pctools.utils.chronik as c
from pctools.utils.params import Tool
import pctools.utils.layer_einnahmen as lib_einnahmen

class Gesamtsumme(Tool):
    """Gesamtsumme-Tool"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Einnahmen.gdb'

    def add_outputs(self):
        self.output.delete_output("Gesamtsumme")

        gemeinde_werte = lib_einnahmen.get_values(["Summe_Einnahmenbilanz"], self.projectname)

        symbology = lib_einnahmen.get_symbology(gemeinde_werte, 1)

        self.output.add_layer(
            groupname = "einnahmen",
            featureclass = "Gemeindebilanzen",
            template_layer = symbology,
            template_folder = "einnahmen",
            name = "Gesamtsumme in €",
            disable_other = True,
            symbology = {'valueField': "Summe_Einnahmenbilanz"},
            label_replace = {'Einw_Saldo': 'Summe_Einnahmenbilanz'}
        )

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

    def run(self):
        """run Gesamtsumme Tool"""

        params = self.par
        projektname = self.projectname

        tablepath_bilanz = self.folders.get_table('Gemeindebilanzen', "FGDB_Einnahmen.gdb")
        fields = self.parent_tbx.spalten
        arcpy.AddMessage(fields)
        cursor_bilanz = arcpy.da.UpdateCursor(tablepath_bilanz, fields)
        for gemeinde in cursor_bilanz:
            gemeinde[0] = 0
            for spalte in range (1, len(fields)):
                #arcpy.AddMessage(gemeinde[spalte])
                gemeinde[0] += gemeinde[spalte]
            cursor_bilanz.updateRow(gemeinde)

        c.set_chronicle("Gesamtbilanz", self.folders.get_table(tablename='Chronik_Nutzung',workspace="FGDB_Einnahmen.gdb",project=projektname))

