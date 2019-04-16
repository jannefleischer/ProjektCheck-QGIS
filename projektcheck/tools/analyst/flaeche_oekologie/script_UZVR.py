# -*- coding: utf-8 -*-

import os
import sys

import arcpy
from tools.utils.params import Tool

class UZVR(Tool):
    """UZVR"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Flaeche_und_Oekologie.gdb'

    def add_outputs(self):
        pass

    def run(self):
        params = self.par
        projekt = self.projectname

        path_teilflaechen = self.folders.get_table('Teilflaechen_Plangebiet', "FGDB_Definition_Projekt.gdb", projekt)
        path_teilflaechen_dissolved = self.folders.get_table('Teilflaechen_Plangebiet_dissolved', "FGDB_Flaeche_und_Oekologie.gdb", projekt)
        arcpy.Dissolve_management(path_teilflaechen, path_teilflaechen_dissolved)

        arcpy.AddField_management(path_teilflaechen_dissolved, "laenge", "DOUBLE")
        arcpy.CalculateField_management(path_teilflaechen_dissolved,"laenge","!shape.geodesicLength@METERS!","PYTHON_9.3","#")

        gesamt_laenge_meter = 0
        fields = ["laenge"]
        cursor = arcpy.da.SearchCursor(path_teilflaechen_dissolved, fields)
        for row in cursor:
            gesamt_laenge_meter += row[0]


