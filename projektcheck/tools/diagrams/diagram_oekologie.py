# -*- coding: utf-8 -*-

import arcpy
from tools.utils.encoding import encode
from tools.utils.diagram import ArcpyDiagram


class Dia_Integrationsgrad(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            "{}: Anteil der Plangebietsgrenze (in Prozent), der ..."
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Integrationsgrad')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Integrationsgrad", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesPie(dataSrc=input_data,
                                   fieldValue = "Umfang",
                                   fieldLabel="Grenze")
        graph.graphPropsGeneral.title = title
        return graph, input_template


class Dia_Wohndichte(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Wohneinheiten pro Hektar Nettowohnbauland"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Wohndichte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Wohndichte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Wohndichte",
                                   fieldLabel="Typ")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Wohnflaechendichte(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: qm Wohnfläche pro Hektar Nettowohnbauland"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Wohnflaechendichte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Wohnflaechendichte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Wohnflaechendichte",
                                   fieldLabel="Typ")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Nullfall(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenbedeckung im Nullfall"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenbedeckung')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Bodenbedeckung_Zeichnung", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Nullfall",
                                   fieldLabel="Bodenbedeckung")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Planfall(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenbedeckung im Planfall"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenbedeckung')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Bodenbedeckung_Zeichnung", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Planfall",
                                   fieldLabel="Bodenbedeckung")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Waerme(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenkennwert Wärmespeicherung"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenkennwerte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Leistungskennwerte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Waermespeicherung",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Staub(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenkennwert Staubbindevermögen"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenkennwerte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Leistungskennwerte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Staubbindevermoegen",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Grundwasser(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenkennwert Grundwasserneubildung"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenkennwerte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Leistungskennwerte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Grundwasserneubildung",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Schadstoff(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenkennwert Schadstoffrückhaltung"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenkennwerte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Leistungskennwerte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Schadstoffrueckhaltung",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Durchlaessigkeit(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenkennwert Durchlässigkeit"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenkennwerte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Leistungskennwerte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Durchlaessigkeit",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Ueberformung(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenkennwert Bodenüberformung"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenkennwerte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Leistungskennwerte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Bodenueberformung",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Abfluss(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenkennwert Oberflächenabfluss"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenkennwerte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Leistungskennwerte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Oberflaechenabfluss",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Regenwasser(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenkennwert Regenwasserversickerung"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenkennwerte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Leistungskennwerte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Regenwasserversickerung",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template

class Dia_Biotop(ArcpyDiagram):
    _workspace = 'FGDB_Definition_Projekt.gdb'

    def _create(self, **kwargs):
        project_name = self.tbx.par.get_projectname()
        title = encode(
            u"{}: Bodenkennwert Biotopausbildungsvermögen"
            .format(project_name))
        input_template = self.tbx.folders.get_diagram_template(
            'Bodenkennwerte')

        graph = arcpy.Graph()
        input_data = self.tbx.folders.get_table("Leistungskennwerte", "FGDB_Flaeche_und_Oekologie.gdb")
        graph.addSeriesBarVertical(dataSrc=input_data,
                                   fieldY= "Biotopausbildungsvermoegen",
                                   fieldLabel="Kategorie")
        graph.graphPropsGeneral.title = title
        return graph, input_template
