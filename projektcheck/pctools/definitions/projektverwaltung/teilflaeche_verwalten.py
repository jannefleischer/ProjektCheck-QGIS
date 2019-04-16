# -*- coding: utf-8 -*-

import arcpy
import os
from collections import OrderedDict

from pctools.utils.params import Tool
from pctools.diagrams.diagram_teilflaechen import DiaTeilflaechen
from pctools.utils.constants import Nutzungsart
from pctools.analyst.standortkonkurrenz.tbx_osm_markteinlesen import MarktEinlesen


class TeilflaechenVerwalten(Tool):

    _param_projectname = 'projectname'
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def add_outputs(self):
        arcpy.RefreshActiveView()

    def run(self):
        df_areas = self.parent_tbx.df_areas
        df_areas_old = self.parent_tbx.table_to_dataframe('Teilflaechen_Plangebiet')
        market_tool = None
        # delete former entries when type of use was changed
        for index, area in df_areas.iterrows():
            tou_id = area['Nutzungsart']
            area_id = area['id_teilflaeche']
            tou_changed = (df_areas.loc[index]['Nutzungsart'] !=
                           df_areas_old.loc[index]['Nutzungsart'])

            if not tou_changed:
                continue
            arcpy.AddMessage(u'Die Nutzungsart von Fläche "{}" hat sich '
                             u'geändert. Bereinige eventuelle bereits '
                             u'berechnete Ergebnisse und Einstellungen...'
                             .format(area['Name']))

            df_areas.loc[index, 'Wege_gesamt'] = 0
            df_areas.loc[index, 'Wege_MIV'] = 0
            df_areas.loc[index, 'ew'] = 0

            # remove table entries eventually stored for this area
            # (may exist if it was defined as a different type before)
            if tou_id != Nutzungsart.WOHNEN:
                tables = ['Wohnen_WE_in_Gebaeudetypen',
                          'Wohnen_Struktur_und_Alterung_WE']
                for table in tables:
                    self.parent_tbx.delete_rows_in_table(
                        table, pkey=dict(IDTeilflaeche=area_id))
                df_areas.loc[index, 'WE_gesamt'] = 0
            if tou_id != Nutzungsart.GEWERBE:
                tables = ['Gewerbe_Anteile', 'Gewerbe_Arbeitsplaetze']
                for table in tables:
                    self.parent_tbx.delete_rows_in_table(
                        table, pkey=dict(IDTeilflaeche=area_id))
                df_areas.loc[index, 'AP_gesamt'] = 0
            if tou_id != Nutzungsart.EINZELHANDEL:
                table = 'Einzelhandel_Verkaufsflaechen'
                self.parent_tbx.delete_rows_in_table(
                    table, pkey=dict(IDTeilflaeche=area_id))
                df_areas.loc[index, 'VF_gesamt'] = 0
                # delete markets eventually belonging to the area
                if not market_tool:
                    market_tool = MarktEinlesen(projectname=self.projectname)
                market_tool.delete_area_market(area_id)

        self.parent_tbx.dataframe_to_table('Teilflaechen_Plangebiet',
                                           df_areas, ['id_teilflaeche'],
                                           upsert=False)

        # reset entries in Einkommenschronik
        chronik = self.folders.get_table("Chronik_Nutzung", "FGDB_Einnahmen.gdb")
        cursor = arcpy.da.UpdateCursor(chronik, ["Letzte_Nutzung"])
        for row in cursor:
            row[0] = None
            cursor.updateRow(row)
        del cursor
