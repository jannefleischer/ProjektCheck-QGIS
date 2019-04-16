# -*- coding: utf-8 -*-

from os.path import abspath, dirname, join
from collections import OrderedDict
import arcpy
import numpy as np

from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.definitions.projektverwaltung.teilflaeche_verwalten import (
    TeilflaechenVerwalten)
from tools.utils.constants import Nutzungsart


class TbxFlaechendefinition(Tbx):
    # filters the available teilflaechen by the id of the nutzungsart
    # (None for access to all teilflaechen)
    _nutzungsart = None
    # the available teilflaechen are stored here
    _teilflaechen = None
    _nutzungsarten = None
    _recently_opened = True

    def _getParameterInfo(self):
        # Projekt
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

        # Teilfläche
        p = self.add_parameter('area')
        p.name = encode(u'Teilfläche')
        p.displayName = encode(u'Teilfläche')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        p.filter.list = []

        self.df_types_of_use = self.table_to_dataframe(
            'Nutzungsarten', workspace='FGDB_Definition_Projekt_Tool.gdb',
            is_base_table=True
        )

        return params

    def get_areas(self, nutzungsart=None):
        where = 'Nutzungsart = {}'.format(nutzungsart) if nutzungsart else None
        df_areas = self.table_to_dataframe('Teilflaechen_Plangebiet',
                                           workspace='FGDB_Definition_Projekt.gdb',
                                           where=where)
        return df_areas

    def _open(self, params):
        self.df_areas = self.get_areas(self._nutzungsart)
        pretty_names = [self.get_pretty_area_name(area) for
                        idx, area in self.df_areas.iterrows()]
        self.df_areas['pretty'] = pretty_names
        self.update_area_list()
        self.set_selected_area()

    def get_selected_area(self):
        '''return the currently selected area as a Series and
        it's index in the list of areas
        '''
        area_idx = self.df_areas['pretty'] == self.par.area.value
        # if user changed name in dropdown you won't find the name in the list
        if area_idx.sum() == 0:
            return None, -1
        idx = np.where(area_idx==True)[0][0]
        area = self.df_areas.iloc[idx]
        return area, idx

    def set_selected_area(self):
        '''set the inputs for the currently selected area '''
        raise NotImplementedError

    def get_pretty_area_name(self, area):
        '''assemble a meaningful name for the area incl. name and additional
        informations'''
        idx = self.df_types_of_use['id'] == area['Nutzungsart']
        type_of_use = self.df_types_of_use['nutzungsart'][idx].values[0]
        pretty = u'"{name}" ({id}) | {gemeinde} | {ha} ha | {tou}'.format(
            id=area['id_teilflaeche'],
            name=area['Name'],
            ha=round(area['Flaeche_ha'], 2),
            gemeinde=area['gemeinde_name'],
            tou=type_of_use
        )
        suffix = ''
        if self._nutzungsart == Nutzungsart.WOHNEN:
            n = int(area['WE_gesamt']) or 'NICHT DEFINIERT'
            suffix = ' | Wohneinheiten: {}'.format(n)
        if self._nutzungsart == Nutzungsart.GEWERBE:
            n = int(area['AP_gesamt']) or 'NICHT DEFINIERT'
            suffix = u' | Arbeitsplätze: {}'.format(n)
        if self._nutzungsart == Nutzungsart.EINZELHANDEL:
            n = u'{} m²'.format(int(area['VF_gesamt'])) if area['VF_gesamt'] \
                else 'NICHT DEFINIERT'
            suffix = u' | Verkaufsfläche: {}'.format(n)
        pretty += suffix
        return pretty

    def update_pretty_name(self):
        area, idx = self.get_selected_area()
        # something changed -> update pretty representation of selected area
        # and update list as well (to show new pretty repr.)
        pretty = self.get_pretty_area_name(area)
        self.df_areas.loc[idx, 'pretty'] = pretty
        self.update_area_list()

    def update_area_list(self, idx=None):
        """update the list of areas and select the area with index if given"""
        if idx is None:
            idx = self.par.area.filter.list.index(
                self.par.area.value) if self.par.area.value else 0
        pretty = self.df_areas['pretty'].values.tolist()
        self.par.area.filter.list = pretty
        self.par.area.value = pretty[idx]

    def _updateParameters(self, params):
        if params.changed('projectname'):
            self._open(params)

        elif params.changed('area'):
            self.set_selected_area()

        return params

    def validate_inputs(self):
        df_areas = self.get_areas(self._nutzungsart)
        if len(df_areas) == 0:
            if self._nutzungsart:
                idx = self.df_types_of_use['id'] == self._nutzungsart
                tou = self.df_types_of_use[idx]['nutzungsart'].values[0]
                tou_str = ' mit der Nutzungsart {}'.format(tou)
            else:
                tou_str = ''
            msg = (u'Es sind keine Flächen{} definiert!'.format(tou_str))
            return False, msg
        return True, ''

    #if not self._get_teilflaechen(nutzungsart=self._nutzungsart):
        #
        #msg = (u'Keine Teilflächen mit der '
                       #u'Nutzungsart "{}" definiert.'.format(nutzung))
        #return False, msg

    def _updateMessages(self, params):
        valid, msg = self.validate_inputs()
        if not valid:
            self.par.projectname.setErrorMessage(msg)


class TbxTeilflaecheVerwalten(TbxFlaechendefinition):
    """Toolbox to name Teilflächen and define their 'nutzungen'"""

    @property
    def label(self):
        return u'Nutzungen auf Teilflächen definieren'

    @property
    def Tool(self):
        return TeilflaechenVerwalten

    def _getParameterInfo(self):
        params = super(TbxTeilflaecheVerwalten, self)._getParameterInfo()
        # Name
        p = self.add_parameter('name')
        p.name = u'Name'
        p.displayName = u'Name'
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'

        # Nutzungsart
        p = self.add_parameter('type_of_use')
        p.name = encode(u'Nutzungsart')
        p.displayName = encode(u'Nutzungsart')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'
        p.filter.list = self.df_types_of_use['nutzungsart'].values.tolist()

        return params

    def _updateParameters(self, params):
        params = super(TbxTeilflaecheVerwalten, self)._updateParameters(params)

        area, idx = self.get_selected_area()
        if area is None:
            return params

        #if params.changed('area') and self.par.area.filter.list:
            #selected, idx = self.get_selected_area()
            #pretty = self.get_pretty_area_name(selected)
            #self.df_areas.loc[idx, 'pretty'] = pretty
            #self.update_area_list()

        if params.changed('name'):
            self.df_areas.loc[idx, 'Name'] = self.par.name.value

        elif params.changed('type_of_use'):
            tou_idx = (self.df_types_of_use['nutzungsart'] ==
                       self.par.type_of_use.value)
            tou_id = self.df_types_of_use[tou_idx]['id'].values[0]
            self.df_areas.loc[idx, 'Nutzungsart'] = tou_id

        if params.changed('name') or params.changed('type_of_use'):
            self.update_pretty_name()

        return params

    def set_selected_area(self):
        '''set the inputs for the currently selected area '''
        area, i = self.get_selected_area()
        tou_idx = self.df_types_of_use['id'] == area['Nutzungsart']
        type_of_use = self.df_types_of_use.loc[tou_idx]['nutzungsart'].values[0]
        self.par.name.value = area['Name']
        self.par.type_of_use.value = type_of_use


if __name__ == '__main__':

    t = TbxTeilflaecheVerwalten()
    t.getParameterInfo()
    t.set_active_project(projectname=u'Häüß')
    t.open()
    t._updateParameters(t.par)
    t.execute()
