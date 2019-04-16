# -*- coding: utf-8 -*-
import os
import arcpy
import webbrowser

from pctools.utils.params import Tbx, Tool
from pctools.utils.encoding import encode
from pctools.analyst.erreichbarkeit.tbx_HaltestellenZentraleOrte import next_working_day
from pctools.analyst.erreichbarkeit.bahn_query import BahnQuery


class Fahrplaene(Tool):
    _param_projectname = 'projectname'
    _workspace = 'FGDB_Erreichbarkeit.gdb'

    def add_outputs(self):
        pass

    def run(self):
        query = BahnQuery(next_working_day())
        idx = self.par.selected_index('stops')
        id = self.parent_tbx.df_stops['id'].values[idx]
        url = query.get_timetable_url(id)
        arcpy.AddMessage('\nDIE ABFAHRTSZEITEN WERDEN EXTERN IM BROWSER ANGEZEIGT!\n')
        webbrowser.open(url, new=1, autoraise=True)

class TbxHaltestellen(Tbx):

    def _getParameterInfo(self):

        params = self.par
        projekte = self.folders.get_projects()

        # Projekt_auswählen
        p = self.add_parameter('projectname')
        p.name = u'Projekt_auswählen'.encode('cp1252')
        p.displayName = u'Projekt'.encode('cp1252')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        p.value = self.config.active_project

        param = self.add_parameter('stops')
        param.name = encode(u'stops')
        param.displayName = encode(u'Name der Haltestelle')
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'GPString'
        param.filter.list = []

        self.df_stops = []

        return params

    def validate_inputs(self):
        df_stops = self.get_stops()
        if len(df_stops) == 0:
            msg = (u'Die Haltestellen wurden noch nicht ermittelt!')
            return False, msg
        return True, ''

    def get_stops(self):
        df_stops = self.table_to_dataframe(
            'Haltestellen', where='flaechenzugehoerig=1')
        return df_stops

    def _open(self, params):
        self.df_stops = self.get_stops()

        names = self.df_stops['name'].values
        distances = self.df_stops['fussweg'].values
        pretty = [u'{} ({} m entfernt)'.format(n, d)
                  for n, d in zip(names, distances)]
        param = params.stops
        param.filter.list = pretty
        param.value = pretty[0]


class TbxFahrplaene(TbxHaltestellen):

    @property
    def label(self):
        return encode(u'Haltestellenplan in einem externen Webbrowser anzeigen')

    @property
    def Tool(self):
        return Fahrplaene

if __name__ == "__main__":
    t = TbxFahrplaene()
    t.getParameterInfo()
    t.set_active_project()
    t._open(t.par)
    t.execute()
