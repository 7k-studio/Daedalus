'''

Copyright (C) 2025-2026 Jakub Kamyk

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

from OpenGL.GL import *
from OpenGL.GLUT import *

import numpy as np

#from .test_cube import draw_object_from_file  # Import the new function

import src.opengl.tools_opengl as tools
import src.opengl.tools_lines as lines

def draw_airfoil(self, Current_Airfoil, line_style="solid", color=None):
    '''
    Plots an airfoil based on objects Airfoil stored in obj.arf.py defined by folowing gorup of parameters:

    Base parameters:
        chord, origin_X, origin_Y
    Leading Edge parameters:
        le_thickness, le_depth, le_offset, le_angle
    Trailing Edge parameters:
        te_thickness, te_depth, te_offset, te_angle
    Pressure Side parameters:
        ps_fwd_angle, ps_rwd_angle, ps_fwd_accel, ps_rwd_accel
    Suction Side parameters:    
        ss_fwd_angle, ss_rwd_angle, ss_fwd_accel, ss_rwd_accel
    '''

    # Extract parameters
    glDisable(GL_DEPTH_TEST)

    if color == "grey":
        color ={'le': [0.5,0.5,0.5],
                'te': [0.5,0.5,0.5],
                'ps': [0.5,0.5,0.5],
                'ss': [0.5,0.5,0.5]
            }
    else:
        color = self.airfoil_settings['wireframe']['color']

    for key in ['le', 'te', 'ps', 'ss']:
        segment = getattr(Current_Airfoil, key.upper())

        lines.draw_styled_line(segment.spline.geom, style=line_style, color=color[key])


def draw_cp_net(self, Current_Airfoil, zoom):
    
    color = self.airfoil_settings['control_points']['color']
    glPointSize(6.0)

    for key in ['le', 'te', 'ps', 'ss']:
        segment = getattr(Current_Airfoil, key.upper())

        glColor3f(color[key][0], color[key][1], color[key][2])
        glBegin(GL_POINTS)
        points = np.array(segment.spline.control_points).T
        #print(f"{key}: ", points)
        for point in points:
            glVertex3f(point[0], point[1], 0.0)
        glEnd()

def draw_reference(self, reference_airfoil):
    '''
    Plots an airfoil based on objects Airfoil stored in obj.arf.py defined by folowing gorup of parameters:

    Base parameters:
        chord, origin_X, origin_Y
    Leading Edge parameters:
        le_thickness, le_depth, le_offset, le_angle
    Trailing Edge parameters:
        te_thickness, te_depth, te_offset, te_angle
    Pressure Side parameters:
        ps_fwd_angle, ps_rwd_angle, ps_fwd_accel, ps_rwd_accel
    Suction Side parameters:    
        ss_fwd_angle, ss_rwd_angle, ss_fwd_accel, ss_rwd_accel
    '''

    # Extract parameters
    glDisable(GL_DEPTH_TEST)

    color = [0.5,0.5,0.5] # self.airfoil_settings['wireframe']['color']

    if reference_airfoil.format in ["XY-points"]:

        lines.draw_styled_line(reference_airfoil.curve, color)

    if reference_airfoil.format in ["030-ddls-parametric"]:
        for key in ['le_spline', 'te_spline', 'ps_spline', 'ss_spline']:
            segment = getattr(reference_airfoil, key)
            color = self.airfoil_settings['wireframe']['color']
            lines.draw_styled_line(segment.geom, style="dashed", color=color.get(key.replace("_spline",""), [0.5,0.5,0.5]))

    if reference_airfoil.format in ["ddls-parametric"]:
        draw_airfoil(self, reference_airfoil, line_style="dashed", color=color)