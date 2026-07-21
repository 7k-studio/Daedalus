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

import src.opengl.tools_opengl as tools

import math

#from .test_cube import draw_object_from_file  # Import the new function
logger = logging.getLogger(__name__)

def draw_grid(linewidth=1, size=100, step=1, zoom=-10):
    glLineWidth(linewidth)
    glColor3f(0.8, 0.8, 0.8)  # Grey color
    glBegin(GL_LINES)

    if -zoom < 3:
        scale = 10  # Adjust scale based on zoom level
    else:
        scale = 1

    for i in range(-size, size + 1, step):
        # Vertical lines [ X | Y | Z ]
        glVertex3f(i/scale, -size, 0)
        glVertex3f(i/scale, size, 0)
        # Horizontal lines [ X | Y | Z ]
        glVertex3f(-size, i/scale, 0)
        glVertex3f(size, i/scale, 0)      
    glEnd()

def _draw_grid(half_size=10, step=1.0):
    glDisable(GL_LIGHTING)
    glColor3f(0.85, 0.85, 0.85)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for i in range(-half_size, half_size + 1):
        glVertex3f(i * step, 0.0, -half_size * step)
        glVertex3f(i * step, 0.0, half_size * step)
        glVertex3f(-half_size * step, 0.0, i * step)
        glVertex3f(half_size * step, 0.0, i * step)
    glEnd()
    # Highlight origin axes on grid
    glColor3f(0.55, 0.58, 0.62)
    glBegin(GL_LINES)
    glVertex3f(-half_size * step, 0.0, 0.0)
    glVertex3f(half_size * step, 0.0, 0.0)
    glVertex3f(0.0, 0.0, -half_size * step)
    glVertex3f(0.0, 0.0, half_size * step)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_grid_2(self, camera):
    left, right, bottom, top = camera.world_bounds(self.width(),self.height())
    # Determine tick spacing and minor spacing
    world_span_x = right - left
    world_span_y = top - bottom
    tick_spacing = tools.nice_tick_spacing(world_span_x, target_ticks=10)
    minor_spacing = tick_spacing / 5.0

    # Colors: major and minor (minor is subtler)
    major_col = [c / 255 for c in self.grid_color]
    minor_col = [c / 255 for c in self.minor_grid_color]

    # Draw minor vertical grid lines (world X = const)
    glLineWidth(0.8)
    x = math.floor(left / minor_spacing) * minor_spacing
    while x <= right:
        glColor3f(*minor_col)
        glBegin(GL_LINES)
        glVertex2f(x, bottom)
        glVertex2f(x, top)
        glEnd()
        x += minor_spacing

    # Draw minor horizontal grid lines (world Y = const)
    y = math.floor(bottom / minor_spacing) * minor_spacing
    while y <= top:
        glColor3f(*minor_col)
        glBegin(GL_LINES)
        glVertex2f(left, y)
        glVertex2f(right, y)
        glEnd()
        y += minor_spacing

    # Draw major vertical grid lines
    glLineWidth(2.0)
    x = math.floor(left / tick_spacing) * tick_spacing
    while x <= right:
        glColor3f(*major_col)
        glBegin(GL_LINES)
        glVertex2f(x, bottom)
        glVertex2f(x, top)
        glEnd()
        x += tick_spacing

    # Draw major horizontal grid lines
    y = math.floor(bottom / tick_spacing) * tick_spacing
    while y <= top:
        glColor3f(*major_col)
        glBegin(GL_LINES)
        glVertex2f(left, y)
        glVertex2f(right, y)
        glEnd()
        y += tick_spacing