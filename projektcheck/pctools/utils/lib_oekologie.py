import arcpy
import math
import pctools.utils.config as config
import os

def create_bodenbedeckung(projekt):

    folders = config.Folders()
    workspace_projekt_oekologie = folders.get_db('FGDB_Flaeche_und_Oekologie.gdb', projekt)
    path_bodenbedeckung = folders.get_table('Bodenbedeckung_Anteile', "FGDB_Flaeche_und_Oekologie.gdb", projekt)
    path_bodenbedeckung_tool = folders.get_base_table("FGDB_Flaeche_und_Oekologie_Tool.gdb", 'Bodenbedeckung_Anteile',  projekt)

    anteile_alt = create_bodenanteile(0, projekt)
    anteile_neu = create_bodenanteile(1, projekt)


    fields = ["IDBodenbedeckung", "Planfall", "Bodenbedeckung_Anteil"]
    cursor = arcpy.da.UpdateCursor(path_bodenbedeckung, fields)
    for row in cursor:
        if row[1] == 0 and row[0] == 1:
             row[2] = anteile_alt[0]
        elif row[1] == 0 and row[0] == 2:
             row[2] = anteile_alt[1]
        elif row[1] == 0 and row[0] == 3:
             row[2] = anteile_alt[2]
        elif row[1] == 0 and row[0] == 4:
             row[2] = anteile_alt[3]
        elif row[1] == 0 and row[0] == 5:
             row[2] = anteile_alt[4]
        elif row[1] == 0 and row[0] == 6:
             row[2] = anteile_alt[5]
        elif row[1] == 0 and row[0] == 7:
             row[2] = anteile_alt[6]
        elif row[1] == 0 and row[0] == 8:
             row[2] = anteile_alt[7]
        elif row[1] == 0 and row[0] == 9:
             row[2] = anteile_alt[8]
        elif row[1] == 0 and row[0] == 10:
             row[2] = anteile_alt[9]
        elif row[1] == 0 and row[0] == 11:
             row[2] = anteile_alt[10]
        elif row[1] == 1 and row[0] == 1:
             row[2] = anteile_neu[0]
        elif row[1] == 1 and row[0] == 2:
             row[2] = anteile_neu[1]
        elif row[1] == 1 and row[0] == 3:
             row[2] = anteile_neu[2]
        elif row[1] == 1 and row[0] == 4:
             row[2] = anteile_neu[3]
        elif row[1] == 1 and row[0] == 5:
             row[2] = anteile_neu[4]
        elif row[1] == 1 and row[0] == 6:
             row[2] = anteile_neu[5]
        elif row[1] == 1 and row[0] == 7:
             row[2] = anteile_neu[6]
        elif row[1] == 1 and row[0] == 8:
             row[2] = anteile_neu[7]
        elif row[1] == 1 and row[0] == 9:
             row[2] = anteile_neu[8]
        elif row[1] == 1 and row[0] == 10:
             row[2] = anteile_neu[9]
        elif row[1] == 1 and row[0] == 11:
             row[2] = anteile_neu[10]
        cursor.updateRow(row)

def import_zeichenanteile(projekt):

    folders = config.Folders()
    workspace_projekt_definition = folders.get_db('FGDB_Definition_Projekt.gdb', projekt)
    path_teilflaechen = folders.get_table('Teilflaechen_Plangebiet', "FGDB_Definition_Projekt.gdb", projekt)
    workspace_projekt_oekologie = folders.get_db('FGDB_Flaeche_und_Oekologie.gdb', projekt)
    path_nullfall = folders.get_table('Bodenbedeckung_Nullfall', "FGDB_Flaeche_und_Oekologie.gdb", projekt)
    path_planfall = folders.get_table('Bodenbedeckung_Planfall', "FGDB_Flaeche_und_Oekologie.gdb", projekt)
    temp = folders.get_table('bodentemp', "FGDB_Flaeche_und_Oekologie.gdb", projekt)

    gesamtflaeche = 0.0
    fields = ["SHAPE_Area"]
    cursor_teilflaechen = arcpy.da.SearchCursor(path_teilflaechen, fields)
    for row in cursor_teilflaechen:
        gesamtflaeche += row[0]

    #Nullfall
    boden_absolut = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0]
    boden_anteil = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0]
    pointer = 0
    skizze_exists = True

    fields = ["SHAPE_Area", "IDBodenbedeckung"]
    cursor = arcpy.da.SearchCursor(path_nullfall, fields)
    for row in cursor:
        pointer = row[1] - 1
        boden_absolut[pointer] += row[0]

    if skizze_exists:
        for x in xrange(11):
            boden_anteil[x] = (boden_absolut[x] / gesamtflaeche) * 100.0
            boden_anteil[x] = math.floor(boden_anteil[x])
        #fields = [ "alt"]
        #cursor = arcpy.da.InsertCursor(temp, fields)
        #for anteil in boden_anteil:
        #    cursor.insertRow([anteil])

        summe = sum(boden_anteil)
        differenz = 100 - summe
        if differenz > 0:
            boden_anteil[11] += differenz
        elif differenz < 0:
            neue_differenz = abs(differenz)
            pointer = 0
            for anteil in bodenanteil:
                if anteil > 0 and neue_differenz > 0:
                    if anteil > neue_differenz:
                        bodenanteil[pointer] = anteil - neue_differenz
                        neue_differenz = 0
                    else:
                        bodenanteil[pointer] = 0
                        neue_differenz = neue_differenz - anteil
                pointer += 1
        anteile_nullfall = boden_anteil

    #Planfall
    boden_absolut = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0]
    boden_anteil = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0]
    pointer = 0

    fields = ["SHAPE_Area", "IDBodenbedeckung"]
    cursor = arcpy.da.SearchCursor(path_planfall, fields)
    for row in cursor:
        pointer = row[1] - 1
        boden_absolut[pointer] += row[0]

    for x in xrange(11):
        boden_anteil[x] = (boden_absolut[x] / gesamtflaeche) * 100.0
        boden_anteil[x] = math.floor(boden_anteil[x])

    summe = sum(boden_anteil)
    differenz = 100 - summe
    if differenz > 0:
        boden_anteil[11] += differenz
    elif differenz < 0:
        neue_differenz = abs(differenz)
        pointer = 0
        for anteil in bodenanteil:
            if anteil > 0 and neue_differenz > 0:
                if anteil > neue_differenz:
                    bodenanteil[pointer] = anteil - neue_differenz
                    neue_differenz = 0
                else:
                    bodenanteil[pointer] = 0
                    neue_differenz = neue_differenz - anteil
            pointer += 1
    anteile_planfall = boden_anteil

    return anteile_nullfall, anteile_planfall
