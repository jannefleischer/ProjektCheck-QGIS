# -*- coding: utf-8 -*-
import pandas as pd
import arcpy
import requests
import sys
from tools.utils.params import Tbx, Tool
from tools.utils.encoding import encode
from tools.analyst.erreichbarkeit.tbx_fahrplaene import TbxHaltestellen
from tools.analyst.erreichbarkeit.bahn_query import BahnQuery
from tools.analyst.erreichbarkeit.tbx_HaltestellenZentraleOrte import next_working_day


class ErreichbarkeitOEPNV(Tool):
    _param_projectname = 'projectname'
    _workspace = 'FGDB_Erreichbarkeit.gdb'

    times = range(9, 18)

    def add_outputs(self):
        idx = self.par.selected_index('stops')
        stop_id = self.parent_tbx.df_stops['id'].values[idx]
        stop_name = self.parent_tbx.df_stops['name'].values[idx]

        group_layer = ("erreichbarkeit")
        fc = 'Erreichbarkeiten_OEPNV'
        layer = u'Erreichbarkeiten ÖPNV'

        layer_name = u'{n} (Haltestelle: {s})'.format(n=layer,
                                                     s=stop_name)
        self.output.add_layer(group_layer, layer, fc,
                              template_folder='Erreichbarkeit',
                              query='id_origin={}'.format(stop_id),
                              name=layer_name,
                              zoom=True)

    def run(self):
        idx = self.par.selected_index('stops')
        stop_name = self.parent_tbx.df_stops['name'].values[idx]
        stop_id = self.parent_tbx.df_stops['id'].values[idx]
        arcpy.AddMessage(u'Berechne Erreichbarkeit der Zentralen Orte\n '
                         u'ausgehend von der Haltestelle {}'.format(stop_name))
        self.routing(stop_name, stop_id, self.par.recalculate.value)

    def routing(self, origin, id_origin, recalculate=False):
        query = BahnQuery(next_working_day(), timeout=0.5)
        df_centers = self.parent_tbx.table_to_dataframe('Zentrale_Orte')
        df_stops = self.parent_tbx.table_to_dataframe('Haltestellen')
        df_calculated = self.parent_tbx.table_to_dataframe(
            'Erreichbarkeiten_OEPNV')
        df_centers['update'] = False
        n_centers = len(df_centers)

        for i, (index, center) in enumerate(df_centers.iterrows()):
            id_destination = center['id_haltestelle']
            destination = df_stops[df_stops['id'] == id_destination]['name'].values[0]
            arcpy.AddMessage(u'  - {} ({}/{})'.format(destination, i + 1,
                                                      n_centers))

            if not recalculate:
                already_calculated = (
                    (df_calculated['id_origin'] == id_origin).values &
                    (df_calculated['id_destination'] == id_destination).values
                ).sum() > 0
                if already_calculated:
                    arcpy.AddMessage(u'   bereits berechnet, wird übersprungen')
                    continue

            try:
                (duration, departure,
                 changes, modes) = query.routing(origin, destination, self.times)
            except requests.exceptions.ConnectionError:
                arcpy.AddError('Die Website der Bahn wurde nicht erreicht. '
                               'Bitte überprüfen Sie Ihre Internetverbindung!')
                return
            # just appending results to existing table to write them later
            df_centers.loc[index, 'id_origin'] = id_origin
            df_centers.loc[index, 'id_destination'] = id_destination
            df_centers.loc[index, 'ziel'] = destination
            df_centers.loc[index, 'abfahrt'] = departure
            if duration != sys.maxint:
                df_centers.loc[index, 'dauer'] = str(duration)
            else:
                df_centers.loc[index, 'dauer'] = "???"
            df_centers.loc[index, 'umstiege'] = changes
            df_centers.loc[index, 'verkehrsmittel'] = modes
            df_centers.loc[index, 'update'] = True

        arcpy.AddMessage(u'Schreibe Ergebnisse in die Datenbank...')

        df_update = df_centers[df_centers['update'] == True]
        if len(df_update) > 0:
            self.parent_tbx.dataframe_to_table(
                'Erreichbarkeiten_OEPNV',
                df_centers,
                pkeys=['id_origin', 'id_destination'],
                upsert=True)


class TbxErreichbarkeitOEPNV(TbxHaltestellen):

    @property
    def label(self):
        return encode(u'Erreichbarkeit der zentralen Orte im ÖPNV ermitteln')

    @property
    def Tool(self):
        return ErreichbarkeitOEPNV

    def _getParameterInfo(self):
        super(TbxErreichbarkeitOEPNV, self)._getParameterInfo()
        params = self.par
        params.stops.displayName = encode(u'Abfahrt von Haltestelle:')

        param = self.add_parameter('recalculate')
        param.name = encode(u'Neuberechnung')
        param.displayName = encode(u'Neuberechnung erzwingen')
        param.parameterType = 'Optional'
        param.direction = 'Input'
        param.datatype = u'GPBoolean'

        return params


if __name__ == "__main__":

    t = TbxErreichbarkeitOEPNV()
    b = t.getParameterInfo()
    t.set_active_project()
    t.open()
    #t.show_outputs()
    t.execute()
