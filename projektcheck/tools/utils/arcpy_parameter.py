# -*- coding: utf-8 -*-


class Parameter(object):
    """Patch problems with capital letters in the arcpy-parameter"""
    def _get_gp_fixargs(self, args):
        from arcpy.geoprocessing._base import gp_fixargs
        fixed_args = gp_fixargs(args)
        return fixed_args

    def setErrorMessage(self, *args):
        try:
            return super(Parameter, self).setErrorMessage(*args)
        except AttributeError:
            fixed_args = self._get_gp_fixargs(args)
            ao = self._arc_object.setErrorMessage(*fixed_args)
        return convertArcObjectToPythonObject(ao)

    def setWarningMessage(self, *args):
        try:
            return super(Parameter, self).setWarningMessage(*args)
        except AttributeError:
            fixed_args = self._get_gp_fixargs(args)
            ao = self._arc_object.setWarningMessage(*fixed_args)
        return convertArcObjectToPythonObject(ao)

    def setIDMessage(self, *args):
        try:
            return super(Parameter, self).setIDMessage(*args)
        except AttributeError:
            fixed_args = self._get_gp_fixargs(args)
            ao = self._arc_object.setIDMessage(*fixed_args)
        return convertArcObjectToPythonObject(ao)

    def clearMessage(self, *args):
        try:
            return super(Parameter, self).clearMessage(*args)
        except AttributeError:
            fixed_args = self._get_gp_fixargs(args)
            ao = self._arc_object.clearMessage(*fixed_args)
        return convertArcObjectToPythonObject(ao)

    def hasError(self, *args):
        try:
            return super(Parameter, self).hasError(*args)
        except AttributeError:
            fixed_args = self._get_gp_fixargs(args)
            ao = self._arc_object.hasError(*fixed_args)
        return convertArcObjectToPythonObject(ao)

    def hasWarning(self, *args):
        try:
            return super(Parameter, self).hasWarning(*args)
        except AttributeError:
            fixed_args = self._get_gp_fixargs(args)
            ao = self._arc_object.hasWarning(*fixed_args)
        return convertArcObjectToPythonObject(ao)

    def isInputValueDerived(self, *args):
        try:
            return super(Parameter, self).isInputValueDerived(*args)
        except AttributeError:
            fixed_args = self._get_gp_fixargs(args)
            ao = self._arc_object.isInputValueDerived(*fixed_args)
        return convertArcObjectToPythonObject(ao)
