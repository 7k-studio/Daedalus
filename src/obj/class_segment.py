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
import numpy as np

from src.obj.class_skin import Skin
from src.obj.class_param import Param, Attr, M, DEG
from src.obj.curves import BSpline

class Segment:
    def __init__(self, program=None, project=None, parent=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.PROJECT = project
        self.parent = parent

        self.name = 'Segment'
        self.info = {'creation_date': '',
                      'modification_date': ''}
        
        self.le_spline = BSpline(self.DAEDALUS, self)
        self.te_spline = BSpline(self.DAEDALUS, self)
        self.ps_spline = BSpline(self.DAEDALUS, self)
        self.ss_spline = BSpline(self.DAEDALUS, self)

        self.ps_le_spline = None
        self.ps_te_spline = None
        self.ss_le_spline = None
        self.ss_te_spline = None

        self.skin = Skin(self.DAEDALUS, self)
        
        self.attrs = {
            'airfoil': Attr('airfoil', self.PROJECT.airfoils[-1], [arf.name for arf in self.PROJECT.airfoils]) # G2 later add 'segment'
        }
        
        # Segment positioning parameters
        self.params = {
            "position_X":  Param("position_X",0,M),
            "position_Y":  Param("position_Y",0,M),
            'span': Param("span",0,M),
            # 'tan_accel': Param('tan_accel', 0.1, M)
        }

        self.stats = {
            'Test': Param('test', 0, M)
            }
    
    def update(self):
        """
        Copy 2D control points from the linked master Airfoil, 
        transform them into 3D space, and generate the segment's splines.
        """
        self.logger.info("Updating SEGMENT geometry...")

        # Get the referenced master airfoil
        linked_airfoil = self.attrs['airfoil'].value
        if not linked_airfoil:
            self.logger.warning("No airfoil linked to this segment.")
            return
        
        # Calculate absolute 3D positioning
        component = self.parent.parent
        total_X = component.params['origin_X'].get() + self.params['position_X'].value
        total_Y = component.params['origin_Y'].get() + self.params['position_Y'].value
        total_Z = component.params['origin_Z'].get() + self.params['span'].value
        
        # Helper function to transform 2D control points into 3D space
        def transform_cps(source_spline):
            if len(source_spline.control_points) == 0:
                return []
                
            # Copy the master 2D control points
            cp = np.array(source_spline.control_points, copy=True)
            
            # Apply X and Y translations
            cp[0, :] += total_X
            cp[1, :] += total_Y
            
            # Add or replace the Z coordinate for span
            if cp.shape[0] == 2:
                cp_z_coords = np.full(cp.shape[1], total_Z)
                cp = np.vstack([cp, cp_z_coords])
            elif cp.shape[0] >= 3:
                cp[2, :] = np.full(cp.shape[1], total_Z)
                
            return cp
        
        # Copy, translate, and assign control points to the Segment's splines
        self.le_spline.control_points = transform_cps(linked_airfoil.LE.spline)
        self.te_spline.control_points = transform_cps(linked_airfoil.TE.spline)
        self.ps_spline.control_points = transform_cps(linked_airfoil.PS.spline)
        self.ss_spline.control_points = transform_cps(linked_airfoil.SS.spline)

        # Generate the final 3D geometry from the new control points
        self.le_spline.create()
        self.te_spline.create()
        self.ps_spline.create()
        self.ss_spline.create()
        
        self.logger.info("SEGMENT 3D splines successfully generated from shared airfoil.")
    