# -*- coding: utf-8 -*-
import arcpy

from pctools.utils.params import Tbx, Tool, Folders
from pctools.utils.encoding import encode
from pctools.analyst.infrastrukturkosten.kostenkennwerte_hilfsfunktionen import kostenkennwerte
import numpy as np
import pandas as pd


class KostenkennwerteKontrollieren(Tool):
    _workspace = 'FGDB_Kosten.gdb'
    _param_projectname = 'project'
    _table = 'Kostenkennwerte_Linienelemente'

    def add_outputs(self):
        pass

    def run(self):
        tbx = self.parent_tbx
        tbx.dataframe_to_table(self._table, tbx.df_costs,
                               pkeys=['ID'], workspace=self._workspace)
        return


class TbxKostenkennwerteKontrollieren(Tbx):
    _table = 'Kostenkennwerte_Linienelemente'
    @property
    def label(self):
        return encode(u'Kostenkennwerte kontrollieren')

    @property
    def Tool(self):
        return KostenkennwerteKontrollieren

    def _open(self, params):
        # if Kostenkennwerte_Linienelemente does not exist, create the table
        # initially
        kostenkennwerte(self.par.project.value)
        df_costs = self.table_to_dataframe(self._table,
                                           workspace='FGDB_Kosten.gdb')
        self.df_costs = df_costs
        network_elements = list(self.df_costs.Netzelement)
        network = list(self.df_costs.Netz)
        network_and_elements = [network[i] + " | " + network_elements[i] for
                                i in range(len(network_elements))]

        params.network.filter.list = network_and_elements
        params.network.value = network_and_elements[0]
        params.costs_EH.value = int(self.df_costs.Euro_EH[0])
        params.costs_BU.value = int(self.df_costs.Cent_BU[0])
        params.costs_EN.value = int(self.df_costs.Euro_EN[0])
        params.lifespan.value = int(self.df_costs.Lebensdauer[0])

    def get_from_df(self, df, columns, df_id):
        df_selected = df.loc[df_id, (columns)]
        return df_selected


    def _updateParameters(self, params):
        network, network_element = params.network.value.split(' | ')
        df_id = self.df_costs[(self.df_costs.Netzelement == network_element) &
                              (self.df_costs.Netz == network)].index
        if self.par.changed('network'):
            # set tbx parameters initially
            df_selected = self.get_from_df(self.df_costs,
                                         ['Euro_EH', 'Cent_BU',
                                          'Euro_EN', 'Lebensdauer'], df_id)
            params.costs_EH.value = int(df_selected.Euro_EH)
            params.costs_BU.value = int(df_selected.Cent_BU)
            params.costs_EN.value = int(df_selected.Euro_EN)
            params.lifespan.value = int(df_selected.Lebensdauer)
            return params
        # update df_costs, if tbx parameters have changed
        if self.par.changed('costs_EH'):
            self.df_costs.loc[df_id, ('Euro_EH')] = self.par.costs_EH.value
        if self.par.changed('costs_BU'):
            self.df_costs.loc[df_id, ('Cent_BU')] = self.par.costs_BU.value
        if self.par.changed('costs_EN'):
            self.df_costs.loc[df_id, ('Euro_EN')] = self.par.costs_EN.value
        if self.par.changed('lifespan'):
            self.df_costs.loc[df_id, ('Lebensdauer')] = self.par.lifespan.value
        return params

    def _getParameterInfo(self):
        params = self.par
        projekte = self.folders.get_projects()

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
        # Netzelement
        p = self.add_parameter('network')
        p.name = u'network'.encode('cp1252')
        p.displayName = u'Netzelement'.encode('cp1252')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        # Kosten EH
        p = self.add_parameter('costs_EH')
        p.name = u'costs_EH'.encode('cp1252')
        p.displayName = u'Kosten der erstmaligen Herstellung: EUR pro laufenen Meter'.encode('cp1252')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = 'Range'
        p.filter.list = [0, 2000]
        # Kosten BU
        p = self.add_parameter('costs_BU')
        p.name = u'costs_BU'.encode('cp1252')
        p.displayName = u'Jährliche Kosten für Betrieb und Unterhaltung: Cent pro laufenden Meter und Jahr'.encode('cp1252')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = 'Range'
        p.filter.list = [0, 2000]
        # Kosten EN
        p = self.add_parameter('costs_EN')
        p.name = u'costs_EN'.encode('cp1252')
        p.displayName = u'Kosten der Erneuerung: Euro pro laufenden Meter und Erneuerungszyklus'.encode('cp1252')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = 'Range'
        p.filter.list = [0, 2000]
        # Lebensdauer
        p = self.add_parameter('lifespan')
        p.name = u'lifespan'.encode('cp1252')
        p.displayName = u'Lebensdauer: Jahre zwischen den Erneuerungszyklen'.encode('cp1252')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = 'Range'
        p.filter.list = [0, 100]

        return params


if __name__ == '__main__':
    t = TbxKostenkennwerteKontrollieren()
    t._getParameterInfo()
    t.par.project.value = t.config.active_project
    t._open(t.par)
    t._updateParameters(t.par)
    t.execute()
