# -*- coding: utf-8 -*-

import arcpy

from pctools.utils.params import Tbx
from pctools.utils.encoding import encode
from pctools.analyst.einnahmen.script_Gewerbesteuer_kontrollieren import HebesaetzeKontrolle
from pctools.utils.constants import Nutzungsart

class TbxKontrolleGewerbesteuer(Tbx):
    """Toolbox Gewerbesteuerhebesaetze bearbeiten"""

    gemeinden_dict = {}
    gemeinden_list = []

    @property
    def label(self):
        return u'Hebesätze für die Gewerbesteuer kontrollieren'

    @property
    def Tool(self):
        return HebesaetzeKontrolle

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

        par.gemeinde = arcpy.Parameter()
        par.gemeinde.name = u'Gemeinde'
        par.gemeinde.displayName = u'Gemeinden'
        par.gemeinde.parameterType = 'Required'
        par.gemeinde.direction = 'Input'
        par.gemeinde.datatype = u'GPString'
        par.gemeinde.filter.list = []

        par.hebesatz = arcpy.Parameter()
        par.hebesatz.name = u'Hebesatz'
        par.hebesatz.displayName = u'Hebesatz für die Gewerbesteuer (von-Hundert-Satz)'
        par.hebesatz.parameterType = 'Required'
        par.hebesatz.direction = 'Input'
        par.hebesatz.datatype = u'GPLong'
        par.hebesatz.filter.type = 'Range'
        par.hebesatz.filter.list = [100, 600]
        par.hebesatz.value = 250

        return par

    def _updateParameters(self, params):
        par = self.par

        if par.changed('name'):
            where = 'Nutzungsart = {} or Nutzungsart = {}'.format(Nutzungsart.WOHNEN, Nutzungsart.EINZELHANDEL)
            rows = self.query_table('Teilflaechen_Plangebiet',
                                    ['Nutzungsart'],
                                    workspace='FGDB_Definition_Projekt.gdb',
                                    where=where)
            if not rows:
                par.gemeinde.enabled = False
                par.gemeinde.filter.list = []
                par.gemeinde.value = (u'Projekt enthält keine Flächen mit der '
                                      u'benötigten Nutzungsart')
            else:
                par.gemeinde.enabled = True
                fields = ["GEN"]
                rows_gemeindebilanz = self.query_table('Gemeindebilanzen', fields,
                                        workspace='FGDB_Einnahmen.gdb')
                for gemeinde in rows_gemeindebilanz:
                    where = '"GEN"' + "='" + gemeinde[0] + "'"
                    fields2 = ["GEN", "Hebesatz_GewSt"]
                    rows_bkg_gemeinden = self.query_table(table_name = 'bkg_gemeinden', columns = fields2,
                                    workspace='FGDB_Basisdaten_deutschland.gdb',
                                    where = where, is_base_table = True)
                    for gem_name, hebesteuer in rows_bkg_gemeinden:
                        self.gemeinden_dict[gem_name] = hebesteuer
                for key in self.gemeinden_dict:
                    self.gemeinden_list.append(u"{} || Hebesatz: {}".format(key, self.gemeinden_dict[key]))
                par.gemeinde.filter.list = sorted(self.gemeinden_list)
                par.gemeinde.value = sorted(self.gemeinden_list)[0]

        if par.changed('gemeinde'):
            target_gemeinde = self.par.gemeinde.value
            target_gemeinde_kurz = target_gemeinde.split(" ||")[0]
            par.hebesatz.value = self.gemeinden_dict[target_gemeinde_kurz]

        if par.changed('hebesatz'):
            target_gemeinde = self.par.gemeinde.value
            target_gemeinde_kurz = target_gemeinde.split(" ||")[0]
            self.gemeinden_dict[target_gemeinde_kurz] = self.par.hebesatz.value

            self.gemeinden_list = []
            for key in self.gemeinden_dict:
                self.gemeinden_list.append(u"{} || Hebesatz: {}".format(key, self.gemeinden_dict[key]))
            par.gemeinde.filter.list = sorted(self.gemeinden_list)
            par.gemeinde.value = u"{} || Hebesatz: {}".format(target_gemeinde_kurz, self.gemeinden_dict[target_gemeinde_kurz])


    def _updateMessages(self, params):
        par = self.par

        cursor = self.query_table(table_name = 'Chronik_Nutzung',
                                columns = ['Arbeitsschritt', 'Letzte_Nutzung'],
                                workspace='FGDB_Einnahmen.gdb')
        for row in cursor:
            if row[0] == u"Wanderung Beschaeftigte" and row[1] is None:
                par.name.setErrorMessage(u'Es wurden noch keine Wanderungssalden für Beschäftigte berechnet!')

        where = 'Nutzungsart = {} or Nutzungsart = {}'.format(Nutzungsart.WOHNEN, Nutzungsart.EINZELHANDEL)
        rows = self.query_table('Teilflaechen_Plangebiet',
                                ['Nutzungsart'],
                                workspace='FGDB_Definition_Projekt.gdb',
                                where=where)
        if not rows:
            par.name.setErrorMessage(u'In diesem Projekt sind keine Gewerbe- oder Einzelhandelsflächen definiert!')
