# -*- coding: utf-8 -*-

import arcpy

from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.analyst.flaeche_oekologie.script_Integrationsgrad import Integrationsgrad_berechnen
from tools.analyst.flaeche_oekologie.script_Integrationsgrad import Integrationsgrad_loeschen
from tools.analyst.flaeche_oekologie.script_Integrationsgrad import Integrationsgrad_zeichnen
from tools.utils.constants import Nutzungsart
from tools.utils.output import Output

class TbxIntegrationsgrad_berechnen(Tbx):
    """Toolbox Integrationsgrad_berechnen"""

    @property
    def label(self):
        return u' Integrationsgrad berechnen'

    @property
    def Tool(self):
        return Integrationsgrad_berechnen

    def _getParameterInfo(self):

        par = self.par

        # Projektname
        par.name = arcpy.Parameter()
        par.name.name = u'Projektname'
        par.name.displayName = u'Projektname'
        par.name.parameterType = 'Required'
        par.name.direction = 'Input'
        par.name.datatype = u'GPString'
        par.name.filter.list = []


        return par

    def _updateParameters(self, params):
        par = self.par

class TbxIntegrationsgrad_zeichnen(Tbx):
    """Toolbox TbxIntegrationsgrad_zeichnen"""

    @property
    def label(self):
        return u' Integrationsgrad zeichnen'

    @property
    def Tool(self):
        return Integrationsgrad_zeichnen

    def _getParameterInfo(self):

        par = self.par

        # Projektname
        par.name = arcpy.Parameter()
        par.name.name = u'Projektname'
        par.name.displayName = u'Projektname'
        par.name.parameterType = 'Required'
        par.name.direction = 'Input'
        par.name.datatype = u'GPString'
        par.name.filter.list = []

        return par

    def _updateParameters(self, params):
        par = self.par

    def grenzlinie_eintragen(self, polyline):

        table = self.folders.get_table("Grenze_Siedlungskoerper", "FGDB_Flaeche_und_Oekologie.gdb")
        cursor = arcpy.da.InsertCursor(table, ['SHAPE@'])
        cursor.insertRow([polyline])


class TbxIntegrationsgrad_loeschen(Tbx):
    """Toolbox TbxIntegrationsgrad_loeschen"""

    @property
    def label(self):
        return u' Integrationsgrad löschen'

    @property
    def Tool(self):
        return Integrationsgrad_loeschen

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
        par = self.par
