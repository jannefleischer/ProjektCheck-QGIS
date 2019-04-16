# -*- coding: utf-8 -*-

import arcpy

from tools.utils.params import Tbx
from tools.utils.encoding import encode
from tools.analyst.einnahmen.script_Ergebnisinterpretation import Ergebnisinterpretation

class TbxErgebnisinterpretation(Tbx):
    """Ergebnisinterpretation"""

    @property
    def label(self):
        return u'Ergebnisinterpretation'

    @property
    def Tool(self):
        return Ergebnisinterpretation

    def _getParameterInfo(self):

        par = self.par

        par.zeitpunkt = arcpy.Parameter()
        par.zeitpunkt.name = u'Zeitpunkt'
        par.zeitpunkt.displayName = u'Zeitpunkt'
        par.zeitpunkt.parameterType = 'Required'
        par.zeitpunkt.datatype = u'GPString'
        par.zeitpunkt.value = "Alle Werte der fiskalischen Bilanz verstehen sich als 'pro Jahr'-Angaben. " + "Diese beziehen sich auf einen Zeitpunkt deutlich nach dem Bezugsbeginn des Planungsprojekts. Zu diesem Zeitpunkt ist der Bezug vollständig abgeschlossen. Zudem sind für Wohngebietsflächen mindestens sieben Jahre vergangen, denn in den ersten sieben Jahren hat die Zuweisung der Einkommensteuer i.d.R. noch nicht auf die Neubau-bedingten Einwohnerwanderungen reagiert."
        par.zeitpunkt.category = "1. Hinweis zum Zeitpunkt"

        par.kfa = arcpy.Parameter()
        par.kfa.name = u'Kommunaler Finanzausgleich'
        par.kfa.displayName = u'Kommunaler Finanzausgleich'
        par.kfa.parameterType = 'Required'
        par.kfa.datatype = u'GPString'
        par.kfa.value = "Den ermittelten Einnahmeverschiebungen bei der Grund-, Einkommen-, Gewerbe- und Umsatzsteuer sowie beim Familienleistungsausgleich stehen in allen Flächenländern Wirkungen des kommunalen Finanzausgleichs gegenüber. Bei den Stadtstaaten gibt es Rückwirkungen auf den Länderfinanzausgleich. Insbesondere bei Gewerbeflächen gleichen die Zuweisungen an die einzelnen Gemeinden einen großen Teil der mit ProjektCheck ermittelten Einnahmengewinne und -verluste wieder aus. Bei Wohnnutzungen fallen die Wirkungen im kommunalen Finanzausgleich i.d.R. deutlich geringer aus. Zudem führen Wanderungsgewinne (trotz der Steuermehreinnahmen) in den meisten Bundesländern eher zu Mehreinnahmen aus dem Kommunalen Finanzausgleich. Da die Regelungen des kommunalen Finanzausgleichs von Bundesland zu Bundesland unterschiedlich sind, regelmäßig verändert werden und in keiner amtlichen Statistik zentral erfasst werden wird in ProjektCheck keine Abschätzung der Veränderung der Zuweisungen aus dem Kommunalen Finanzausgleich angeboten."
        par.kfa.category = "2. Hinweis zum Kommunalen Finanzausgleich"

        par.kreisumlage = arcpy.Parameter()
        par.kreisumlage.name = u'Kreisumlage'
        par.kreisumlage.displayName = u'Kreisumlage'
        par.kreisumlage.parameterType = 'Required'
        par.kreisumlage.datatype = u'GPString'
        par.kreisumlage.value = "Auf Steuermehreinnahmen zahlen kreisangehörige Gemeinden eine – z.T. hebesatzbereinigte – Kreisumlage. Sinkende Steuereinnahmen führen zu geringeren Umlagezahlungen. Da die Kreisumlagesätze nicht zentral erfasst werden und sich die Umlagegrundlagen von Bundesland zu Bundesland unterscheiden wird in ProjektCheck keine Abschätzung der Kreisumlagezahlungen der Gemeinden angeboten."
        par.kreisumlage.category = "3. Hinweis zur Kreisumlage"

        return par

    def _updateParameters(self, params):

        par = self.par
        par.zeitpunkt.enabled = False
        par.kreisumlage.enabled = False
        par.kfa.enabled = False
