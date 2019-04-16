# -*- coding: utf-8 -*-

import arcpy

from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.analyst.flaeche_oekologie.script_Wohnflaeche import Wohnflaechendichte
from tools.utils.constants import Nutzungsart

class TbxWohnflaechendichte(Tbx):
    """Toolbox Wohnflaechendichte"""

    id_teilflaeche = 1

    @property
    def label(self):
        return u'Wohnflächendichte anzeigen'

    @property
    def Tool(self):
        return Wohnflaechendichte

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

        heading = encode("Durchschnittliche Wohnfläche nach Gebäudetyp")

        # Durchschnittliche_�berbaute_Fl�che_je_Wohneinheit_in_Ein-_und_Zweifamilienh�usern__qm_
        par.flaeche_efh = arcpy.Parameter()
        par.flaeche_efh.name = u'Durchschnittliche_\xfcberbaute_Fl\xe4che_je_Wohneinheit_in_Ein-_und_Zweifamilienh\xe4usern__qm_'
        par.flaeche_efh.displayName = u'Durchschnittliche Wohnfläche je Wohneinheit in Ein- und Zweifamilienh\xe4usern (qm)'
        par.flaeche_efh.parameterType = 'Required'
        par.flaeche_efh.direction = 'Input'
        par.flaeche_efh.datatype = u'Long'
        par.flaeche_efh.value = 50
        par.flaeche_efh.filter.type = 'Range'
        par.flaeche_efh.filter.list = [0, 200]
        par.flaeche_efh.category = heading

        # Durchschnittliche_�berbaute_Fl�che_je_Wohneinheit_in_Doppelh�usern__qm_
        par.flaeche_dh = arcpy.Parameter()
        par.flaeche_dh.name = u'Durchschnittliche_\xfcberbaute_Fl\xe4che_je_Wohneinheit_in_Doppelh\xe4usern__qm_'
        par.flaeche_dh.displayName = u'Durchschnittliche Wohnfläche je Wohneinheit in Doppelh\xe4usern (qm)'
        par.flaeche_dh.parameterType = 'Required'
        par.flaeche_dh.direction = 'Input'
        par.flaeche_dh.datatype = u'Long'
        par.flaeche_dh.value = 50
        par.flaeche_dh.filter.type = 'Range'
        par.flaeche_dh.filter.list = [0, 200]
        par.flaeche_dh.category = heading

        # Durchschnittliche_�berbaute_Fl�che_je_Wohneinheit_in_Reihenh�usern__qm_
        par.flaeche_rh = arcpy.Parameter()
        par.flaeche_rh.name = u'Durchschnittliche_\xfcberbaute_Fl\xe4che_je_Wohneinheit_in_Reihenh\xe4usern__qm_'
        par.flaeche_rh.displayName = u'Durchschnittliche Wohnfläche je Wohneinheit in Reihenh\xe4usern (qm)'
        par.flaeche_rh.parameterType = 'Required'
        par.flaeche_rh.direction = 'Input'
        par.flaeche_rh.datatype = u'Long'
        par.flaeche_rh.value = 50
        par.flaeche_rh.filter.type = 'Range'
        par.flaeche_rh.filter.list = [0, 200]
        par.flaeche_rh.category = heading

        # Durchschnittliche_�berbaute_Fl�che_je_Wohneinheit_in_Mehrfamilienh�usern__qm_
        par.flaeche_mfh = arcpy.Parameter()
        par.flaeche_mfh.name = u'Durchschnittliche_\xfcberbaute_Fl\xe4che_je_Wohneinheit_in_Mehrfamilienh\xe4usern__qm_'
        par.flaeche_mfh.displayName = u'Durchschnittliche Wohnfläche je Wohneinheit in Mehrfamilienh\xe4usern (qm)'
        par.flaeche_mfh.parameterType = 'Required'
        par.flaeche_mfh.direction = 'Input'
        par.flaeche_mfh.datatype = u'Long'
        par.flaeche_mfh.value = 50
        par.flaeche_mfh.filter.type = 'Range'
        par.flaeche_mfh.filter.list = [0, 200]
        par.flaeche_mfh.category = heading

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

            path_vorgabewerte = self.folders.get_base_table("FGDB_Definition_Projekt_Tool.gdb", "Wohnen_Gebaeudetypen")
            cursor = arcpy.da.SearchCursor(path_vorgabewerte, ["IDGebaeudetyp", "Wohnfl_m2_pro_WE"])
            for row in cursor:
                if row[0] == 1:
                    par.flaeche_efh.value = row[1]
                elif row[0] == 2:
                    par.flaeche_dh.value = row[1]
                elif row[0] == 3:
                    par.flaeche_rh.value = row[1]
                elif row[0] == 4:
                    par.flaeche_mfh.value = row[1]

        if par.teilflaeche.altered and not par.teilflaeche.hasBeenValidated:
            split1 = par.teilflaeche.value.split("ID: ")[1]
            split2 = split1.split(")")[0]
            self.id_teilflaeche = int(split2)




if __name__ == "__main__":
    t = TbxWohnflaechendichte()
    t.getParameterInfo()
    t.set_active_project()
    t.open()
    t.show_outputs()
    t.execute()
