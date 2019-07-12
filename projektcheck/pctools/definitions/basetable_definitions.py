# -*- coding: utf-8 -*-

from collections import OrderedDict


class BuildingType(object):
    def __init__(self,
                 typ_id,
                 name,
                 param_we,
                 param_ew_je_we,
                 display_name,
                 default_ew_je_we):
        """
        Gebäudetyp

        Parameters
        ----------
        typ_id : int
        name : str
        param_we : str
        param_ew_je_we : str
        display_name : str
        default_ew_je_we : str
        """
        self.typ_id = typ_id
        self.name = name
        self.param_we = param_we
        self.param_ew_je_we = param_ew_je_we
        self.display_name = display_name
        self.default_ew_je_we = default_ew_je_we


class BuildingTypes(OrderedDict):
    """Get From BaseTable Wohnen_Gebaeudetypen"""
    def __init__(self, database):
        super(BuildingTypes, self).__init__()
        fields = ['IDGebaeudetyp', 'NameGebaeudetyp', 'param_we',
                  'param_ew_je_we', 'display_name', 'default_ew_je_we']
        table = database.get_table(
            'Wohnen_Gebaeudetypen', 'Definition_Projekt',
            fields=fields
        )
        for row in table:
            values = list(row.values())
            self[values[0]] = BuildingType(*values)


class Sortiment(object):
    """Description of a Sortiment"""
    def __init__(self,
                 typ_id,
                 name,
                 param_vfl,
                 kurzname,
                ):
        """
        Gebäudetyp

        Parameters
        ----------
        typ_id : int
        name : str
        param_vfl : str
        kurzname : str
        """
        self.typ_id = typ_id
        self.name = name
        self.param_vfl = param_vfl
        self.kurzname = kurzname


class Sortimente(OrderedDict):
    """Get From BaseTable Einzelhandel_Sortimente"""
    def __init__(self, folders):
        super(Sortimente, self).__init__()
        table = folders.get_base_table(
            'FGDB_Definition_Projekt_Tool.gdb', 'Einzelhandel_Sortimente')
        fields = ['ID_Sortiment_ProjektCheck', 'Name_Sortiment_ProjektCheck',
                  'param_vfl', 'Kurzname']
        rows = arcpy.da.SearchCursor(table, fields)
        for row in rows:
            self[row[0]] = Sortiment(*row)
        del rows


class Branche(object):
    def __init__(self, id, name, param_gewerbenutzung, default_gewerbenutzung):
        self.id = id
        self.name = name
        self.param_gewerbenutzung = param_gewerbenutzung
        self.default_gewerbenutzung = default_gewerbenutzung
        self.estimated_jobs = 0
        self.jobs_per_ha = 0


class Branchen(OrderedDict):
    """Get From BaseTable Wohnen_Gebaeudetypen"""
    def __init__(self, folders):
        super(Branchen, self).__init__()
        table = folders.get_base_table(
            'FGDB_Definition_Projekt_Tool.gdb', 'Gewerbe_branchen')
        fields = ['ID_Branche_ProjektCheck', 'Name_Branche_ProjektCheck',
                  'param_gewerbenutzung', 'default_gewerbenutzung']
        rows = arcpy.da.SearchCursor(table, fields)
        for row in rows:
            self[row[0]] = Branche(*row)
        del rows


class Netzart(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

