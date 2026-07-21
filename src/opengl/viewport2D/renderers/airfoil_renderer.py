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

        vec_length = len(segment.spline.geom[0])
        if vec_length > 0:
            points = [(segment.spline.geom[0][i], segment.spline.geom[1][i]) for i in range(vec_length)]
            if line_style == "solid":
                lines._draw_solid_line(points, color[key])
            if line_style == "dashed":
                _draw_dashed_line(points, color[key])
            if line_style == "dot-dash":
                _draw_dot_dash_line(points, color[key])

def _draw_dashed_line(points, color, dash_length=0.001):
    """Draws a dashed line connecting the given points."""

    glColor3f(*color)
    # total_len = sum(
    # linalg.norm(array(points[i+1]) - array(points[i]))
    # for i in range(len(points)-1)
    # )
    # dash_length = total_len * dash_length_scale

    for i in range(len(points) - 1):
        p1 = np.array([points[i][0], points[i][1], 0.0])
        p2 = np.array([points[i + 1][0], points[i + 1][1], 0.0])
        vec = p2 - p1
        length = np.linalg.norm(vec)
        if length == 0:
            continue
        dir_vec = vec / length

        num_dashes = max(1, int(length / (2 * dash_length)))
        for j in range(num_dashes):
            start = p1 + dir_vec * (2 * j) * dash_length
            end = p1 + dir_vec * (2 * j + 1) * dash_length
            glBegin(GL_LINES)
            glVertex3fv(start)
            glVertex3fv(end)
            glEnd()

def _draw_dot_dash_line(points, color, dash_length=0.01, dot_size=3.0):
    """Draws a dot-dash line connecting the given points."""

    glColor3f(*color)
    for i in range(len(points) - 1):
        p1 = np.array([points[i][0], points[i][1], 0.0])
        p2 = np.array([points[i + 1][0], points[i + 1][1], 0.0])
        vec = p2 - p1
        length = np.linalg.norm(vec)
        dir_vec = vec / length

        num_dashes = int(length / (3 * dash_length))
        for j in range(num_dashes):
            # Draw dash
            start = p1 + dir_vec * (3 * j) * dash_length
            end = p1 + dir_vec * (3 * j + 1) * dash_length
            glBegin(GL_LINES)
            glVertex3fv(start)
            glVertex3fv(end)
            glEnd()

            # Draw dot
            dot = p1 + dir_vec * (3 * j + 2) * dash_length
            glPointSize(dot_size)
            glBegin(GL_POINTS)
            glVertex3fv(dot)
            glEnd()

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

def draw_dashed_line(airfoil, base_dash_length=0.01, zoom=1):
    """Draw dashed line between points p1 and p2."""

    for key in airfoil.constr:
        points = np.array(airfoil.constr[key]).T
        z = 0 if key in ['le', 'ps', 'ss', 'te'] else None
        for j in range(len(points) - 1):
            p1 = points[j]
            #print(p1)
            p2 = points[j + 1]
            if z is not None:
                p1 = [p1[0], p1[1], z]
                p2 = [p2[0], p2[1], z]
            #print(f"{key}: ", points)

            zoom = abs(zoom) if zoom != 0 else 0.001  # avoid divide-by-zero
            dash_length = base_dash_length * zoom

            p1 = np.array(p1)
            p2 = np.array(p2)
            vec = p2 - p1
            length = np.linalg.norm(vec)
            dir_vec = vec / length 

            num_dashes = int(length / (2 * dash_length))
            for i in range(num_dashes):
                start = p1 + dir_vec * (2 * i) * dash_length
                end = p1 + dir_vec * (2 * i + 1) * dash_length
                glColor3f(0.3, 0.3, 0.3)
                glBegin(GL_LINES)
                glVertex3fv(start)
                glVertex3fv(end)
                glEnd()

def draw_airfoil_selig_format(self, reference_airfoil):
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

    color = self.airfoil_settings['wireframe']['color']

    vec_length = len(reference_airfoil.top_curve[0])
    if vec_length > 0:
        # Draw edges connecting front and back faces
        glColor3f(0.5,0.5,0.5)
        glBegin(GL_LINE_STRIP)
        for i in range(vec_length):
            x = reference_airfoil.top_curve[0][i]
            y = reference_airfoil.top_curve[1][i]
            glVertex3f(x, y, 0.0)  # force z=0
        glEnd()
    
    vec_length = len(reference_airfoil.dwn_curve[0])
    if vec_length > 0:

        glColor3f(0.5,0.5,0.5)
        glBegin(GL_LINE_STRIP)
        for i in range(vec_length):
            x = reference_airfoil.dwn_curve[0][i]
            y = reference_airfoil.dwn_curve[1][i]
            glVertex3f(x, y, 0.0)  # force z=0
        glEnd()