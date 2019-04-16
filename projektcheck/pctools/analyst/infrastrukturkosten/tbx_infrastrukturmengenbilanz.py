# -*- coding: utf-8 -*-
import sys
import datetime
import arcpy
from pctools.utils.params import Tbx, Tool
from pctools.utils.encoding import encode
import pandas as pd
import numpy as np
from pctools.diagrams.infrastruktur import MassnahmenKostenDiagramm, NetzlaengenDiagramm


class InfrastrukturmengenBilanz(Tool):
    _param_projectname = 'projectname'
    _workspace = 'FGDB_Kosten.gdb'

    def add_outputs(self):

        kosten_diagram = MassnahmenKostenDiagramm()

        netz_diagram = NetzlaengenDiagramm()

        self.output.add_diagram(kosten_diagram, netz_diagram)

    def run(self):
        pass


class TbxInfrastrukturmengenBilanz(Tbx):
    """Toolbox Projekt loeschen"""
    @property
    def label(self):
        return u'Schritt ?: Infrastrukturmengen bilanzieren'

    @property
    def Tool(self):
        return InfrastrukturmengenBilanz

    def _getParameterInfo(self):

        # Bestehendes_Projekt_auswählen
        p = self.add_parameter('projectname')
        p.name = encode('Projekt')
        p.displayName = encode('Projekt')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = 'GPString'
        p.filter.list = []

        return self.par

    def _updateParameters(self, params):
        pass

if __name__ == "__main__":
    t = TbxInfrastrukturmengenBilanz()
    t.getParameterInfo()
    t.par.projectname.value = t.config.active_project
    t.execute()
