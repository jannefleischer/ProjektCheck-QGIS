# -*- coding: utf-8 -*-

import arcpy

from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.utils.constants import Nutzungsart
from tools.analyst.einnahmen.script_Wanderungssalden_schaetzen_Einwohner import Wanderungssalden1


class TbxWanderungssalden1(Tbx):
    """Toolbox Wanderungssalden für Einwohner"""

    @property
    def label(self):
        return u'Wanderungssalden schätzen (Einwohner)'

    @property
    def Tool(self):
        return Wanderungssalden1

    def _getParameterInfo(self):

        par = self.par

        # Projektname
        par.name = arcpy.Parameter()
        par.name.name = u'Projektname'
        par.name.displayName = u'Projekt'
        par.name.parameterType = 'Required'
        par.name.direction = 'Input'
        par.name.datatype = u'GPString'
        par.name.filter.list = []

        par.aktualisieren = arcpy.Parameter()
        par.aktualisieren.name = u'aktualisieren'
        par.aktualisieren.displayName = u'Neuberechnung der Wanderungssalden erzwingen'
        par.aktualisieren.parameterType = 'Optional'
        par.aktualisieren.datatype = u'GPBoolean'

        return par

    def _updateMessages(self, params):
        par = self.par

##        where = 'Nutzungsart = {}'.format(
##            Nutzungsart.WOHNEN)
##
##        rows = self.query_table('Teilflaechen_Plangebiet',
##                                ['Nutzungsart'],
##                                workspace='FGDB_Definition_Projekt.gdb',
##                                where=where)
##
##        if not rows:
##            par.name.setErrorMessage(u'In diesem Projekt sind keine Wohnflächen definiert!')

if __name__ == '__main__':
    t = TbxWanderungssalden1()
    t.getParameterInfo()
    t.set_active_project()
    t.show_outputs()
    t.open()
