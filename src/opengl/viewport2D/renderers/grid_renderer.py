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

from OpenGL.GL import *
from OpenGL.GLUT import *

import math

import src.opengl.tools_opengl as tools

def draw(context):
    left, right, bottom, top = context.camera.world_bounds(context.width, context.height)
    # Determine tick spacing and minor spacing
    world_span_x = right - left
    world_span_y = top - bottom
    tick_spacing = tools.nice_tick_spacing(world_span_x, target_ticks=10)
    minor_spacing = tick_spacing / 5.0

    # Colors: major and minor (minor is subtler)
    major_col = [c / 255 for c in context.grid_color]
    minor_col = [c / 255 for c in context.minor_grid_color]

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