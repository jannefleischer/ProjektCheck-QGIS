# -*- coding: utf-8 -*-

import os
import sys

import arcpy

from pctools.utils.params import Tool


class HebesaetzeKontrolle(Tool):
    """HebesaetzeKontrolle-Tool"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Einnahmen.gdb'

    def add_outputs(self):
        pass

    def run(self):
        """run HebesaetzeKontrolle Tool"""

        parameters = self.par
        projektname = self.par.name.value
        hebesatz = self.par.hebesatz.value
        target_gemeinde = self.par.gemeinde.value
        target_gemeinde_kurz = target_gemeinde.split(" ||")[0]
        basetable_GewSt = self.folders.get_base_table("FGDB_Basisdaten_deutschland.gdb", 'bkg_gemeinden')
        fields = ["GEN", "Hebesatz_GewSt"]
        for key in self.parent_tbx.gemeinden_dict:
            where_clause = '"GEN"' + "='" + key + "'"
            cursor = arcpy.da.UpdateCursor(basetable_GewSt, fields, where_clause)
            for gemeinde in cursor:
                gemeinde[1] = self.parent_tbx.gemeinden_dict[key]
                cursor.updateRow(gemeinde)

        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = mxd.activeDataFrame
        if arcpy.mapping.ListLayers(mxd, projektname, df):
            projekt_layer = arcpy.mapping.ListLayers(mxd, projektname, df)[0]
            if arcpy.mapping.ListLayers(projekt_layer, "Gewerbesteuer"):
                lyr = arcpy.mapping.ListLayers(projekt_layer, "Gewerbesteuer")[0]
                lyr.symbology.reclassify()

            arcpy.RefreshActiveView()
            arcpy.RefreshTOC()





