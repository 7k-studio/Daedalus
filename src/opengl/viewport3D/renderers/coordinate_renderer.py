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

# PyQt6 imports

from OpenGL.GL import *
from OpenGL.GLUT import *

import math

#from .test_cube import draw_object_from_file  # Import the new function
logger = logging.getLogger(__name__)

def draw_origin_arrows(self, zoom, origin_x, origin_y, origin_z, quality=32):
    """Draw a tube from given origin."""
    diameter = 0.008 * zoom
    length = 0.075
    arrow = length + 0.02

    glLineWidth(2)
    
    # X Axis
    glColor3f(1, 0, 0) # Set tube color to dark grey
    angle_step = 2 * math.pi / quality

    glBegin(GL_QUAD_STRIP)
    for i in range(quality + 1):
        angle = i * angle_step
        y = origin_y + (diameter / 3) * math.cos(angle)
        z = origin_z + (diameter / 3) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(origin_x, y, z)
        glVertex3f(origin_x+(length * zoom), y, z)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x+(arrow*zoom), origin_y, origin_z)
    for i in range(quality + 1):
        angle = i * angle_step
        y = origin_y + (diameter) * math.cos(angle)
        z = origin_z + (diameter) * math.sin(angle)
        glVertex3f(origin_x+(length*zoom), y, z)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x+(length*zoom), origin_y, origin_z) 
    for i in range(quality + 1):
        angle = i * angle_step
        y = origin_y + (diameter) * math.cos(angle)
        z = origin_z + (diameter) * math.sin(angle)
        glVertex3f(origin_x+(length*zoom), y, z)
    glEnd()


    # Y Axis
    glColor3f(0, 1, 0) # Set tube color to dark grey
    angle_step = 2 * math.pi / quality

    glBegin(GL_QUAD_STRIP)
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 3) * math.cos(angle)
        z = origin_z + (diameter / 3) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(x, origin_y, z)
        glVertex3f(x, origin_y+(length * zoom), z)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y+(arrow*zoom), origin_z)  # Center of the base circle
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter) * math.cos(angle)
        z = origin_z + (diameter) * math.sin(angle)
        glVertex3f(x, origin_y+(length*zoom), z)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y+(length*zoom), origin_z) 
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter) * math.cos(angle)
        z = origin_z + (diameter) * math.sin(angle)
        glVertex3f(x, origin_y+(length*zoom), z)
    glEnd()

    # Z Axis
    glColor3f(0, 0, 1) # Set tube color to dark grey
    angle_step = 2 * math.pi / quality

    glBegin(GL_QUAD_STRIP)
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 3) * math.cos(angle)
        y = origin_y + (diameter / 3) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(x, y, origin_z)
        glVertex3f(x, y, origin_z + (length * zoom))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y, origin_z+(arrow*zoom))  # Center of the base circle
    for i in range(quality + 1):
        angle = i * angle_step
        y = origin_y + (diameter) * math.cos(angle)
        z = origin_z + (diameter) * math.sin(angle)
        glVertex3f(x, y, origin_z+(length*zoom))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y, origin_z+(length*zoom)) 
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter) * math.cos(angle)
        y = origin_y + (diameter) * math.sin(angle)
        glVertex3f(x, y, origin_z+(length*zoom))
    glEnd()

def draw_axes(self, length=1.5, width=1.0):
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    # X - red
    glColor3f(1.0, 0.2, 0.2)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(length, 0.0, 0.0)
    # Y - green
    glColor3f(0.2, 1.0, 0.2)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, length, 0.0)
    # Z - blue
    glColor3f(0.2, 0.4, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, length)
    glEnd()
    glEnable(GL_LIGHTING)