# -*- coding: utf-8 -*-

import arcpy
from tools.utils.constants import Nutzungsart
from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.analyst.einnahmen.script_Gesamtsumme import Gesamtsumme
import tools.utils.chronik as c

class TbxGesamtsumme(Tbx):
    """Toolbox Gesamtsumme der Einnahmen """

    @property
    def label(self):
        return u'Gesamtsumme der Mehr- und Mindereinnahmen der Gemeinden'

    @property
    def Tool(self):
        return Gesamtsumme

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

        par.summe = arcpy.Parameter()
        par.summe.name = u'Bestandteile'
        par.summe.displayName = u'Bestandteile der Gesamtsumme'
        par.summe.parameterType = 'Required'
        par.summe.direction = 'Input'
        par.summe.datatype = u'GPString'
        par.summe.value = "Alles"
        par.summe.enabled = False

        return par

    def _updateParameters(self, params):
        par = self.par

        wohnen_vorhanden = False
        gewerbe_oder_einzelhandel_vorhanden = False

        cursor = self.query_table('Teilflaechen_Plangebiet',
                                ['Nutzungsart'],
                                workspace='FGDB_Definition_Projekt.gdb')

        for row in cursor:
            if row[0] == Nutzungsart.GEWERBE or row[0] == Nutzungsart.EINZELHANDEL:
                gewerbe_oder_einzelhandel_vorhanden = True
            if row[0] == Nutzungsart.WOHNEN:
                wohnen_vorhanden = True

        if wohnen_vorhanden and gewerbe_oder_einzelhandel_vorhanden:
            bestandteile = "Grundsteuer + Einkommensteuer + Familienleistungsausgleich + Gewerbesteuer + Umsatzsteuer"
            self.spalten = ["Summe_Einnahmenbilanz", "GrSt", "ESt", "FamLeistAusgl", "GewSt", "USt"]
        elif wohnen_vorhanden and not gewerbe_oder_einzelhandel_vorhanden:
            bestandteile = "Grundsteuer + Einkommensteuer + Familienleistungsausgleich"
            self.spalten = ["Summe_Einnahmenbilanz", "GrSt", "ESt", "FamLeistAusgl"]
        elif not wohnen_vorhanden and gewerbe_oder_einzelhandel_vorhanden:
            bestandteile = "Grundsteuer + Gewerbesteuer + Umsatzsteuer"
            self.spalten = ["Summe_Einnahmenbilanz", "GrSt", "GewSt", "USt"]

        par.summe.value = bestandteile


    def _updateMessages(self, params):

        par = self.par

        wohnen_vorhanden = False
        gewerbe_oder_einzelhandel_vorhanden = False
        missing = []

        cursor = self.query_table('Teilflaechen_Plangebiet',
                                ['Nutzungsart'],
                                workspace='FGDB_Definition_Projekt.gdb')

        for row in cursor:
            if row[0] == Nutzungsart.GEWERBE or row[0] == Nutzungsart.EINZELHANDEL:
                gewerbe_oder_einzelhandel_vorhanden = True
            if row[0] == Nutzungsart.WOHNEN:
                wohnen_vorhanden = True

        table = self.folders.get_table(tablename='Chronik_Nutzung',workspace="FGDB_Einnahmen.gdb",project=par.name.value)
        cursor = self.query_table(table_name = 'Chronik_Nutzung',
                                columns = ['Arbeitsschritt', 'Letzte_Nutzung'],
                                workspace='FGDB_Einnahmen.gdb')

        for row in cursor:
            if row[0] == "Grundsteuer" and row[1] is None:
                missing.append(u"Grundsteuer")
            if wohnen_vorhanden and row[0] == "Einkommensteuer" and (row[1] is None or c.compare_chronicle("Einkommensteuer", "Wanderung Einwohner", table) == False):
                missing.append(u"Einkommensteuer")
            if wohnen_vorhanden and row[0] == "Familienleistungsausgleich" and (row[1] is None or c.compare_chronicle("Einkommensteuer", "Wanderung Einwohner", table) == False):
                missing.append(u"Familienleistungsausgleich")
            if gewerbe_oder_einzelhandel_vorhanden and row[0] == "Gewerbesteuer" and (row[1] is None or c.compare_chronicle("Gewerbesteuer", "Wanderung Beschaeftigte", table) == False):
                missing.append(u"Gewerbesteuer")
            if gewerbe_oder_einzelhandel_vorhanden and row[0] == "Umsatzsteuer" and (row[1] is None or c.compare_chronicle("Umsatzsteuer", "Gewerbesteuer", table) == False):
                missing.append(u"Umsatzsteuer")

        if missing:
            missing_nr = 1
            missing_msg = u"Zur Darstellung der Gesamtsumme müssen zunächst noch folgende Bilanzen (erneut) berechnet werden: "
            for bilanz in missing:
                missing_msg += bilanz
                if missing_nr != len(missing):
                    missing_msg += ", "
                missing_nr += 1
            par.name.setErrorMessage(missing_msg)
