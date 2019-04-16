import arcpy
from arcpy import env
import numpy as np




class Read_FGDB(object):


    def __init__(self, gdb_path, table, columns, clause=None, header=0):
        self.gdb_path = gdb_path
        self.table = table
        self.columns = columns
        self.clause = clause
        self.result_block = []
        self.header = header

    def get_result_block(self):
        """
        Extract data from gdb.

        Parameters
        ----------
        gdb_path : str
            Path to GDB
        table : str
            Table inside the GDB
        columns : np.array of str
            Columns inside the table

        Returns
        -------
        result_block : np.array of str
            Extracted data from GDB
        """
        env.workspace = self.gdb_path
        result_block = self.columns
        with arcpy.da.SearchCursor(self.table, self.columns,
                                   where_clause=self.clause) as cur:
            for cols in cur:
                new_row = np.array(cols)
                result_block = np.vstack((result_block, new_row))
        # delete header
        if not self.header:
            result_block = np.delete(result_block, 0, axis=0)
        # overwrite self.result_block
        self.result_block = result_block


    def sort_results_by_col(self, col):
        """
        """
        self.result_block[self.header:, :] = self.result_block[self.header:, :]\
            [self.result_block[self.header:, col].argsort()]



def calc_weighted_mean(Data, Nutzungsart=None):
    """
    Calculates the weighted mean coordinates for areas with the same
    'Nutzungsart'

    Parameters
    ----------
    Data : np.array of str
        Input data; Columns: Nutzungsart, Flaeche_ha, INSIDE_X, INSIDE_Y
    Nutzungsart : int, optional
        Only areas of the given 'Nutzungsart' will be considered

    Returns
    -------
    XY : np.array of float
        X and Y Coordinates of the weighted mean
    """
    Data = Data.astype(np.float)
    if Nutzungsart is not None:
        Data = Data[Data[:, 0] == Nutzungsart]
    # multiply X- and Y-column with the relative area sizes
    weighted_XY = np.einsum('ij,i->ij', Data[:, 2:4], Data[:, 1] /
                                 np.sum(Data[:, 1]))

    XY = np.array([np.sum(weighted_XY[:, 0]), np.sum(weighted_XY[:, 1])])

    return XY

###Beispiel
##database = r'c:\projektcheck\3 Benutzerdefinierte Projekte\test_mean2' + \
##    '\FGDB_Definition_Projekt.gdb'
##table = 'Teilflaechen_Plangebiet'
##columns = np.array(['Nutzungsart', 'Flaeche_ha', 'INSIDE_X', 'INSIDE_Y'])
##Results = Read_FGDB(database, table, columns)
##Results.get_result_block()
##print(calc_weighted_mean(Results.result_block, Nutzungsart=0))
