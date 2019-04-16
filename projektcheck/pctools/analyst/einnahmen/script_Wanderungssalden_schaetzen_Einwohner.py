# -*- coding: utf-8 -*-

import arcpy, sys

from pctools.utils.params import Tool
import pctools.utils.layer_einnahmen as lib_einnahmen
from pctools.diagrams.diagram_wanderung import Dia_Wanderung_Ew
import pctools.analyst.einnahmen.script_Wanderungssalden_schaetzen as ws


class Wanderungssalden1(Tool):

    _param_projectname = 'name'
    _workspace = 'FGDB_Einnahmen.gdb'

    def add_outputs(self):
        self.output.delete_output("Einw_Saldo")

        gemeinde_werte = lib_einnahmen.get_values(["Einw_Saldo"], self.projectname)

        symbology = lib_einnahmen.get_symbology(gemeinde_werte, 1)

        self.output.add_layer(
            groupname = "einnahmen",
            featureclass = "Gemeindebilanzen",
            template_layer = symbology,
            template_folder = "einnahmen",
            name = "Einwohner-Saldo",
            disable_other = True,
            symbology = {'valueField': "Einw_Saldo"},
            label_replace = {'Einw_Saldo': 'Einw_Saldo'}
        )

        diagram = Dia_Wanderung_Ew(projectname=self.par.name.value)
        self.output.add_diagram(diagram)

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

    def run(self):
        ws.Wanderungssalden_schaetzen(self)
