# -*- coding: utf-8 -*-
from tools.utils.params import Tbx, Tool
from tools.utils.encoding import encode
from tools.utils.constants import Nutzungsart as nart
from tools.analyst.verkehr.otp_router import OTPRouter
from tools.analyst.verkehr.routing import Routing
import arcpy
import pandas as pd
import os

class Settings(Routing):
    _workspace = 'FGDB_Verkehr.gdb'
    _param_projectname = 'project'
    _initial_routing_exists = False
    _transfernodes_layer_exsists = False
    _nodes_have_been_weighted = False

    def add_outputs(self):
        if self._initial_routing_exists:
            self.output.add_layer('verkehr', 'links',
                                  featureclass='links',
                                  template_folder='Verkehr',
                                  name='Zusätzliche PKW-Fahrten', zoom=True,
                                  zoom_extent=self._extent,
                                  symbology_classes=(15, 'weight'))
            if self._transfernodes_layer_exsists:
                return
            if self._nodes_have_been_weighted:
                self.output.add_layer('verkehr', 'Zielpunkte_gewichtet',
                                      featureclass='Zielpunkte',
                                      template_folder='Verkehr',
                                      name='Zielpunkte gewichtet',
                                      symbology_classes=(10, 'Neue_Gewichte'),
                                      zoom=False)
            else:
                self.output.add_layer('verkehr', 'Zielpunkte',
                                      featureclass='Zielpunkte',
                                      template_folder='Verkehr',
                                      name='Herkunfts-/Zielpunkte',
                                      zoom=False)

    def run(self):
        toolbox = self.parent_tbx
        # tbx settings
        wege_w = toolbox.par.wohnen_wege.value
        pkw_w = toolbox.par.wohnen_pkw.value
        wege_g = toolbox.par.gewerbe_wege.value
        pkw_g = toolbox.par.gewerbe_pkw.value
        wege_e = toolbox.par.einzelhandel_wege.value
        pkw_e = toolbox.par.einzelhandel_pkw.value
        # write settings into the table
        toolbox.update_table('Wege_je_Nutzung',
                          {'Wege_gesamt': wege_w, 'PKW_Anteil': pkw_w},
                          where='Nutzungsart={}'.format(nart.WOHNEN))
        toolbox.update_table('Wege_je_Nutzung',
                          {'Wege_gesamt': wege_g, 'PKW_Anteil': pkw_g},
                          where='Nutzungsart={}'.format(nart.GEWERBE))
        toolbox.update_table('Wege_je_Nutzung',
                          {'Wege_gesamt': wege_e, 'PKW_Anteil': pkw_e},
                          where='Nutzungsart={}'.format(
                              nart.EINZELHANDEL))
        #self.remove_output()
        # delete pickle file
        pickle_path = self.folders.get_otp_pickle_filename(check=False)

        if os.path.exists(pickle_path):
            self._initial_routing_exists = True
            otp_router = OTPRouter.from_dump(pickle_path)
            data_wjn = [(1, wege_w, pkw_w), (2, wege_g, pkw_g), (3, wege_e, pkw_e)]
            data_tfl = self.get_areas_data()
            data_tfl = pd.DataFrame(self.calc_trips(data_tfl, data_wjn))

            for area in otp_router.areas.itervalues():
                trips = data_tfl.loc[(data_tfl[0] == area.source_id), 1]
                area.trips = trips.values[0]

            #otp_router.transfer_nodes.calc_initial_weight()
            otp_router.calc_vertex_weights()
            otp_router.create_polyline_features()
            otp_router.create_node_features()
            self._nodes_have_been_weighted = otp_router.nodes_have_been_weighted
            self._extent = otp_router.extent
            otp_router.dump(pickle_path)
            self.remove_output()
            #transfer_nodes = otp_router.transfer_nodes
            #transfer_nodes.assign_weights_to_routes()
            #otp_router.create_polyline_features()
            #os.remove(pickle_path)

    def remove_output(self):
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
        layers1 = arcpy.mapping.ListLayers(mxd, "Zielpunkte*", df)
        layers2 = arcpy.mapping.ListLayers(mxd, "*Fahrten*", df)
        if layers1:
            self._transfernodes_layer_exsists = True
        layers = sum([layers2], [])
        for layer in layers:
            arcpy.mapping.RemoveLayer(df, layer)
        del(mxd)

