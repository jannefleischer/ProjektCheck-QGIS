# -*- coding: utf-8 -*-
import os
import sys
import arcpy
import shutil
import re
import pandas as pd
import numpy as np

from tools.utils.params import Tbx, Tool
from tools.utils.encoding import encode
from tools.utils.spatial_lib import get_ags, minimal_bounding_poly, remove_duplicates
from tools.analyst.standortkonkurrenz.osm_einlesen import (OSMShopsReader,
                                                              Point)
from tools.analyst.standortkonkurrenz.tbx_osm_markteinlesen import (
    OSMMarktEinlesen)


class OSMMarktBuffer(OSMMarktEinlesen):
    _markets_table = 'Maerkte'
    _markets_buffer = 'Maerkte_Puffer'
    _out_layer_name = 'erweiterter Betrachtungsraum'

    def add_outputs(self):
        super(OSMMarktEinlesen, self).add_outputs()
        self.output.add_layer('standortkonkurrenz',
                              self._markets_buffer,
                              featureclass=self._markets_buffer,
                              name=self._out_layer_name,
                              template_folder="Standortkonkurrenz")

    def run(self):
        communities = self.folders.get_table('Zentren')
        ws_tmp = arcpy.env.scratchGDB
        sel_comm = os.path.join(ws_tmp, 'sel_comm')
        feat_buffered = os.path.join(ws_tmp, 'feat_buffered')
        markets_table = self.folders.get_table(self._markets_table, check=False)
        markets_tmp = self.folders.get_table('markets_tmp', check=False)
        markets_buffer = self.folders.get_table('markets_buffer', check=False)
        markets_buffer_output = self.folders.get_table(self._markets_buffer,
                                                       check=False)
        markets_com = os.path.join(ws_tmp, 'markets_com')

        def del_tmp():
            for f in [sel_comm, feat_buffered, markets_buffer, markets_tmp,
                      markets_com]:
                arcpy.Delete_management(f)

        del_tmp()

        arcpy.FeatureClassToFeatureClass_conversion(
            communities, ws_tmp, os.path.split(sel_comm)[1],
            where_clause='Auswahl<>0')

        # ToDo: buffer -> multi_poly -> markets -> markets in selected communities -> remove those from markets in multi_poly -> to db

        arcpy.AddMessage('Analysiere Pufferbereich...')
        # create buffer area
        arcpy.Buffer_analysis(sel_comm, feat_buffered,
                              self.par.radius_markets.value,
                              dissolve_option='NONE')
        try:
            self.output.remove_layer(self._out_layer_name)
        except:
            pass

        arcpy.Delete_management(markets_buffer_output)
        arcpy.Dissolve_management(feat_buffered, markets_buffer_output, "", "",
                                  "SINGLE_PART", "DISSOLVE_LINES")

        multi_poly = minimal_bounding_poly(feat_buffered)
        epsg = self.parent_tbx.config.epsg
        multi_poly = [[Point(p.X, p.Y, epsg=epsg) for p in poly]
                      for poly in multi_poly]
        reader = OSMShopsReader(epsg=epsg)
        markets = []
        arcpy.AddMessage('Ermittle Märkte im Randgebiet...')
        count = 1000
        for poly in multi_poly:
            m = reader.get_shops(poly, count=count-len(markets))
            markets += m

        if len(markets) > 0:
            # pro license only
            #arcpy.SymDiff_analysis(feat_buffered, sel_comm, buffer_diff)

            #self.parent_tbx.delete_rows_in_table(self._markets_table,
                                                 #where='is_buffer=1')
            arcpy.CreateFeatureclass_management(
                os.path.split(markets_tmp)[0], os.path.split(markets_tmp)[1],
                template=markets_table
            )
            ids = [id for id, in self.parent_tbx.query_table(markets_table, ['id'])]
            start_id = max(ids) + 1 if ids else 0
            markets = self.parse_meta(markets)
            self.markets_to_db(markets,
                               tablename=os.path.split(markets_tmp)[1],
                               is_buffer=True, start_id=start_id, is_osm=True)
            arcpy.Clip_analysis(markets_tmp, feat_buffered, markets_buffer)
            arcpy.Clip_analysis(markets_buffer, sel_comm, markets_com)
            cursor = arcpy.da.SearchCursor(markets_com, ['id'])
            in_com_ids = [str(id) for id, in cursor]
            del(cursor)
            where = 'id IN ({})'.format(','.join(in_com_ids))
            self.parent_tbx.delete_rows_in_table(markets_buffer, where)
            arcpy.Append_management(markets_buffer, markets_table)

            arcpy.AddMessage('Entferne Duplikate...')
            n = remove_duplicates(markets_table, 'id', match_field='id_kette',
                                  where='is_buffer=1', distance=50)
            arcpy.AddMessage('{} Duplikate entfernt...'.format(n))

            self.set_ags()
        del_tmp()


class TbxOSMBuffer(Tbx):

    @property
    def label(self):
        return encode(u'Erweiterten Betrachtungsraum mit Märkten '
                      u'aus OpenStreetMap ergänzen')

    @property
    def Tool(self):
        return OSMMarktBuffer

    def _getParameterInfo(self):

        params = self.par

        # Projekt_auswählen
        param = self.add_parameter('projectname')
        param.name = encode(u'Projekt_auswählen')
        param.displayName = encode(u'Projekt')
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'GPString'
        param.filter.list = []

        # markets radius
        p = self.add_parameter('radius_markets')
        p.name = u'radius_markets'
        p.displayName = encode(u'Pufferzone für Märkte um gewählte '
                               u'Gemeinden festlegen (in m)')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = 'Range'
        p.filter.list = [3000, 10000]
        p.value = 6000
        p.enabled = True

        return params

    def _updateParameters(self, params):

        return params


if __name__ == '__main__':
    t = TbxOSMBuffer()
    t._getParameterInfo()
    t.set_active_project()
    t.execute()
