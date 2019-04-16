# -*- coding: utf-8 -*-
import arcpy

from pctools.utils.params import Tool, Tbx
from pctools.utils.spatial_lib import get_project_centroid, Point
from pctools.utils.encoding import encode
from pctools.analyst.erreichbarkeit.geoserver_query import GeoserverQuery


class Einrichtungen(Tool):
    _param_projectname = 'projectname'
    _workspace = 'FGDB_Erreichbarkeit.gdb'
    cutoff = None

    categories = [u'Kita', u'Autobahnanschlussstelle', u'Dienstleistungen',
                  u'Ärzte', 'Freizeit', u'Läden',
                  u'Supermarkt/Einkaufszentrum', 'Schule']

    def add_outputs(self):
        group_layer = ("erreichbarkeit")
        fc = 'Einrichtungen'
        layer = 'Einrichtungen'
        self.output.add_layer(group_layer, layer, fc,
                              template_folder='Erreichbarkeit',
                              zoom=True)

    def run(self):
        query = GeoserverQuery()
        radius = self.par.radius.value * 1000
        x, y = get_project_centroid(self.par.projectname.value)
        centroid = Point(x, y, epsg=self.parent_tbx.config.epsg)
        target_epsg = self.parent_tbx.config.epsg
        arcpy.AddMessage('Frage Geoserver an...')
        features = query.get_features(centroid, radius,
                                      self.categories, target_epsg)
        arcpy.AddMessage('Schreibe {} Einrichtungen in die Datenbank...'
                         .format(len(features)))
        self.parent_tbx.delete_rows_in_table('Einrichtungen')
        column_values = {'name': [], 'SHAPE': [], 'projektcheck_category': []}
        for feat in features:
            column_values['name'].append(feat.name)
            feat.create_geom()
            column_values['SHAPE'].append(feat.geom)
            column_values['projektcheck_category'].append(feat.category)

        self.parent_tbx.insert_rows_in_table('Einrichtungen', column_values)


class TbxEinrichtungen(Tbx):
    @property
    def label(self):
        return encode(u'Einrichtungen in der Umgebung ermitteln und einblenden')

    @property
    def Tool(self):
        return Einrichtungen

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

        param = self.add_parameter('radius')
        param.name = encode(u'radius')
        param.displayName = encode(u'Radius in Kilometern')
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'GPLong'
        param.filter.type = 'Range'
        param.filter.list = [1, 20]
        param.value = 10

        return params

if __name__ == '__main__':
    t = TbxEinrichtungen()
    params = t.getParameterInfo()
    t.set_active_project()
    t.open()
    t.execute()
