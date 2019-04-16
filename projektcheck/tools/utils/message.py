# -*- coding: utf-8 -*-

class Message(object):

    @staticmethod
    def addMessage(message):
        arcpy.AddMessage(message)
        print(message)

    @staticmethod
    def addErrorMessage(message):
        arcpy.AddError(message)
        print(message)

    @staticmethod
    def addWarningMessage(message):
        arcpy.AddWarning(message)
        print(message)

    @staticmethod
    def addIDMessage(message,
                     message_ID,
                     add_argument1=None,
                     add_argument2=None):
        arcpy.AddIDMessage(message,
                           message_ID,
                           add_argument1=add_argument1,
                           add_argument2=add_argument2)
        print(message)

    @staticmethod
    def addGPMessages():
        arcpy.AddMessage('')

    @staticmethod
    def AddMessage(message):
        arcpy.AddMessage(message)
        print(message)

    @staticmethod
    def AddErrorMessage(message):
        arcpy.AddError(message)
        print(message)

    @staticmethod
    def AddWarningMessage(message):
        arcpy.AddWarning(message)
        print(message)

    @staticmethod
    def AddIDMessage(message,
                     message_ID,
                     add_argument1=None,
                     add_argument2=None):
        arcpy.AddIDMessage(message,
                           message_ID,
                           add_argument1=add_argument1,
                           add_argument2=add_argument2)
        print(message)

    @staticmethod
    def AddGPMessages():
        arcpy.AddMessage('')
