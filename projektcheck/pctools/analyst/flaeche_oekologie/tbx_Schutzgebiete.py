# -*- coding: utf-8 -*-

import arcpy

from pctools.utils.params import Tbx
from pctools.analyst.flaeche_oekologie.script_Schutzgebiete import Schutzgebiete
from pctools.utils.params import Tool

class TbxSchutzgebiete(Tbx):
    """Toolbox Ueberschneidungen"""

    @property
    def label(self):
        return u'Details aufrufen'

    @property
    def Tool(self):
        return Schutzgebiete

    def _getParameterInfo(self):

        par = self.par

        # Projekt_auswählen
        par.name = arcpy.Parameter()
        par.name.name = u'Projektname'
        par.name.displayName = u'Projekt'
        par.name.parameterType = 'Required'
        par.name.direction = 'Input'
        par.name.datatype = u'GPString'
        par.name.filter.list = []


        return par

