# -*- coding: utf-8 -*-

import arcpy

from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.analyst.flaeche_oekologie.script_UZVR import UZVR
from tools.utils.constants import Nutzungsart

class TbxUZVR(Tbx):
    """Toolbox UZVR"""

    @property
    def label(self):
        return u'UZVR bestimmen'

    @property
    def Tool(self):
        return UZVR

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

