# -*- coding: utf-8 -*-
import os
import sys
import arcpy

from tools.utils.params import Tbx
from tools.utils.encoding import encode

from tools.analyst.verkehr.routing import Routing


class TbxRouting(Tbx):

    @property
    def label(self):
        return encode(u'Straßenverkehrsbelastung schätzen')

    @property
    def Tool(self):
        return Routing

    def _getParameterInfo(self):

        params = self.par
        projekte = self.folders.get_projects()

        # Projekt_auswählen
        p = self.add_parameter('project')
        p.name = u'Projekt_auswählen'.encode('cp1252')
        p.displayName = u'Projekt'.encode('cp1252')
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = u'GPString'

        p.filter.list = projekte
        if projekte:
            p.value = projekte[0]

        # inner radius
        p = self.add_parameter('inner')
        p.name = u'inner_circle'
        p.displayName = u'Entfernung der Herkunfts-/Zielpunkte vom ' +\
            u'Mittelpunkt des Plangebiets (in Metern Straßenentfernung)'
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = 'GPLong'
        p.filter.type = 'Range'
        p.filter.list = [1000, 3000]
        p.value = 1500

        return params


    def _updateParameters(self, params):
        return


if __name__ == "__main__":
    t = TbxRouting()
    t.getParameterInfo()
    t.par.project.value = t.config.active_project
    t.execute()


    print 'done'
