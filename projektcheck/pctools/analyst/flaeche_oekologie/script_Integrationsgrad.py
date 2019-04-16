# -*- coding: utf-8 -*-

import os
import sys

import arcpy
from pctools.utils.params import Tool
from pctools.diagrams.diagram_oekologie import Dia_Integrationsgrad

class Integrationsgrad_berechnen(Tool):
    """Integrationsgrad_berechnen"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Flaeche_und_Oekologie.gdb'

    aussengrenze = 0.0
    gemeinsame_grenze = 0.0

    def add_outputs(self):
        self.output.add_layer(groupname = "oekologie", featureclass = "Grenze_Siedlungskoerper", template_layer = "Grenze_Siedlungskoerper", template_folder="oekologie",  zoom=False, disable_other = True)

        diagram = Dia_Integrationsgrad(projectname=self.par.name.value)
        self.output.add_diagram(diagram)
        self.output.show_layers()

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

    def run(self):
        params = self.par
        projekt = self.projectname
        table_grenzlinie = self.folders.get_table("Grenze_Siedlungskoerper", "FGDB_Flaeche_und_Oekologie.gdb")
        cursor = arcpy.da.SearchCursor(table_grenzlinie, ["SHAPE_Length"])
        self.gemeinsame_grenze = 0.0
        for row in cursor:
            self.gemeinsame_grenze += row[0]

        teilflaechen = self.folders.get_table("Teilflaechen_Plangebiet", "FGDB_Definition_Projekt.gdb")
        path_aussengrenze = os.path.join(self.folders.get_db("FGDB_Flaeche_und_Oekologie.gdb"),"Aussengrenze_Plangebiet")
        if arcpy.Exists(path_aussengrenze):
            arcpy.Delete_management(path_aussengrenze)
        arcpy.Dissolve_management(teilflaechen, path_aussengrenze)
        cursor = arcpy.da.SearchCursor(path_aussengrenze, ["SHAPE_Length"])
        self.aussengrenze = 0.0
        for row in cursor:
            self.aussengrenze += row[0]
        arcpy.Delete_management(path_aussengrenze)
        current_mxd = arcpy.mapping.MapDocument("CURRENT")
        current_dataframe = current_mxd.activeDataFrame
        aussengrenze_layer = arcpy.mapping.ListLayers(
            current_mxd,
            "Aussengrenze_Plangebiet",
            current_dataframe)[0]
        arcpy.mapping.RemoveLayer(current_dataframe, aussengrenze_layer)

        table_integrationsgrad = self.folders.get_table("Integrationsgrad", "FGDB_Flaeche_und_Oekologie.gdb")
        cursor = arcpy.da.UpdateCursor(table_integrationsgrad, ["*"])
        for row in cursor:
            cursor.deleteRow()

        geteilte_grenze = round(self.gemeinsame_grenze / self.aussengrenze, 3) * 100
        if geteilte_grenze > 100.0:
            geteilte_grenze = 100.0
        neue_grenze = 100.0 - geteilte_grenze
        column_values = {"Grenze": [u"... an bestehende Siedlungen angrenzt", u"... nicht an bestehende Siedlungen angrenzt"],
                                "Umfang": [geteilte_grenze, neue_grenze]}
        self.parent_tbx.insert_rows_in_table("Integrationsgrad", column_values)

class Integrationsgrad_loeschen(Tool):
    """Integrationsgrad_loeschen"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Flaeche_und_Oekologie.gdb'

    def add_outputs(self):
        pass

    def run(self):
        params = self.par
        projekt = self.projectname

        table_grenzlinie = self.folders.get_table("Grenze_Siedlungskoerper", "FGDB_Flaeche_und_Oekologie.gdb")

        cursor = arcpy.da.UpdateCursor(table_grenzlinie, ["*"])
        for row in cursor:
            cursor.deleteRow()

        arcpy.RefreshActiveView()
        arcpy.RefreshTOC()

class Integrationsgrad_zeichnen(Tool):
    """Integrationsgradzeichnen"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Flaeche_und_Oekologie.gdb'

    def add_outputs(self):
        self.output.add_layer(groupname = "oekologie", featureclass = "Grenze_Siedlungskoerper", template_layer = "Grenze_Siedlungskoerper", template_folder="oekologie",  zoom=False, disable_other = True)
        self.output.show_layers()
        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

    def run(self):
        params = self.par


