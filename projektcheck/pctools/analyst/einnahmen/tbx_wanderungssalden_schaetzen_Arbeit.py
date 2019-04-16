# -*- coding: utf-8 -*-

import arcpy

from pctools.utils.params import Tbx
from pctools.utils.encoding import encode
from pctools.utils.constants import Nutzungsart
from pctools.analyst.einnahmen.script_Wanderungssalden_schaetzen_Arbeit import Wanderungssalden2

class TbxWanderungssalden2(Tbx):
    """Toolbox Wanderungssalden für Beschäftigte"""

    @property
    def label(self):
        return u'Wanderungssalden schätzen (Beschäftigte)'

    @property
    def Tool(self):
        return Wanderungssalden2

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

##        where = 'Nutzungsart = {}'.format(Nutzungsart.GEWERBE)
##
##        rows = self.query_table('Teilflaechen_Plangebiet',
##                                ['Nutzungsart'],
##                                workspace='FGDB_Definition_Projekt.gdb',
##                                where=where)
##
##        if not rows:
##            par.name.setErrorMessage(u'In diesem Projekt sind keine Gewerbeflächen definiert!')


if __name__ == '__main__':
    t = TbxWanderungssalden()
    t.getParameterInfo()
    t.open()
