# -*- coding: utf-8 -*-

import arcpy
from tools.utils.constants import Nutzungsart
from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.analyst.einnahmen.script_Einkommensteuer import Einkommensteuer

class TbxEinkommensteuer(Tbx):
    """Toolbox Einkommensteuer für Einnahmen"""

    @property
    def label(self):
        return u'Einkommensteuer (Kommunalanteil)'

    @property
    def Tool(self):
        return Einkommensteuer

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

        return par

    def _updateMessages(self, params):

        par = self.par

        where = 'Nutzungsart = {}'.format(Nutzungsart.WOHNEN)
        rows = self.query_table('Teilflaechen_Plangebiet',
                                ['Nutzungsart'],
                                workspace='FGDB_Definition_Projekt.gdb',
                                where=where)

        if not rows:
            par.name.setErrorMessage(u'In diesem Projekt sind keine Wohnflächen definiert!')

        cursor = self.query_table(table_name = 'Chronik_Nutzung',
                                columns = ['Arbeitsschritt', 'Letzte_Nutzung'],
                                workspace='FGDB_Einnahmen.gdb')
        for row in cursor:
            if row[0] == "Wanderung Einwohner" and row[1] is None:
                par.name.setErrorMessage(u'Es wurden noch keine Wanderungssalden für Einwohner berechnet!')
