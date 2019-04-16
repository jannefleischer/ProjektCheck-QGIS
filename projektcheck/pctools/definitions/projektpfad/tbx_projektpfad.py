# -*- coding: utf-8 -*-
import arcpy
import os

from pctools.utils.config import Config
from pctools.utils.params import Tbx, Tool


class ProjectFolder(Tool):

    def run(self):
        config = Config()
        tbx = self.parent_tbx
        if not tbx._writeable:
            arcpy.AddError("Für den von Ihnen angegebenen Dateipfad besitzen "
                           "Sie keine Schreibrechte. Bitte geben Sie einen "
                           "anderen Pfad an!")
            return
        config.project_folder = str(tbx.par.folderpath.value)
        projects = self.folders.get_projects()
        config.active_project = projects[0] if projects else ''


    def add_outputs(self):
        pass


class TbxProjectFolder(Tbx):
    _writeable = True

    def __init__(self):
        super(TbxProjectFolder, self).__init__()
        self.requires_existing_project = False
        self.requires_existing_project_path = False

    @property
    def label(self):
        return u'Speicherort für Ihre Projekte'

    @property
    def Tool(self):
        return ProjectFolder

    def _open(self, params):
        p = params.folderpath
        project_folder = self.config.project_folder
        p.value = project_folder

    def _getParameterInfo(self):
        params = self.par
        p = self.add_parameter('folderpath')
        p.name = u'folderpath'
        p.displayName = u'Speicherort für alle Ihre benutzerdefinierten ' + \
            'Projekte (Pfad zu einem Ordner)'
        p.parameterType = 'Required'
        p.direction = 'Input'
        p.datatype = 'DEFolder'
        p.value = ''

        p = self.add_parameter('dummy')
        p.name = u'dummy'
        p.direction = 'Input'
        p.parameterType = 'Required'
        p.datatype = 'GPBoolean'
        p.enabled = False
        p.value = False

        return params

    def _updateParameters(self, params):
        pass

    def _updateMessages(self, params):
        par = self.par
        if par.changed('folderpath'):
            err = ''
            if not os.path.exists(str(par.folderpath.value)):
                err = 'Der Pfad existiert nicht.'
            else:
                try:
                    test_path = str(par.folderpath.value) + \
                        r'\writability_test.txt'
                    testfile = open(test_path, 'w+')
                    testfile.close()
                    os.remove(test_path)
                    self._writeable = True
                except:
                    self._writeable = False
                    arcpy.AddMessage(str(par.folderpath.value))
                    err = u'Sie besitzen keine Schreibrechte für diesen Pfad!'
            if err:
                par.folderpath.setErrorMessage(err)

if __name__ == "__main__":
    t = TbxProjectFolder()
    parameters = t._getParameterInfo()
    t.updateParameters(parameters)
