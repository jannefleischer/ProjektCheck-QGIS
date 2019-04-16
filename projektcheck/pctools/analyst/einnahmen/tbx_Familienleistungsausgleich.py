# -*- coding: utf-8 -*-

import arcpy
from pctools.utils.constants import Nutzungsart
from pctools.utils.params import Tbx
from pctools.utils.encoding import encode
from pctools.analyst.einnahmen.script_Familienleistungsausgleich import Familienleistungsausgleich
import pctools.utils.chronik as c

class TbxFLA(Tbx):
    """Toolbox Familienleistungsausgleich"""

    @property
    def label(self):
        return u'Familienleistungsausgleich'

    @property
    def Tool(self):
        return Familienleistungsausgleich

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

    def _updateParameters(self, params):
        return

    def _updateMessages(self, params):
        par = self.par

        where = 'Nutzungsart = {}'.format(Nutzungsart.WOHNEN)

        rows = self.query_table('Teilflaechen_Plangebiet',
                                ['Nutzungsart'],
                                workspace='FGDB_Definition_Projekt.gdb',
                                where=where)

        if not rows:
            par.name.setErrorMessage(u'In diesem Projekt sind keine Wohnflächen definiert!')

        table = self.folders.get_table(tablename='Chronik_Nutzung',workspace="FGDB_Einnahmen.gdb",project=par.name.value)

        if c.compare_chronicle("Einkommensteuer", "Wanderung Einwohner", table) == False:
            par.name.setErrorMessage(u'Es muss zuerst die Einkommensteuer (erneut) berechnet werden!')
