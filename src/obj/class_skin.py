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
        Generates a continuous skin surface for the wing while preserving 
        boundary BSpline references on each Patch.
        """
        self.logger.info("Building wing skin...")
        wing = self.parent
        if not wing or not wing.segments:
            self.logger.error("No segments available to build wing skin.")
            return

        # Determine mode ('approximated' or 'interpolated') from wing attributes
        connection_mode = 'approximated'
        if hasattr(wing, 'attrs') and 'connection' in wing.attrs:
            attr_val = wing.attrs['connection'].value.lower()
            if 'interpolated' in attr_val:
                connection_mode = 'interpolated'
            elif 'approximated' in attr_val:
                connection_mode = 'approximated'

        # Mapping: patch_key -> (profile_attr, u_fwd_spline, u_rwd_spline)
        patch_mapping = {
            'PS': ('ps_spline', wing.LE_PS, wing.TE_PS),
            'SS': ('ss_spline', wing.LE_SS, wing.TE_SS),
            'LE': ('le_spline', wing.LE_SS, wing.LE_PS),
            'TE': ('te_spline', wing.TE_PS, wing.TE_SS),
        }

        for patch_key, (spline_attr, u_fwd_spline, u_rwd_spline) in patch_mapping.items():
            # Collect profile BSpline objects along span
            profile_splines = [
                getattr(seg, spline_attr)
                for seg in wing.segments 
                if hasattr(seg, spline_attr) and getattr(seg, spline_attr) is not None
            ]

            patch_obj = getattr(self, patch_key)
            patch_obj.build_loft(
                spline_objects=profile_splines,
                u_fwd=u_fwd_spline,
                u_rwd=u_rwd_spline,
                mode_v=connection_mode
            )