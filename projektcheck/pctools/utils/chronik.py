import datetime
import arcpy

def set_chronicle(step, table):

    now = datetime.datetime.today()

    where = '"Arbeitsschritt"'+" ='"+ step + "'"
    cursor = arcpy.da.UpdateCursor(table, ["Arbeitsschritt", "Letzte_Nutzung"], where)
    for schritt in cursor:
        schritt[1] = now
        cursor.updateRow(schritt)

def compare_chronicle(step1, step2, table):

    where = '"Arbeitsschritt"'+" ='"+ step1 + "'"
    cursor = arcpy.da.SearchCursor(table, ["Arbeitsschritt", "Letzte_Nutzung"], where)
    for schritt in cursor:
        date1 = schritt[1]

    if date1 is None:
        date1 = datetime.datetime(1, 1, 1)

    where = '"Arbeitsschritt"'+" ='"+ step2 + "'"
    cursor = arcpy.da.SearchCursor(table, ["Arbeitsschritt", "Letzte_Nutzung"], where)
    for schritt in cursor:
        date2 = schritt[1]

    if date2 is None:
        date2 = datetime.datetime(1, 1, 1)

    return date1 > date2


