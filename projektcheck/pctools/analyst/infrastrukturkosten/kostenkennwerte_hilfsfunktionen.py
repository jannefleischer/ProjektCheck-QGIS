from pctools.utils.params import DummyTbx
import time
import numpy as np
import pandas as pd

def kostenkennwerte(project):
    """
    Check if Kostenkennwerte_Linienelemente hat data.
    If not: Copy from Netze_und_Netzelemente (only if Shape == Line) and
    multiply by interest- and time-factor

    Parameters
    ----------
    project : String
        name of the active project

    """
    table = 'Kostenkennwerte_Linienelemente'
    workspace_tool = 'FGDB_Kosten_Tool.gdb'
    tbx = DummyTbx()
    tbx.set_active_project(project)
    # check if table Kostenkennwerte_Linienelemente contains content
    df_costs_line_elements = tbx.table_to_dataframe(
        table, workspace='FGDB_Kosten.gdb')
    if len(df_costs_line_elements) != 0:
        return
    # calculate time factor
    current_year = int(time.strftime("%Y"))
    df_frame_data = tbx.table_to_dataframe('Rahmendaten',
                                        workspace=workspace_tool,
                                        is_base_table=True)
    interest = df_frame_data['Zins']
    reference_year = df_frame_data['Stand_Kostenkennwerte']
    time_factor = (1 + interest) ** (current_year - reference_year)
    # get regional factor
    ags = tbx.query_table('Projektrahmendaten',
                          workspace='FGDB_Definition_Projekt.gdb',
                          columns=['AGS'])[0][0]
    regional_factor = tbx.table_to_dataframe(
        'bkg_gemeinden', workspace='FGDB_Basisdaten_deutschland.gdb',
        columns=['BKI_Regionalfaktor'], where="AGS='{}'".format(str(ags)),
        is_base_table=True)
    # fill table Kostenkennwerte_Linienelemente
    regional_time_factor = time_factor * \
        regional_factor.loc[:, 'BKI_Regionalfaktor']
    rounding_factor = 5
    df_networks = tbx.table_to_dataframe('Netze_und_Netzelemente',
                                         workspace='FGDB_Kosten_Tool.gdb',
                                         where="Typ='{}'".format('Linie'),
                                         is_base_table=True)
    # multiply with factors
    df_networks.loc[:, ['Euro_EH', 'Cent_BU', 'Euro_EN']] *= \
        regional_time_factor[0]
    # round to 5
    df_networks.loc[:, ['Euro_EH', 'Cent_BU', 'Euro_EN']] = \
        round_df_to(df_networks.loc[:, ['Euro_EH', 'Cent_BU', 'Euro_EN']],
                    rounding_factor)

    tbx.dataframe_to_table(table, df_networks,
                           pkeys=['ID'], workspace='FGDB_Kosten.gdb',
                           upsert=True)
    return

def round_df_to(df, rounding_factor):
    """
    Round all values of a Dataframe to some value.
    For example: round to 5 euro

    Parameters
    ----------
    df : pandas dataframe
        the input dataframe
    rounding_factor : int
        rounding value

    """
    df = df / rounding_factor
    df = df.apply(pd.Series.round)
    df *= rounding_factor
    df = df.astype('int')
    return df

def kostenaufteilung_startwerte(project):
    """
    Check if table Kostenaufteilung has data.
    If not: copy data from Kostenaufteilung_Startwerte

    Parameters
    ----------
    project : String
        name of the active project

    """
    table = 'Kostenaufteilung'
    tbx = DummyTbx()
    tbx.set_active_project(project)
    df_cost_allocation = tbx.table_to_dataframe(
        table, workspace='FGDB_Kosten.gdb')
    if len(df_cost_allocation) != 0:
        return
    df_cost_allocation_initial = tbx.table_to_dataframe(
        'Kostenaufteilung_Startwerte', columns=[],
        workspace='FGDB_Kosten_Tool.gdb', where=None, is_base_table=True)
    tbx.dataframe_to_table(table, df_cost_allocation_initial, pkeys=['OBJECTID'],
                           workspace='FGDB_Kosten.gdb', upsert=True)




