# -*- coding: utf-8 -*-
import arcpy
import pandas as pd
import numpy as np

from tools.utils.params import Tbx, Tool
from tools.utils.encoding import encode
from tools.utils.spatial_lib import closest_point


class MassnahmenEditieren(Tool):
    _param_projectname = 'projectname'
    _workspace = 'FGDB_Kosten.gdb'

    def add_outputs(self):
        group_layer = 'infrastruktur'
        fc = 'Erschliessungsnetze_Linienelemente'
        layer = "Erschließungsnetz"
        self.output.add_layer(group_layer, layer, fc, zoom=False)

        fc = 'Erschliessungsnetze_Punktelemente'
        layer = "Erschließungsnetz - punktuelle Maßnahmen"
        self.output.add_layer(group_layer, layer, fc, zoom=False)

        self.output.hide_layer('projektdefinition')

    def run(self):
        df_measures = self.parent_tbx.df_measures
        delete_df = df_measures.loc[df_measures['do_delete'] == True]
        update_df = df_measures.loc[df_measures['do_delete'] == False]

        # deletions
        if len(delete_df) > 0:
            arcpy.AddMessage(u'Lösche Maßnahmen')
        for idx, measure in delete_df.iterrows():
            arcpy.AddMessage(u' - {}'.format(measure['pretty']))
            self.parent_tbx.delete_rows_in_table(
                'Erschliessungsnetze_Punktelemente',
                where='id={}'.format(measure['id']))
        # updates
        arcpy.AddMessage(u'Schreibe Änderungen in Datenbank...')
        self.parent_tbx.dataframe_to_table('Erschliessungsnetze_Punktelemente',
                                           update_df, ['id'], upsert=False)
        arcpy.RefreshActiveView()


