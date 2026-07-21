'''

Copyright (C) 2025 Jakub Kamyk

This file is part of DAEDALUS.

DAEDALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DAEDALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DAEDALUS.  If not, see <http://www.gnu.org/licenses/>.

'''
import logging
from src.obj.surfaces import Patch

class Skin:
    def __init__(self, program, parent):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.parent = parent
        self.name = 'Skin'
        self.infos = {'creation_date': '',
                      'modification_date': ''}

        self.LE = Patch(self.DAEDALUS, self)
        self.PS = Patch(self.DAEDALUS, self)
        self.SS = Patch(self.DAEDALUS, self)
        self.TE = Patch(self.DAEDALUS, self)
    
    def build(self):
        """
        Generuje pojedynczą, ciągłą i gładką powierzchnię dla całego skrzydła.
        """
        self.logger.info("Building wing skin...")
        wing = self.parent
        if not wing or not wing.segments:
            self.logger.warning("Brak segmentów do zbudowania poszycia skrzydła")
            return

        for key in ['le', 'ps', 'ss', 'te']:
            spline_attr = f"{key.lower()}_spline"
            
            # Zbiór krzywych z segmentów
            curves = [
                getattr(seg, spline_attr).geom 
                for seg in wing.segments 
                if hasattr(getattr(seg, spline_attr, None), 'geom')
            ]

            # Każdy patch w Skin po prostu buduje się swoją metodą loft!
            patch_obj = getattr(self, key.upper())
            patch_obj.build_loft(curves)