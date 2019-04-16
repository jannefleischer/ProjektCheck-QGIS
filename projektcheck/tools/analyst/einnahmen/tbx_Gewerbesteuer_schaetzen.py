# -*- coding: utf-8 -*-

import arcpy
from tools.utils.constants import Nutzungsart
from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.analyst.einnahmen.script_Gewerbesteuer_schaetzen import Gewerbesteuer

class TbxGewerbesteuer(Tbx):
    """Toolbox Gewerbesteuer"""

    @property
    def label(self):
        return u'Gewerbesteuer (netto)'

    @property
    def Tool(self):
        return Gewerbesteuer

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

        cursor = self.query_table(table_name = 'Chronik_Nutzung',
                                columns = ['Arbeitsschritt', 'Letzte_Nutzung'],
                                workspace='FGDB_Einnahmen.gdb')
        for row in cursor:
            if row[0] == u"Wanderung Beschaeftigte" and row[1] is None:
                par.name.setErrorMessage(u'Es wurden noch keine Wanderungssalden für Beschäftigte berechnet!')

        where = 'Nutzungsart = {} or Nutzungsart = {}'.format(Nutzungsart.WOHNEN, Nutzungsart.EINZELHANDEL)
        if par.changed('name'):
            where = 'Nutzungsart = {} or Nutzungsart = {}'.format(Nutzungsart.WOHNEN, Nutzungsart.EINZELHANDEL)
            rows = self.query_table('Teilflaechen_Plangebiet',
                                    ['Nutzungsart'],
                                    workspace='FGDB_Definition_Projekt.gdb',
                                    where=where)
            if not rows:
                par.name.setErrorMessage(u'In diesem Projekt sind keine Gewerbe- oder Einzelhandelsflächen definiert!')
                par.gemeinde.enabled = False
                par.gemeinde.filter.list = []
                par.gemeinde.value = (u'Projekt enthält keine Flächen mit der '
                                      u'benötigten Nutzungsart')

