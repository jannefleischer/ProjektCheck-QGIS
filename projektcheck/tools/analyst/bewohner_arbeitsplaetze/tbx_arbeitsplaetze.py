# -*- coding: utf-8 -*-

from definitions.projektverwaltung.tbx_teilflaechen_verwalten import \
     TbxFlaechendefinition
from utils.params import Tool
from utils.constants import Nutzungsart
from utils.spatial_lib import get_gemeindetyp
from diagrams.bewohner_arbeitsplaetze import (ArbeitsplatzEntwicklung,
                                                       BranchenAnteile)
import pandas as pd
import arcpy


class Arbeitsplaetze(Tool):
    _param_projectname = 'projectname'
    _workspace = 'FGDB_Bewohner_Arbeitsplaetze.gdb'

    def add_outputs(self):

        area, idx = self.parent_tbx.get_selected_area()
        if area['AP_gesamt'] == 0:
            arcpy.AddError(u'Die Detailangaben zu Teilfläche "{}" fehlen!'
                           .format(area['Name']))
            return
        diagram = ArbeitsplatzEntwicklung(
            flaechen_id=area['id_teilflaeche'],
            flaechen_name=area['Name'])
        self.output.add_diagram(diagram)

        diagram = BranchenAnteile(
            flaechen_id=area['id_teilflaeche'],
            flaechen_name=area['Name'])
        self.output.add_diagram(diagram)

    def run(self):
        pass


class TbxArbeitsplaetze(TbxFlaechendefinition):
    _nutzungsart = Nutzungsart.GEWERBE

    @property
    def Tool(self):
        return Arbeitsplaetze

    @property
    def label(self):
        return u'Arbeitsplätze schätzen'

    def set_selected_area(self):
        pass

if __name__ == '__main__':
    t = TbxArbeitsplaetze()
    params = t.getParameterInfo()
    t.set_active_project()
    t.open()
    t.execute()
