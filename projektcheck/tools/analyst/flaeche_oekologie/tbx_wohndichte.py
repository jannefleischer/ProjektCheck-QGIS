# -*- coding: utf-8 -*-

import arcpy

from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.analyst.flaeche_oekologie.script_Wohnflaeche import Wohndichte
from tools.utils.constants import Nutzungsart

class TbxWohndichte(Tbx):
    """Toolbox Wohndichte"""

    id_teilflaeche = 1

    @property
    def label(self):
        return u'Wohndichte anzeigen'

    @property
    def Tool(self):
        return Wohndichte

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

        # Teilfläche
        par.teilflaeche = arcpy.Parameter()
        par.teilflaeche.name = u'Teilflaeche'
        par.teilflaeche.displayName = u'Teilfläche'
        par.teilflaeche.parameterType = 'Required'
        par.teilflaeche.direction = 'Input'
        par.teilflaeche.datatype = u'GPString'
        par.teilflaeche.filter.list = []

        # Nicht-Nettofläche
        par.nettoflaeche = arcpy.Parameter()
        par.nettoflaeche.name = u'nettoflaeche'
        par.nettoflaeche.displayName = u'Anteil der Fläche der ausgewählten Teilfläche, welcher kein Nettowohnbauland (= Wohnbaugrundstücke) ist (in Prozent)'
        par.nettoflaeche.parameterType = 'Required'
        par.nettoflaeche.direction = 'Input'
        par.nettoflaeche.datatype = u'Long'
        par.nettoflaeche.filter.type = 'Range'
        par.nettoflaeche.filter.list = [0, 100]
        par.nettoflaeche.value = 15

        return par

    def _updateParameters(self, par):

        if par.name.altered and not par.name.hasBeenValidated:
            teilflaechen = []
            id_teilflaechen = []
            table_teilflaechen = self.folders.get_table("Teilflaechen_Plangebiet", "FGDB_Definition_Projekt.gdb")

            cursor = arcpy.da.SearchCursor(table_teilflaechen, ["Name", "Nutzungsart", "id_teilflaeche"])
            for teilflaeche in cursor:
                if teilflaeche[1] == Nutzungsart.WOHNEN:
                    teilflaechen.append(teilflaeche[0] + " (ID: " + str(teilflaeche[2]) + ")")
                    id_teilflaechen.append(teilflaeche[2])
            par.teilflaeche.filter.list = teilflaechen
            if teilflaechen:
                par.teilflaeche.value = teilflaechen[0]
                self.id_teilflaeche = id_teilflaechen[0]
            else:
                par.name.setErrorMessage(u'Es wurden keine Wohngebiete definiert.')


        if par.teilflaeche.altered and not par.teilflaeche.hasBeenValidated:
            split1 = par.teilflaeche.value.split("ID: ")[1]
            split2 = split1.split(")")[0]
            self.id_teilflaeche = int(split2)



