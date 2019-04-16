# -*- coding: utf-8 -*-

import arcpy

from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.analyst.einnahmen.script_Umsatzsteuer import Umsatzsteuer
import tools.utils.chronik as c

class TbxUmsatzsteuer(Tbx):
    """Toolbox Umsatzsteuer für Einnahmen"""

    @property
    def label(self):
        return u'Umsatzsteuer (Kommunalanteil)'

    @property
    def Tool(self):
        return Umsatzsteuer

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
        table = self.folders.get_table(tablename='Chronik_Nutzung',workspace="FGDB_Einnahmen.gdb",project=par.name.value)

        cursor = self.query_table(table_name = 'Chronik_Nutzung',
                                columns = ['Arbeitsschritt', 'Letzte_Nutzung'],
                                workspace='FGDB_Einnahmen.gdb')
        for row in cursor:
            if row[0] == u"Wanderung Beschaeftigte" and row[1] is None:
                par.name.setErrorMessage(u'Es wurden noch keine Wanderungssalden für Beschäftigte berechnet!')
            elif row[0] == u"Gewerbesteuer" and c.compare_chronicle("Gewerbesteuer", "Wanderung Beschaeftigte", table) == False:
                par.name.setErrorMessage(u'Es muss zunächst die Gewerbesteuer (erneut berechnet) werden!')

        vergleich = c.compare_chronicle(u"Gewerbesteuer", u"Wanderung Beschaeftigte", table)
        if not vergleich:
            par.name.setErrorMessage(u'Die Gewerbesteuer muss zuerst (erneut) berechnet werden!')
