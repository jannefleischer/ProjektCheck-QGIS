import arcpy
import pctools.utils.config

def Bewohner_referenz_plangebiet(self, projektname):

    we_tabelle = self.folders.get_table(tablename= "Wohnen_WE_in_Gebaeudetypen", workspace='FGDB_Definition_Projekt.gdb', project= projektname, check=True)
    fields = ["WE", "EW_je_WE"]
    einwohnerzahl = 0
    cursor = arcpy.da.SearchCursor(we_tabelle, fields)
    for flaeche in cursor:
        einwohnerzahl += flaeche[0] * flaeche[1]

    return einwohnerzahl


def Erwerbstaetige_referenz_plangebiet(self, projektname):

    erwerbstaetige = 0
    pfad_rahmendaten = self.folders.get_table(
        tablename='Projektrahmendaten',
        workspace="FGDB_Definition_Projekt.gdb",
        project=projektname)
    cursor = arcpy.da.SearchCursor(pfad_rahmendaten, ["AGS", "Gemeindetyp"])
    for projekt in cursor:
        ags_projekt = projekt[0]
        gemeindetyp = projekt[1]

    table_teilflaechen = self.folders.get_table(
        tablename='Teilflaechen_Plangebiet',
        workspace="FGDB_Definition_Projekt.gdb",
        project=projektname)
    pfad_flaechenanteile_branchen = self.folders.get_table(tablename='Gewerbe_Anteile', workspace="FGDB_Definition_Projekt.gdb", project=projektname)
    pfad_dichtekennwerte = self.folders.get_base_table(table = "Dichtekennwerte_Gewerbe", workspace="FGDB_Definition_Projekt_Tool.gdb")

    where_clause_teilflaechen = '"Nutzungsart" = 2'
    cursor_teilflaechen = arcpy.da.SearchCursor(table_teilflaechen, ["id_teilflaeche", "Nutzungsart", "Flaeche_ha"], where_clause_teilflaechen)
    for flaeche in cursor_teilflaechen:
        where_clause_anteile ='"IDTeilflaeche"' + "=" + str(flaeche[0])
        cursor_branchenanteile = arcpy.da.SearchCursor(pfad_flaechenanteile_branchen, ["IDTeilflaeche", "IDBranche", "anteil"], where_clause_anteile)
        for eintrag in cursor_branchenanteile:
            where_clause_dichtekennwerte = '"ID_Branche_ProjektCheck"' + "=" + str(eintrag[1]) + " AND " + '"Gemeindetyp_ProjektCheck"' + "=" + str(gemeindetyp)
            cursor_dichtekennwerte = arcpy.da.SearchCursor(pfad_dichtekennwerte, ["ID_Branche_ProjektCheck", "Gemeindetyp_ProjektCheck", "AP_pro_ha_brutto"], where_clause_dichtekennwerte)
            for dichtekennwert in cursor_dichtekennwerte:
                erwerbstaetige += dichtekennwert[2] * flaeche[2] * eintrag[2] / 100

    return erwerbstaetige







