# -*- coding: utf-8 -*-

import arcpy
from tools.utils.encoding import encode
from tools.utils.diagram import ArcpyDiagram


class Dia_Wanderung_Ew(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        """
        Diagramm für die Zuzugsstatistik (Einwohner)
        """
        project_name = self.tbx.par.get_projectname()
        title = encode(
            "{}: Herkunftsorte der Einwohner im Plangebiet"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Zuzugsstatistik')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Zuzugsstatistik_Ew", "FGDB_Einnahmen.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Anzahl",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Wanderung_SvB(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        """
        Diagramm für die Zuzugsstatistik (SvB)
        """
        project_name = self.tbx.par.get_projectname()
        title = encode(
            "{}: Herkunftsorte der Arbeitsplätze im Plangebiet"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Zuzugsstatistik')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Zuzugsstatistik_SvB", "FGDB_Einnahmen.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Anzahl",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template
