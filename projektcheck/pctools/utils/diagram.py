import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt
import subprocess
import os
from argparse import ArgumentParser
import sys
import pickle

from pctools.utils.params import DummyTbx, Folders
from pctools.utils import diagram_exec
from pctools.utils.encoding import encode


class Diagram(object):
    _workspace = None

    def __init__(self, **kwargs):
        """
        title : str
        """
        self.title = ''
        self.kwargs = kwargs
        self.tbx = DummyTbx()

    def create(self):
        '''
        create a plot

        kwargs: other optional parameters the subclassing diagram needs
        '''
        self.tbx._getParameterInfo()
        projectname = self.kwargs['projectname'] if 'projectname' in self.kwargs else None
        self.tbx.set_active_project(projectname=projectname)
        if self._workspace:
            self.tbx.folders._workspace = self._workspace

    def show(self):
        pass


class ArcpyDiagram(Diagram):

    def __init__(self, **kwargs):
        """
        title : str
        """
        super(ArcpyDiagram, self).__init__(**kwargs)
        self.graph = None
        self.template = None

    def create(self):
        '''
        create a plot

        Parameters
        ----------
        projectname: str, optional
            the name of the project the data the plot is based on belongs to
            defaults to the active project

        kwargs: other optional parameters the subclassing diagram needs
        '''
        super(ArcpyDiagram, self).create()
        self.graph, self.template = self._create(**self.kwargs)

    def _create(self, **kwargs):
        """to be implemented by subclasses,
        has to return the graph-object and the path to the template"""

    def show(self):
        if not self.graph:
            self.create()
        title = self.graph.graphPropsGeneral.title or self.title
        self.tbx.output.add_graph(self.template, self.graph, title)


class MatplotDiagram(Diagram):
    '''
    superclass to plot diagrams with matplotlib
    '''
    # USE THIS PLT, NEVER IMPORT MATPLOTLIB SOMEWHERE ELSE!!!!
    # (matplotlib needs to be set to PS, as tkinter causes errors and
    # crashes within arcmap)
    folders = Folders()
    # possible stylesheets: 'rpc.mplstyle' and 'rpc2.mplstyle'
    stylesheet = os.path.join(folders.INTERN, 'styles', 'rpc.mplstyle')
    plt = plt
    plt.style.use(stylesheet)
    def __init__(self, **kwargs):
        """
        title : str
        """
        super(MatplotDiagram, self).__init__(**kwargs)
        self.figure = None

    def show(self, external=True):
        '''
        show the created plot in current process or externally in own process

        if not shown in external process, ArcMap will crash

        Parameters
        ----------
        external: bool, optional
            show the plot in an external process
            defaults to True
        '''
        if not self.figure:
            self.create()
        if external:
            filename = os.path.join(self.tbx.folders.TEMPORARY_GDB_PATH,
                                    '{}diagram.pickle'.format(
                                        self.__class__.__name__))
            self.show_external(self.figure, filename)
        else:
            self.plt.show()

    def create(self):
        '''
        create a plot

        Parameters
        ----------
        projectname: str, optional
            the name of the project the data the plot is based on belongs to
            defaults to the active project

        kwargs: other optional parameters the subclassing diagram needs
        '''
        super(MatplotDiagram, self).create()
        self.plt.clf()
        self.figure = self._create(**self.kwargs)

    def show_external(self, plot, filename):
        filename = str(filename)

        if plot is None:
            return
        with open(filename,'wb') as f:
            pickle.dump(plot, f)
        subprocess.Popen(
            [os.path.join(sys.exec_prefix, 'python.exe'),
             '-m' , diagram_exec.__name__, '-f', filename,
             '-t', encode(self.title)], shell=True)

    def _create(self, **kwargs):
        """to be implemented by subclasses,
        has to return the axes-object of the plot"""