class TbxMassnahmenEditieren(Tbx):
    table = 'Erschliessungsnetze_Punktelemente'
    missing_msg = u'keine Maßnahmen vorhanden'

    @property
    def label(self):
        return encode(u'Punktuelle Maßnahme beschreiben')

    @property
    def Tool(self):
        return MassnahmenEditieren

    def _getParameterInfo(self):
        params = self.par

        p = self.add_parameter('projectname')
        p.name = u'Projekt'
        p.displayName = u'Projekt'
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        projects = self.folders.get_projects()
        p.filter.list = projects
        p.value = '' if len(projects) == 0 else p.filter.list[0]

        p = self.add_parameter('measures')
        p.name = encode(u'Maßnahme')
        p.displayName = encode(u'Maßnahme')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        p.filter.list = []

        p = self.add_parameter('name')
        p.name = encode(u'Bezeichnung der Maßnahme')
        p.displayName = encode(u'Bezeichnung der Maßnahme ändern')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'

        self.df_elements = self.table_to_dataframe(
            'Netze_und_Netzelemente', workspace='FGDB_Kosten_Tool.gdb',
            is_base_table=True, where="Typ = 'Punkt'"
        )

        p = self.add_parameter('netzelement')
        p.name = encode(u'Netzelement')
        p.displayName = encode(u'Maßnahme gehört zu folgenden '
                               u'Erschließungsnetz')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        p.filter.list = self.df_elements['Netz'].values.tolist()

        p = self.add_parameter('kosten_eh')
        p.name = u'Kosten der erstmaligen Herstellung (Euro)'
        p.displayName = u'Kosten der erstmaligen Herstellung (Euro)'
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPDouble'

        p = self.add_parameter('kosten_bu')
        p.name = encode(u'Jährliche Kosten für Betrieb und Unterhaltung (Euro)')
        p.displayName = encode(u'Jährliche Kosten für '
                               u'Betrieb und Unterhaltung (Euro)')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPDouble'

        p = self.add_parameter('kosten_en')
        p.name = encode(u'Erneuerungskosten nach Ablauf der Lebensdauer (Euro)')
        p.displayName = encode(u'Erneuerungskosten nach Ablauf der '
                               u'Lebensdauer (Euro)')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPDouble'

        p = self.add_parameter('lebensdauer')
        p.name = encode(u'Technische oder wirtschaftliche Lebensdauer bis '
                        u'zur Erneuerung (Jahre)')
        p.displayName = encode(u'Technische oder wirtschaftliche Lebensdauer '
                               u'bis zur Erneuerung (Jahre)')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPLong'
        p.filter.type = 'Range'
        p.filter.list = [1, 100]
        p.value = 1

        param = self.add_parameter('do_delete')
        param.name = encode(u'Löschen')
        param.displayName = encode(u'Maßnahme entfernen')
        param.parameterType = 'Optional'
        param.direction = 'Input'
        param.datatype = u'GPBoolean'

        param = self.add_parameter('delete_all')
        param.name = encode(u'Alle Löschen')
        param.displayName = encode(u'alle Maßnahmen entfernen')
        param.parameterType = 'Optional'
        param.direction = 'Input'
        param.datatype = u'GPBoolean'

        return params

    def add_measure_to_db(self, name, coords):
        '''add a measure to the database located in given coordinates'''
        df_measures = self.get_measures()
        if len(df_measures) == 0:
            new_id = 1
        else:
            new_id = df_measures['id'].max() + 1
        columns = df_measures.columns
        new_measure = pd.DataFrame(np.zeros((1, len(columns))), columns=columns)
        new_measure['id'] = new_id
        new_measure['Bezeichnung'] = name
        new_measure['SHAPE'] = [coords]

        new_measure['Euro_EH'] = 0.
        new_measure['Cent_BU'] = 0.
        new_measure['Euro_EN'] = 0.
        new_measure['Lebensdauer'] = 1
        # default: "Straße (innere Erschließung)"
        new_measure['IDNetz'] = 1
        new_measure['IDNetzelement'] = 13
        self.insert_dataframe_in_table('Erschliessungsnetze_Punktelemente',
                                       new_measure)

    def get_measures(self):
        df_measures = self.table_to_dataframe(
            'Erschliessungsnetze_Punktelemente')
        return df_measures

    def _open(self, params):
        # reset measures dataframe on opening of toolbox
        self.df_measures = self.get_measures()
        self.df_measures['do_delete'] = False
        self.df_measures.sort(columns=['IDNetzelement', 'id'], inplace=True)
        if len(self.df_measures) == 0:
            return

        # check, if there is a specific location set (most likely via addin)
        x, y = self.config.active_coord
        closest_idx = None
        if x and y:
            closest_idx, c = closest_point(
                (x, y), self.df_measures['SHAPE'].values)

        # update the names of the measures and list them
        pretty_names = []
        for idx, measure in self.df_measures.iterrows():
            pretty = self.get_pretty_measure_name(measure)
            pretty_names.append(pretty)
        self.df_measures['pretty'] = pretty_names
        self.update_measures_list(closest_idx)
        self.set_selected_measure_inputs()

    def get_pretty_measure_name(self, measure):
        '''assemble a meaningful name for the measure incl. name and additional
        informations'''
        idx = self.df_elements['IDNetzelement'] == measure['IDNetzelement']
        net_name = self.df_elements['Netz'][idx].values[0]
        pretty = u'{net} - "{name}" ({id})'.format(
            id=measure['id'], name=measure['Bezeichnung'], net=net_name)
        if measure['do_delete']:
            pretty += u' - WIRD ENTFERNT'
        return pretty

    def update_measures_list(self, idx=None):
        '''update the input list of measures with pretty names in dataframe'''
        if idx is None:
            idx = self.par.measures.filter.list.index(
                self.par.measures.value) if self.par.measures.value else 0
        # sort by net id, keep id of measure with given idx
        m_id = self.df_measures.iloc[idx]['id']
        self.df_measures.sort(columns=['IDNetzelement', 'id'], inplace=True)
        new_idx = np.where(self.df_measures['id'] == m_id)[0][0]
        pretty = self.df_measures['pretty'].values.tolist()
        self.par.measures.filter.list = pretty
        self.par.measures.value = pretty[new_idx]

    def set_selected_measure_inputs(self):
        '''set all input fields to match data of currently selected measure'''
        self.par.delete_all.value = False
        measure_idx = self.df_measures['pretty'] == self.par.measures.value
        measure = self.df_measures.loc[measure_idx]

        self.par.name.value = measure['Bezeichnung'].values[0]
        self.par.kosten_eh.value = measure['Euro_EH'].values[0]
        self.par.kosten_bu.value = measure['Cent_BU'].values[0] / 100
        self.par.kosten_en.value = measure['Euro_EN'].values[0]
        # a big arcpy mystery again: cast to int required else
        # arcpy just ignores setting the value
        self.par.lebensdauer.value = int(measure['Lebensdauer'].values[0])

        element_idx = (self.df_elements['IDNetzelement'] ==
                       measure['IDNetzelement'].values[0])
        net_name = self.df_elements['Netz'][element_idx]
        self.par.netzelement.value = net_name.values[0]

        do_delete = measure['do_delete'].values[0]
        self.par.do_delete.value = True if do_delete else False

    def validate_inputs(self):
        df_measures = self.get_measures()
        if len(df_measures) == 0:
            msg = (u'Es sind keine punktuellen Maßnahmen vorhanden.')
            return False, msg
        return True, ''

    def _updateParameters(self, params):
        if len(self.df_measures) == 0:
            return
        measure_idx = self.df_measures['pretty'] == self.par.measures.value

        if self.par.changed('name'):
            self.df_measures.loc[
                measure_idx, 'Bezeichnung'] = self.par.name.value
        elif self.par.changed('kosten_eh'):
            self.df_measures.loc[
                measure_idx, 'Euro_EH'] = self.par.kosten_eh.value
        elif self.par.changed('kosten_bu'):
            self.df_measures.loc[
                measure_idx, 'Cent_BU'] = self.par.kosten_bu.value * 100
        elif self.par.changed('kosten_en'):
            self.df_measures.loc[
                measure_idx, 'Euro_EN'] = self.par.kosten_en.value
        elif self.par.changed('lebensdauer'):
            self.df_measures.loc[
                measure_idx, 'Lebensdauer'] = self.par.lebensdauer.value

        elif self.par.changed('netzelement'):
            idx = self.df_elements['Netz'] == self.par.netzelement.value
            element = self.df_elements[idx]
            element_id = element['IDNetzelement'].values[0]
            net_id = element['IDNetz'].values[0]
            self.df_measures.loc[measure_idx, 'IDNetzelement'] = element_id
            self.df_measures.loc[measure_idx, 'IDNetz'] = net_id

        elif self.par.changed('do_delete'):
            do_delete = self.par.do_delete.value
            self.df_measures.loc[measure_idx, 'do_delete'] = do_delete

        elif self.par.changed('delete_all'):
            delete_all = self.par.delete_all.value
            self.par.do_delete.value = delete_all
            self.df_measures['do_delete'] = delete_all
            for index, measure in self.df_measures.iterrows():
                pretty = self.get_pretty_measure_name(measure)
                self.df_measures.loc[index, 'pretty'] = pretty
            self.update_measures_list()

        # update the pretty names of the selected measure
        if (self.par.changed('name') or
            self.par.changed('netzelement') or
            self.par.changed('do_delete')):
            i = np.where(measure_idx == True)[0][0]
            pretty = self.get_pretty_measure_name(
                self.df_measures.iloc[i])
            self.df_measures.loc[measure_idx, 'pretty'] = pretty
            self.update_measures_list()

        # measure changed -> change values of input fields
        if self.par.changed('measures'):
            self.set_selected_measure_inputs()
        return params

    def _updateMessages(self, params):
        valid, msg = self.validate_inputs()
        if not valid:
            self.par.projectname.setErrorMessage(msg)

if __name__ == '__main__':
    from time import time
    start = time()
    t = TbxMassnahmenEditieren()
    t.getParameterInfo()
    t.set_active_project()
    t.open()
    t.execute()
