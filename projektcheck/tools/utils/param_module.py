# -*- coding: utf-8 -*-

from collections import OrderedDict

from pprint import pformat
import numpy as np


class Param(object):
    '''Dummy-Param-Class'''


class Params(object):
    """Parameter class like an ordered dict"""

    def __init__(self,
                 param_projectname='name',
                 workspace='',
                 *args,
                 **kwargs):
        """
        Parameters
        ----------
        param_projectname : str (optional, default='name')
            the name of the project_name-Parameter
        param_workspace : str (optional)
            the name of the Default Database for the Tool

        Examples
        --------
        >>> params = Params()
        >>> params.param1 = 99
        >>> params.param2 = 42
        >>> params.param3 = 123

        >>> len(params)
        3
        >>> params[0]
        99
        >>> params[1]
        42
        >>> params.param2
        42
        >>> params.param1
        99
        >>> params['param2']
        42
        >>> for param in params:
        ...     print(param)
        99
        42
        123
        >>> del params.param1
        >>> params.param1
        Traceback (most recent call last):
            ...
        AttributeError: Attribute param1 not found in Params-instance. Available attributes are ['param2', 'param3']
        >>> params[0]
        42
        >>> params[1]
        123
        >>> params[2]
        Traceback (most recent call last):
            ...
        IndexError: list index out of range
        >>> del params[0]
        >>> params[0]
        123
        >>> params.param3
        123
        >>> params.param4 = 444
        >>> params.param5 = 555
        >>> params[:2]
        [123, 444]
        >>> params[1:3]
        [444, 555]
        >>> 'param5' in params
        True
        >>> 'param6' in params
        False
        """
        self._od = OrderedDict(*args, **kwargs)
        self._param_projectname = param_projectname
        self._workspace = workspace

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        try:
            return self._od[name]
        except KeyError:
            msg = 'Attribute {} not found in Params-instance. Available attributes are {}'.format(name, self._od.keys())
            raise AttributeError(msg)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
        else:
            self._od[name] = value

    def __delattr__(self, name):
        del self._od[name]

    def __getitem__(self, i):
        try:
            values = self._od.values()
            return values[i]
        except TypeError:
            return self._od[i]

    def __setitem__(self, i, value):
        try:
            items = self._od.items()
            items[i] = value
        except TypeError:
            self._od[i] = value

    def __delitem__(self, i):
        try:
            del self._od[i]
        except KeyError:
            keys = self._od.keys()
            del self._od[keys[i]]

    def __iter__(self):
        return self._od.itervalues()

    def __contains__(self, value):
        return value in self._od

    def __len__(self):
        return len(self._od)

    def __getslice__(self, start, stop):
        return self._od.values().__getslice__(start, stop)

    def __repr__(self):
        ret = self._od.items()
        return pformat(ret)

    def _update_parameters(self, parameters):
        """update the parameter values with a list of parameters"""
        n_params_tbx = len(self)
        n_params_tool = len(parameters)
        msg = '{} Parameter der Toolbox passen nicht zu den {} Parametern des Tools'
        assert n_params_tbx == n_params_tool, msg.format(n_params_tbx,
                                                         n_params_tool)
        # setze die Werte
        for i, key in enumerate(self._od):
            self[key]._arc_object = parameters[i]

    def _get_param_project(self):
        """return the parameter holding the project name,
        return None if project parameter is not used"""
        param_projectname = getattr(self, self._param_projectname, None)
        return param_projectname

    def get_projectname(self):
        """
        return the value for project name parameter if exists, else empty string

        Returns
        -------
        projectname : str

        Examples
        --------
        >>> params = Params(param_projectname='project')
        >>> param = Param()
        >>> param.value = 'Projekt_Name'
        >>> params.project = param
        >>> params._get_projectname()
        'Projekt_Name'
        """
        param_projectname = self._get_param_project()
        if param_projectname:
            return param_projectname.value
        return ''

    def changed(self, *names):
        """check parameter with names if thy are altered and not validated"""
        change = False
        for name in names:
            param = self._od[name]
            if param.altered and not param.hasBeenValidated:
                change = True
        return change

    def toolbox_opened(self):
        """return True if toolbox was opened just before last update"""
        opened = not any([p.hasBeenValidated for p in self])
        #raise Exception(opened)
        return opened

    def selected_index(self, name):
        """get the index of the current selection of given list-parameter"""
        param = self._od[name]
        if param.value not in param.filter.list:
            return -1
        index = param.filter.list.index(param.value)
        return index

    def get_multivalues(self, name):
        """
        return a numpy recarray with the values of a value table

        Parameters
        ----------
        name : str
            the name of the value-table parameter

        Returns
        -------
        ra : np.recarray
            the values as np.recarray. The column names are defined
            by the param.columns
        """
        param = getattr(self, name)
        if not param.datatype == 'GPValueTable':
            raise ValueError('{} is no ValueTable'.format(name))
        column_names = [p[1] for p in param.columns]
        ra = np.rec.fromrecords(param.values, names=column_names)
        return ra

    def set_multivalues(self, name, values):
        """
        set the values of a value table with the values
        given as a recarray

        Parameters
        ----------
        name : str
            the name of the value-table parameter
        values : np.recarray
            the values to assign to the parameter
        """
        msg = 'values must be a recarray and not {}'.format(type(values).__name__)
        assert isinstance(values, np.rec.recarray), msg
        param = getattr(self, name)
        if not param.datatype == 'GPValueTable':
            raise ValueError('{} is no ValueTable'.format(name))
        param.values = values.tolist()



if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