class TbxSettings(Tbx):

    @property
    def label(self):
        return encode(u'Verkehrsaufkommen und Verkehrsmittelwahl')

    @property
    def Tool(self):
        return Settings

    def round_param(self, value):
        if value >= 10000:
            return round(value, -3)
        elif value >= 1000:
            return round(value, ndigits=-2)
        return round(value, -1)

    def _open(self, params):
        # get values from fgdb
        wege_w, pkw_w= self.query_table('Wege_je_Nutzung',
                                    columns=['Wege_gesamt',
                                             'PKW_Anteil'],
                                    where='Nutzungsart={}'.format(
                                        nart.WOHNEN))[0]
        wege_g, pkw_g= self.query_table('Wege_je_Nutzung',
                                        columns=['Wege_gesamt',
                                                'PKW_Anteil'],
                                        where='Nutzungsart = {}'.format(
                                            nart.GEWERBE))[0]
        wege_e, pkw_e= self.query_table('Wege_je_Nutzung',
                                        columns=['Wege_gesamt',
                                                 'PKW_Anteil'],
                                        where='Nutzungsart = {}'.format(
                                            nart.EINZELHANDEL))[0]
        wege_w = self.round_param(wege_w)
        wege_g = self.round_param(wege_g)
        wege_e = self.round_param(wege_e)
        # set params and check if wege_x is set. if not: disable
        params.wohnen_wege.value = wege_w
        params.wohnen_pkw.value = pkw_w
        if wege_w == 0:
            params.wohnen_wege.enabled = False
            params.wohnen_pkw.enabled = False
        params.gewerbe_wege.value = wege_g
        params.gewerbe_pkw.value = pkw_g
        if wege_g == 0:
            params.gewerbe_wege.enabled = False
            params.gewerbe_pkw.enabled = False
        params.einzelhandel_wege.value = wege_e
        params.einzelhandel_pkw.value = pkw_e
        if wege_e == 0:
            params.einzelhandel_wege.enabled = False
            params.einzelhandel_pkw.enabled = False


    def _getParameterInfo(self):
        params = self.par

        # Projekt
        param = params.project = arcpy.Parameter()
        param.name = u'Projekt'
        param.displayName = u'Projekt'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'GPString'

        category = '1) Verkehrsaufkommen Wohnen'

        # Wohnen
        param = params.wohnen_wege = arcpy.Parameter()
        param.name = u'wohnen_wege'
        param.displayName = u'Gesamtzahl der Wege pro Werktag ' + \
            u'(Hin- und Rückwege)'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Long'
        param.category = category

        param = params.wohnen_pkw = arcpy.Parameter()
        param.name = u'wohnen_pkw'
        param.displayName = u'Anteil der Wege als Pkw-Fahrer/in an dieser ' + \
            u'Gesamtzahl (in Prozent)'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Long'
        param.filter.type = 'Range'
        param.filter.list = [0, 100]
        param.category = category
        category = '2) Verkehrsaufkommen Gewerbe'

        # Gewerbe
        param = params.gewerbe_wege = arcpy.Parameter()
        param.name = u'gewerbe_wege'
        param.displayName = u'Gesamtzahl der Wege pro Werktag ' + \
            u'(Hin- und Rückwege)'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Long'
        param.category = category

        param = params.gewerbe_pkw = arcpy.Parameter()
        param.name = u'gewerbe_pkw'
        param.displayName = u'Anteil der Wege als Pkw-Fahrer/in an dieser ' + \
            u'Gesamtzahl (in Prozent)'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Long'
        param.filter.type = 'Range'
        param.filter.list = [0, 100]
        param.category = category

        category = '3) Verkehrsaufkommen Einzelhandel'

        # Einzelhandel
        param = params.einzelhandel_wege = arcpy.Parameter()
        param.name = u'einzelhandel_wege'
        param.displayName = u'Gesamtzahl der Wege pro Werktag ' + \
            u'(Hin- und Rückwege)'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Long'
        param.category = category

        param = params.einzelhandel_pkw = arcpy.Parameter()
        param.name = u'einzelhandel_pkw'
        param.displayName = u'Anteil der Wege als Pkw-Fahrer/in an dieser ' + \
            u'Gesamtzahl (in Prozent)'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Long'
        param.filter.type = 'Range'
        param.filter.list = [0, 100]
        param.category = category

        return params

    def _updateParameters(self, params):
        return

if __name__ == "__main__":
    t = TbxSettings()
    t.getParameterInfo()
    t.par.wohnen_wege.value = 1000
    t.par.wohnen_pkw.value = 50
    t.par.gewerbe_wege.value = 2000
    t.par.gewerbe_pkw.value = 30
    t.par.einzelhandel_wege.value = 3000
    t.par.einzelhandel_pkw.value = 60
    t.par.project.value = t.config.active_project
    t.execute()
    print("done")
