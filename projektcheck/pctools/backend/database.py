from abc import ABC

from pctools.utils.singleton import SingletonABCMeta


class Database(ABC):
    '''
    abstract class for managing connection to a database
    '''
    _workspaces = {}
    def __init__(self):
        pass

    def get_workspace(self, name: str):
        return self._workspaces.get(name, None)

    def add_workspace(self, name, path):
        workspace = Workspace(name, path, self)
        self._workspaces[name] = workspace
        return workspace

    def get_table(self, name, workspace: str):
        return NotImplemented

    def __repr__(self):
        table_repr = '\n'.join(['   ' + str(v) for k, v in self._workspaces.items()])
        return '{} {{\n{}\n}}'.format(type(self).__name__, table_repr)


class Workspace:
    def __init__(self, name: str, path, database: Database):
        self.name = name
        self.path = path
        self.database = database

    def get_table(self, name):
        return self.database.get_table(name, self.name)

    def __str__(self):
        ret = '{} - {}'.format(self.name, self.path)
        return ret


class Table:
    '''
    abstract class for a database table
    '''

    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    def get(self):
        return NotImplemented

    def update(self):
        return NotImplemented

    def to_pandas(self):
        return NotImplemented

    def __iter__(self):
        # return the rows here
        return NotImplemented

    def __next__(self):
        return NotImplemented

    def create(self):
        return NotImplemented


class TemporaryTable(Table):
    '''
    temporary table with no database behind
    '''
