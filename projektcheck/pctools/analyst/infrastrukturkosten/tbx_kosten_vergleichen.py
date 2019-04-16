# -*- coding: utf-8 -*-
import os
import arcpy
import pandas as pd
import numpy as np

from pctools.utils.params import Tbx, Tool
from pctools.utils.encoding import encode
from pctools.utils.constants import Nutzungsart
from pctools.diagrams.infrastruktur import (VergleichAPDiagramm,
                                             VergleichWEDiagramm)
from pctools.analyst.infrastrukturkosten.tbx_gesamtkosten import Gesamtkosten


class KostenVergleichen(Gesamtkosten):
    _param_projectname = 'projectname'
    _workspace = 'FGDB_Kosten.gdb'

    def add_outputs(self):

        df_areas = self.parent_tbx.table_to_dataframe(
            'Teilflaechen_Plangebiet',
            workspace='FGDB_Definition_Projekt.gdb',
            columns=['Nutzungsart'],
            where='Nutzungsart <> {}'.format(Nutzungsart.UNDEFINIERT)
        )

        if len(df_areas) == 0:
            return

        unique_tou = df_areas['Nutzungsart'].unique()
        if len(unique_tou) == 1:
            tou = unique_tou[0]
            if tou == Nutzungsart.GEWERBE:
                diagram = VergleichAPDiagramm()
                self.output.add_diagram(diagram)
            elif tou == Nutzungsart.WOHNEN:
                diagram = VergleichWEDiagramm()
                self.output.add_diagram(diagram)

    def run(self):
        super(KostenVergleichen, self).run()


class TbxKostenVergleichen(Tbx):

    @property
    def label(self):
        return encode(u'Kosten pro Wohneinheit bzw. Arbeitsplatz vergleichen')

    @property
    def Tool(self):
        return KostenVergleichen

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
        return params

    def get_areas(self):
        df_areas = self.table_to_dataframe(
            'Teilflaechen_Plangebiet',
            workspace='FGDB_Definition_Projekt.gdb',
            columns=['Nutzungsart', 'WE_gesamt', 'AP_gesamt'],
            where='Nutzungsart <> {}'.format(Nutzungsart.UNDEFINIERT)
        )
        return df_areas

    def validate_inputs(self):
        df_areas = self.get_areas()

        if len(df_areas) == 0:
            err_msg = (u'Es wurden keine Flächen mit definierten Nutzungsarten '
                       u'gefunden.')
            return False, err_msg

        unique_tou = df_areas['Nutzungsart'].unique()
        if len(unique_tou) > 1:
            err_msg = (u'Die Funktion steht leider nur für Projekte zur '
                       u'Verfügung, bei denen alle Teilflächen die gleiche '
                       u'Nutzung (Wohnen oder Gewerbe) haben.')
            return False, err_msg

        tou = unique_tou[0]
        if tou == Nutzungsart.EINZELHANDEL:
            err_msg = (u'Für die Nutzung "Einzelhandel" stehen leider keine '
                       u'Vergleichswerte zur Verfügung.')
            return False, err_msg

        if tou == Nutzungsart.WOHNEN:
            if df_areas['WE_gesamt'].sum() == 0:
                err_msg = (u'Um die Funktion zu nutzen, müssen Sie zunächst '
                           u'festlegen, wie viele Wohnungen auf den '
                           u'Teilflächen Ihres Projekts gebaut werden sollen')
                return False, err_msg

        elif tou == Nutzungsart.GEWERBE:
            if df_areas['AP_gesamt'].sum() == 0:
                err_msg = (u'Um die Funktion zu nutzen, müssen Sie zunächst '
                           u'festlegen, wie viele Arbeitsplätze auf den '
                           u'Teilflächen Ihres Projekts angesiedelt '
                           u'werden sollen.')
                return False, err_msg
        return True, ''

if __name__ == "__main__":
    t = TbxKostenVergleichen()
    t.getParameterInfo()
    t.set_active_project()
    msg = t.validate_inputs()
    t.execute()
