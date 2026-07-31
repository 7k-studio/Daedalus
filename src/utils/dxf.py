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
import ezdxf
import ezdxf.layouts
from ezdxf.math import ConstructionArc, Vec3, BSpline
import numpy as np
import math

logger = logging.getLogger(__name__)

def calculate_length(points):
    length = 0
    for i in range(1, len(points)):
        length += Vec3(points[i]).distance(Vec3(points[i-1]))
    return length

def find_point_at_length(points, target_length):
    length = 0
    for i in range(1, len(points)):
        segment_length = Vec3(points[i]).distance(Vec3(points[i-1]))
        if length + segment_length >= target_length:
            ratio = (target_length - length) / segment_length
            return Vec3(points[i-1]) + (Vec3(points[i]) - Vec3(points[i-1])) * ratio
        length += segment_length
    return Vec3(points[-1])

def export_airfoil_to_dxf(airfoil, file_name=None):

    Z = 0
    
    doc = ezdxf.new()
    msp = doc.modelspace()

    #for idx, airfoil in enumerate(export_airfoil):

    if not airfoil:
        logger.error("Airfoil incorrect or not selected")
        return

    spline_keys = ['LE','TE','PS','SS']
    for key in spline_keys:
        if not hasattr(airfoil, key):
            logger.error(f"Airfoil is missing {key} attribute, cannot proceed")
            return
        
        airfoil_segment = getattr(airfoil, key)

        if not hasattr(airfoil_segment, 'spline') and len(airfoil_segment.spline.control_points) == 0:
            logger.error(f"Airfoil {airfoil.name} and segment {key} has an empty or insufficient control points array.")
            return

        logger.info(f"Exporting airfoil {airfoil.name} to DXF...")
        # is not None and hasattr(airfoil, 'constr') and airfoil.constr['le'] is not None and len(airfoil.constr['le']) > 0:
        
        # Sprawdzenie, czy wszystkie tablice mają wystarczającą ilość danych
        # if len(airfoil.constr['le'][0]) > 0 and len(airfoil.constr['le'][1]) > 0:
        exp_array = airfoil_segment.spline.control_points

        Z_row = np.full((1, exp_array.shape[1]), Z)
        _array = np.vstack((exp_array, Z_row)).T
        #ps_spline = msp.add_spline(ps)
        dxf_spline = msp.add_open_spline(_array)

    doc.saveas("{}".format(file_name))
