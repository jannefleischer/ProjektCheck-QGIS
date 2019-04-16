# -*- coding: utf-8 -*-
import arcpy

from pctools.utils.params import Tbx, Tool, Folders
from pctools.utils.encoding import encode
from pctools.analyst.infrastrukturkosten.kostenkennwerte_hilfsfunktionen \
     import kostenaufteilung_startwerte
import numpy as np
import pandas as pd


class NetzKostenaufteilung(Tool):
    _workspace = 'FGDB_Kosten.gdb'
    _param_projectname = 'project'

    def add_outputs(self):
        pass
    def run(self):
        tbx = self.parent_tbx
        df_results = tbx.df_results
        df_results = df_results.drop("Kostenregel", axis=1)
        arcpy.AddMessage("Änderungen werden in datenbank übertragen")
        tbx.dataframe_to_table('Kostenaufteilung', df_results,
                               pkeys=["IDNetz", "IDKostenphase"], workspace=self._workspace,
                               upsert=False)
        return



class TbxNetzKostenaufteilung(Tbx):
    _workspace = 'FGDB_Kosten.gdb'
    _netztyp = 1
    _has_been_opened = False

    @property
    def label(self):
        return encode(u'Kostenaufteilung festlegen')

    @property
    def Tool(self):
        return NetzKostenaufteilung

    def params_to_results(self, params, id_kostenphase):
        """
        update df_results with toolbox values
        id_kostenphase : list
        """

        for id_to_set in id_kostenphase:
            if id_to_set == 1:
                params_to_set = [params.owner_EH.value, params.community_EH.value, params.users_EH.value, params.default_EH.value]
            elif id_to_set == 2:
                params_to_set = [params.owner_BU.value, params.community_BU.value, params.users_BU.value, params.default_BU.value]
            elif id_to_set == 3:
                params_to_set = [params.owner_EN.value, params.community_EN.value, params.users_EN.value, params.default_EN.value]
            default = params_to_set[3]

            if default == "benutzerdefinierte Einstellungen":
                id_default = 99
            else:
                id_default = self._df_defaults.loc[default, 'IDKostenregel']

            params_to_set.append(id_default)
            self.df_results.loc[(self.df_results["IDNetz"] == self._netztyp) & (self.df_results["IDKostenphase"] == id_to_set), ["Anteil_GSB", "Anteil_GEM", "Anteil_ALL", "Kostenregel", "IDKostenregel"]] = params_to_set

    def load_network(self, params):
        """
        set params for another networkID
        params: params"""
        for id_to_set in range(1, 4):
            if id_to_set == 1:
                params_to_set = [params.default_EH, params.owner_EH, params.community_EH, params.users_EH]
            elif id_to_set == 2:
                params_to_set = [params.default_BU, params.owner_BU, params.community_BU, params.users_BU]
            elif id_to_set == 3:
                params_to_set = [params.default_EN, params.owner_EN, params.community_EN, params.users_EN]

            # set the toolbox parameters
            default, owner, community, users = params_to_set
            idx = ((self.df_results.IDNetz == self._netztyp) &
                   (self.df_results.IDKostenphase == id_to_set))
            id_rule = self.df_results.loc[idx, 'IDKostenregel'].values[0]

            owner.value = int(self.df_results.loc[idx, 'Anteil_GSB'])
            community.value = int(self.df_results.loc[idx, 'Anteil_GEM'])
            users.value = int(self.df_results.loc[idx, 'Anteil_ALL'])
            default.value = self.df_results.loc[idx, 'Kostenregel'].values[0] \
                if id_rule < 99 else u"benutzerdefinierte Einstellungen"

    def load_defaults(self, params, id_kostenphase):
        """
        sets the toolbox values for EH:1, BU:2 or EN:3
        params : params
        id_kostenphase : list
        """
        for id_to_set in id_kostenphase:
            if id_to_set == 1:
                params_to_set = [params.default_EH, params.owner_EH, params.community_EH, params.users_EH]
            elif id_to_set == 2:
                params_to_set = [params.default_BU, params.owner_BU, params.community_BU, params.users_BU]
            elif id_to_set == 3:
                params_to_set = [params.default_EN, params.owner_EN, params.community_EN, params.users_EN]

            # set the toolbox parameters
            default, owner, community, users = params_to_set
            owner.value = int(self._df_defaults.loc[(self._df_defaults.Kostenregel == default.value), 'Anteil_GSB'])
            community.value = int(self._df_defaults.loc[(self._df_defaults.Kostenregel == default.value), 'Anteil_GEM'])
            users.value = int(self._df_defaults.loc[(self._df_defaults.Kostenregel == default.value), 'Anteil_ALL'])
            # update the results dataframe
            id_default = self._df_defaults.loc[default.value, 'IDKostenregel']
            self.df_results.loc[(self.df_results.IDNetz == self._netztyp) & (self.df_results.IDKostenphase == id_to_set), ['Anteil_GSB', 'Anteil_GEM', 'Anteil_ALL', 'Kostenregel', 'IDKostenregel']] = \
                [owner.value, community.value, users.value, default.value, id_default]

    def _update_suggestion_list(self, params):
        suggestions_EH = self._df_suggestions.loc[(self._df_suggestions.IDNetz == self._netztyp) & (self._df_suggestions.IDPhase==1), 'Kostenregel'].values.tolist()
        suggestions_EH.append(u"benutzerdefinierte Einstellungen")
        params.default_EH.filter.list = suggestions_EH
        suggestions_BU = self._df_suggestions.loc[(self._df_suggestions.IDNetz == self._netztyp) & (self._df_suggestions.IDPhase==2), 'Kostenregel'].values.tolist()
        suggestions_BU.append(u"benutzerdefinierte Einstellungen")
        params.default_BU.filter.list = suggestions_BU
        suggestions_EN = self._df_suggestions.loc[(self._df_suggestions.IDNetz == self._netztyp) & (self._df_suggestions.IDPhase==3), 'Kostenregel'].values.tolist()
        suggestions_EN.append(u"benutzerdefinierte Einstellungen")
        params.default_EN.filter.list = suggestions_EN

    def _open(self, params):
        # get initial data
        kostenaufteilung_startwerte(self.par.get_projectname())
        params.network.value = self._df_netzwork_id.loc[self._df_netzwork_id.IDNetz == self._netztyp, 'Netz'].values[0]
        self.df_results = self.table_to_dataframe('Kostenaufteilung', workspace=self._workspace)
        self.df_results = self.df_results.astype(int)
        rules = self._df_defaults[['IDKostenregel', 'Kostenregel']]
        self.df_results = pd.merge(self.df_results, rules,
                                   on='IDKostenregel', how='left')
        self.load_network(params)


    def _updateParameters(self, params):
        if not self._has_been_opened:
            self._has_been_opened = True
            return params
        if self.par.changed('network'):
            network_id = int(self._df_netzwork_id.loc[self._df_netzwork_id.Netz == params.network.value, 'IDNetz'])
            self._netztyp = network_id
            self.load_network(params)
            self._update_suggestion_list(params)

        # check if other default settings were choosen
        if self.par.changed('default_EH'):
            if params.default_EH.value != u"benutzerdefinierte Einstellungen":
                self.load_defaults(params, [1])
        if self.par.changed('default_BU'):
            if params.default_BU.value != u"benutzerdefinierte Einstellungen":
                self.load_defaults(params, [2])
        if self.par.changed('default_EN'):
            if params.default_EN.value != u"benutzerdefinierte Einstellungen":
                self.load_defaults(params, [3])
        # check if range-filter has changed
        # EH
        if self.par.changed('community_EH', 'owner_EH', 'users_EH'):
            params.default_EH.value = u"benutzerdefinierte Einstellungen"
            self.params_to_results(params, [1])
        # BU
        if self.par.changed('community_BU', 'owner_BU', 'users_BU'):
            params.default_BU.value = u"benutzerdefinierte Einstellungen"
            self.params_to_results(params, [2])
            # EN
        if self.par.changed('community_EN', 'owner_EN', 'users_EN'):
            params.default_EN.value = u"benutzerdefinierte Einstellungen"
            self.params_to_results(params, [3])
        return params

    def _getParameterInfo(self):
        params = self.par
        projekte = self.folders.get_projects()
        # load default setting from table Aufteilungsregeln
        self._df_defaults = self.table_to_dataframe('Aufteilungsregeln', columns=[],
                                                   workspace='FGDB_Kosten_Tool.gdb',
                                                   where=None,
                                                   pkey='',
                                                   project='',
                                                   is_base_table=True)
        self._df_defaults.rename(columns={'IDAufteilungsregel': 'IDKostenregel', 'Aufteilungsregel': 'Kostenregel',}, inplace=True)
        self._df_defaults.index = self._df_defaults["Kostenregel"]
        self._df_defaults.loc[:, ["Anteil_GSB", "Anteil_GEM", "Anteil_ALL"]] = \
            self._df_defaults.loc[:, ["Anteil_GSB", "Anteil_GEM", "Anteil_ALL"]].astype(int)
        # filter list for Kostenregel
        self._df_suggestions = self.table_to_dataframe(
            'Aufteilungsregeln_zu_Netzen_und_Phasen', columns=[],
            workspace='FGDB_Kosten_Tool.gdb', where=None, is_base_table=True)
        self._df_suggestions = pd.merge(self._df_suggestions, self._df_defaults.loc[:, ['IDKostenregel', 'Kostenregel']], left_on='IDAufteilungsregel', right_on='IDKostenregel')
        default_list = list(self._df_defaults.Kostenregel)
        default_list.append(u"benutzerdefinierte Einstellungen")
        # dataframe for network and networkID
        self._df_netzwork_id = self.table_to_dataframe(
            'Netze_und_Netzelemente', columns=['IDNetz', 'Netz'],
            workspace='FGDB_Kosten_Tool.gdb', is_base_table=True)
        self._df_netzwork_id = self._df_netzwork_id.drop_duplicates()
        category_EH = "1) Einmalige Herstellung"
        category_BU = "2) Betrieb und Unterhaltung"
        category_EN = "3) Erneuerung"
        # Projekt_auswählen
        p = self.add_parameter('project')
        p.name = u'Projekt_auswählen'.encode('cp1252')
        p.displayName = u'Projekt'.encode('cp1252')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        p.filter.list = projekte
        if projekte:
            p.value = projekte[0]

        # Netz
        p = self.add_parameter('network')
        p.name = u'network'.encode('cp1252')
        p.displayName = u'Netz'.encode('cp1252')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        p.filter.list = list(self._df_netzwork_id.Netz)

        # category = EH
        # Nachfolgende Werte setzen auf
        p = self.add_parameter("default_EH")
        p.name = u"default_EH".encode("cp1252")
        p.displayName = u"Nachfolgende Werte setzen auf ...".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        #p.filter.list = default_list
        p.category = category_EH
        # Grundstücksbesitzer
        p = self.add_parameter("owner_EH")
        p.name = u"owner_EH".encode("cp1252")
        p.displayName = u"Kostenanteil der GrundstücksbesitzerInnen (in Prozent)".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = "Range"
        p.filter.list = [0, 100]
        p.category = category_EH
        # Gemeinde
        p = self.add_parameter("community_EH")
        p.name = u"community_EH".encode("cp1252")
        p.displayName = u"Kostenanteil der Gemeinde (in Prozent)".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = "Range"
        p.filter.list = [0, 100]
        p.category = category_EH
        # Nutzer
        p = self.add_parameter("users_EH")
        p.name = u"users_EH".encode("cp1252")
        p.displayName = u"Kostenanteil der Allgemeinheit der Netznutzer und Tarifkunden (in Prozent)".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = "Range"
        p.filter.list = [0, 100]
        p.category = category_EH
        self.add_dependency(['owner_EH', 'community_EH', 'users_EH'], 100)

        # category = BU
        # Nachfolgende Werte setzen auf
        p = self.add_parameter("default_BU")
        p.name = u"default_BU".encode("cp1252")
        p.displayName = u"Nachfolgende Werte setzen auf ...".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        #p.filter.list = default_list
        p.category = category_BU
        # Grundstücksbesitzer
        p = self.add_parameter("owner_BU")
        p.name = u"owner_BU".encode("cp1252")
        p.displayName = u"Kostenanteil der GrundstücksbesitzerInnen (in Prozent)".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = "Range"
        p.filter.list = [0, 100]
        p.category = category_BU
        # Gemeinde
        p = self.add_parameter("community_BU")
        p.name = u"community_BU".encode("cp1252")
        p.displayName = u"Kostenanteil der Gemeinde (in Prozent)".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = "Range"
        p.filter.list = [0, 100]
        p.category = category_BU
        # Nutzer
        p = self.add_parameter("users_BU")
        p.name = u"users_BU".encode("cp1252")
        p.displayName = u"Kostenanteil der Allgemeinheit der Netznutzer und Tarifkunden (in Prozent)".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = "Range"
        p.filter.list = [0, 100]
        p.category = category_BU
        self.add_dependency(['owner_BU', 'community_BU', 'users_BU'], 100)

        # category = EN
        # Nachfolgende Werte setzen auf
        p = self.add_parameter("default_EN")
        p.name = u"default_EN".encode("cp1252")
        p.displayName = u"Nachfolgende Werte setzen auf ...".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        #p.filter.list = default_list
        p.category = category_EN
        # Grundstücksbesitzer
        p = self.add_parameter("owner_EN")
        p.name = u"owner_EN".encode("cp1252")
        p.displayName = u"Kostenanteil der GrundstücksbesitzerInnen (in Prozent)".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = "Range"
        p.filter.list = [0, 100]
        p.category = category_EN
        # Gemeinde
        p = self.add_parameter("community_EN")
        p.name = u"community_EN".encode("cp1252")
        p.displayName = u"Kostenanteil der Gemeinde (in Prozent)".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = "Range"
        p.filter.list = [0, 100]
        p.category = category_EN
        # Nutzer
        p = self.add_parameter("users_EN")
        p.name = u"users_EN".encode("cp1252")
        p.displayName = u"Kostenanteil der Allgemeinheit der Netznutzer und Tarifkunden (in Prozent)".encode("cp1252")
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = "Range"
        p.filter.list = [0, 100]
        p.category = category_EN
        self.add_dependency(['owner_EN', 'community_EN', 'users_EN'], 100)

        self._update_suggestion_list(params)

        return params

class TbxNetzKostenaufteilungInnere(TbxNetzKostenaufteilung):
    _netztyp = 1
class TbxNetzKostenaufteilungAuessere(TbxNetzKostenaufteilung):
    _netztyp = 2
class TbxNetzKostenaufteilungKanalisation(TbxNetzKostenaufteilung):
    _netztyp = 3
class TbxNetzKostenaufteilungTrinkwasser(TbxNetzKostenaufteilung):
    _netztyp = 4
class TbxNetzKostenaufteilungElektrizitaet(TbxNetzKostenaufteilung):
    _netztyp = 5

if __name__ == '__main__':
    t = TbxNetzKostenaufteilung()
    t._getParameterInfo()
    t.par.project.value = t.config.active_project
    t.open()
    t._has_been_opened = False
    t._updateParameters(t.par)
    t.execute()
