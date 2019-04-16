# -*- coding: utf-8 -*-

import arcpy, sys

from tools.utils.params import Tool
import tools.utils.layer_einnahmen as lib_einnahmen
from tools.diagrams.diagram_wanderung import Dia_Wanderung_SvB
import tools.analyst.einnahmen.script_Wanderungssalden_schaetzen as ws

class Wanderungssalden2(Tool):

    _param_projectname = 'name'
    _workspace = 'FGDB_Einnahmen.gdb'

    def add_outputs(self):
        self.output.delete_output("SvB_Saldo")

        gemeinde_werte = lib_einnahmen.get_values(["SvB_Saldo"], self.projectname)

        symbology = lib_einnahmen.get_symbology(gemeinde_werte, 1)

        self.output.add_layer(
            groupname = "einnahmen",
            featureclass = "Gemeindebilanzen",
            template_layer = symbology,
            template_folder = "einnahmen",
            name = "SvB-Saldo",
            disable_other = True,
            symbology = {'valueField': "SvB_Saldo"},
            label_replace = {'Einw_Saldo': 'SvB_Saldo'}
        )

        diagram = Dia_Wanderung_SvB(projectname=self.par.name.value)
        self.output.add_diagram(diagram)

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

    def run(self):
        ws.Wanderungssalden_schaetzen(self)
