# -*- coding: utf-8 -*-

import os
import sys
import arcpy
from pctools.utils.params import Tool

class Ergebnisinterpretation(Tool):
    """Ergebnisinterpretation-Tool"""

    _param_projectname = 'name'
    _workspace = 'FGDB_Einnahmen.gdb'

    def add_outputs(self):
        self.output.add_image("C:\\Temp\\hui.png",
                                "hui",
                                [10.0, 7.0],
                                "lanczos",
                                False,
                                False
                                )

    def run(self):
        """run Ergebnisinterpretation Tool"""
        text =  "Alle Werte der fiskalischen Bilanz verstehen sich als 'pro Jahr'-Angaben. " + "Diese beziehen sich auf einen Zeitpunkt deutlich nach dem Bezugsbeginn des Planungsprojekts. Zu diesem Zeitpunkt ist der Bezug vollständig abgeschlossen. Zudem sind für Wohngebietsflächen mindestens sieben Jahre vergangen, denn in den ersten sieben Jahren hat die Zuweisung der Einkommensteuer i.d.R. noch nicht auf die Neubau-bedingten Einwohnerwanderungen reagiert."



