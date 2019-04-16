# -*- coding: utf-8 -*-

import arcpy
import os
from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.utils.constants import Nutzungsart
from tools.analyst.einnahmen.script_Wanderungssalden_bearbeiten import Salden_bearbeiten


class TbxSaldenbearbeiten(Tbx):
    """ superclass for wanderungssalden einwohner/gewerbe"""
    _nutzungsart = None
    _saldo_field = None

    gemeinden_dict = {}
    gemeinden_dict_initial = {}
    gemeinden_list = []

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

        par.saldo = arcpy.Parameter()
        par.saldo.name = u'Saldo'
        par.saldo.displayName = u'Neuer Saldo'
        par.saldo.parameterType = 'Required'
        par.saldo.direction = 'Input'
        par.saldo.datatype = u'GPDouble'

        par.summe = arcpy.Parameter()
        par.summe.name = u'Summe'
        par.summe.displayName = u' Gesamtsumme der Wanderungssalden'
        par.summe.parameterType = 'Required'
        par.summe.datatype = u'GPLong'
        par.summe.enabled = False

        par.kontrolle = arcpy.Parameter()
        par.kontrolle.name = u'kontrolle'
        par.kontrolle.displayName = u'Wanderungssalden so aktualisieren, dass die Gesamtsumme 0 beträgt'
        par.kontrolle.parameterType = 'Optional'
        par.kontrolle.datatype = u'GPBoolean'



        return par

    def _updateParameters(self, params):
        par = self.par
        path_gemeindebilanzen = self.folders.get_table("Gemeindebilanzen", 'FGDB_Einnahmen.gdb')

        if par.changed('name'):
            if self._nutzungsart == Nutzungsart.WOHNEN:
                where = 'Nutzungsart = {}'.format(Nutzungsart.WOHNEN)
            elif self._nutzungsart == Nutzungsart.GEWERBE:
                where = 'Nutzungsart = {} OR Nutzungsart = {}'.format(Nutzungsart.GEWERBE, Nutzungsart.EINZELHANDEL)

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

                self.gemeinden_list = []
                fields = ["GEN", self._saldo_field]
                rows = self.query_table('Gemeindebilanzen', fields, workspace='FGDB_Einnahmen.gdb')
                for gem_name, saldo in rows:
                    self.gemeinden_dict[gem_name] = saldo
                for key in self.gemeinden_dict:
                    self.gemeinden_list.append(u"{} || Saldo: {}".format(key, self.gemeinden_dict[key]))
                gemeinden_sorted = sorted(self.gemeinden_list)

                fields = ["Kategorie", "Anzahl"]
                where = ' NOT "Kategorie"' + "='" + 'Projektgemeinde/Region' + "'"
                rows = self.query_table(self._table, fields, workspace='FGDB_Einnahmen.gdb', where = where)
                for kategorie, anzahl in rows:
                    self.gemeinden_dict[kategorie] = -anzahl
                    gemeinden_sorted.append(u"{} || Saldo: {}".format(kategorie, -anzahl))
                self.gemeinden_dict_initial = self.gemeinden_dict
                par.gemeinde.filter.list = gemeinden_sorted
                par.gemeinde.value = gemeinden_sorted[0]

                summe = 0
                for key in self.gemeinden_dict:
                    summe += self.gemeinden_dict[key]
                par.summe.value = summe

        if par.changed('gemeinde'):
            target_gemeinde = par.gemeinde.value
            target_gemeinde_kurz = target_gemeinde.split(" ||")[0]
            par.saldo.value = self.gemeinden_dict[target_gemeinde_kurz]

        if par.changed('saldo'):
            target_gemeinde = par.gemeinde.value
            target_gemeinde_kurz = target_gemeinde.split(" ||")[0]
            self.gemeinden_dict[target_gemeinde_kurz] = par.saldo.value
            summe = 0
            for key in self.gemeinden_dict:
                summe += self.gemeinden_dict[key]
            par.summe.value = summe

            self.gemeinden_list = []
            for key in self.gemeinden_dict:
                self.gemeinden_list.append(u"{} || Saldo: {}".format(key, self.gemeinden_dict[key]))
            gemeinden_sorted = sorted(self.gemeinden_list)
            fields = ["Kategorie", "Anzahl"]
            where = 'NOT "Kategorie"' + "='" + 'Projektgemeinde/Region' + "'"
            rows = self.query_table(self._table, fields, workspace='FGDB_Einnahmen.gdb', where = where)
            for kategorie, anzahl in rows:
                gemeinden_sorted.append(u"{} || Saldo: {}".format(kategorie, -anzahl))
            par.gemeinde.filter.list = gemeinden_sorted
            par.gemeinde.value = u"{} || Saldo: {}".format(target_gemeinde_kurz, self.gemeinden_dict[target_gemeinde_kurz])

    def _updateMessages(self, params):

        par = self.par
        gemeinde_saldo = par.gemeinde.value
        gemeinde_saldo = gemeinde_saldo.split(" ||")[0]

        pfad_rahmendaten = self.folders.get_table(
            tablename='Projektrahmendaten',
            workspace="FGDB_Definition_Projekt.gdb",
            project=par.name.value)
        cursor = arcpy.da.SearchCursor(pfad_rahmendaten, ["Gemeindename"])
        for projekt in cursor:
            gemeinde_projekt = projekt[0]

        path_gemeindebilanzen = os.path.join(self.folders.get_db('FGDB_Einnahmen.gdb'), "Gemeindebilanzen")
        if not arcpy.Exists(path_gemeindebilanzen):
            par.name.setErrorMessage(u'Es müssen zuerst Wanderungssalden geschätzt werden, ehe diese bearbeitet werden können.')

        if self._nutzungsart == Nutzungsart.WOHNEN:
            where = 'Nutzungsart = {}'.format(Nutzungsart.WOHNEN)
        elif self._nutzungsart == Nutzungsart.GEWERBE:
            where = 'Nutzungsart = {} OR Nutzungsart = {}'.format(Nutzungsart.GEWERBE, Nutzungsart.EINZELHANDEL)
        rows = self.query_table('Teilflaechen_Plangebiet',
                                ['Nutzungsart'],
                                workspace='FGDB_Definition_Projekt.gdb',
                                where=where)
        if not rows:
            par.gemeinde.setErrorMessage(u'Projekt enthält keine Flächen mit der benötigten Nutzungsart.')

        if par.saldo.value > 0 and gemeinde_saldo != gemeinde_projekt:
            par.saldo.setErrorMessage('Das Wanderungssaldo dieser Gemeinde darf nicht positiv sein.')


class TbxEWSaldenbearbeiten(TbxSaldenbearbeiten):
    """Toolbox Wanderungssalden bearbeiten für Einwohner"""
    _nutzungsart = Nutzungsart.WOHNEN
    _saldo_field = "Einw_Saldo"
    _table = 'Zuzugsstatistik_Ew'

    @property
    def label(self):
        return u'Schritt 1a: Einwohner-Salden bearbeiten'

    @property
    def Tool(self):
        return Salden_bearbeiten


class TbxGewSaldenbearbeiten(TbxSaldenbearbeiten):
    """Toolbox Wanderungssalden bearbeiten Beschäftigte"""
    _nutzungsart = Nutzungsart.GEWERBE
    _saldo_field = "SvB_Saldo"
    _table = 'Zuzugsstatistik_SvB'

    @property
    def label(self):
        return u'Schritt 2a: Erwerbstätige-Salden bearbeiten'

    @property
    def Tool(self):
        return Salden_bearbeiten
