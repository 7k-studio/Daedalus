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

logger = logging.getLogger(__name__)

def draw_tube(self, origin_x, origin_y, origin_z, diameter, width, quality=32):
    """Draw a tube from given origin."""
    glLineWidth(2)
    glColor3f(0.5, 0.5, 0.5) # Set tube color to dark grey
    angle_step = 2 * math.pi / quality

    glBegin(GL_QUAD_STRIP)
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 2) * math.cos(angle)
        y = origin_y + (diameter / 2) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(x, y, origin_z)
        glVertex3f(x, y, origin_z + width)
    glEnd()

    # Draw the end caps
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y, origin_z)  # Center of the base circle
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 2) * math.cos(angle)
        y = origin_y + (diameter / 2) * math.sin(angle)
        glVertex3f(x, y, origin_z + width)
    glEnd()

    glColor3f(0.0, 0.0, 0.0)  # Black color for edges
    glBegin(GL_LINES)

    x_old = origin_x + (diameter / 2) * math.cos(0)
    y_old = origin_y + (diameter / 2) * math.sin(0)

    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 2) * math.cos(angle)
        y = origin_y + (diameter / 2) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(x, y, origin_z)
        glVertex3f(x_old, y_old, origin_z)

        x_old = x
        y_old = y
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y, origin_z)  # Center of the base circle
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 2) * math.cos(angle)
        y = origin_y + (diameter / 2) * math.sin(angle)
        glVertex3f(x, y, origin_z + width)
    glEnd()

    glColor3f(0.0, 0.0, 0.0)  # Black color for edges
    glBegin(GL_LINES)
    x_old = origin_x + (diameter / 2) * math.cos(0)
    y_old = origin_y + (diameter / 2) * math.sin(0)

    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 2) * math.cos(angle)
        y = origin_y + (diameter / 2) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(x, y, origin_z + width)
        glVertex3f(x_old, y_old, origin_z + width)

        x_old = x
        y_old = y
    glEnd()
    
def draw_cube(origin_x, origin_y, origin_z, width):
    """Draw a simple cube."""
    glBegin(GL_LINES)
    # Define vertices for a cube
    glColor3f(0, 1, 0)  # Green
    glVertex3f(origin_x, origin_y-width/2, origin_z)
    glVertex3f(origin_x, origin_y+width/2, origin_z)
    glVertex3f(origin_x-width, origin_y+width/2, origin_z)
    glVertex3f(origin_x-width, origin_y-width/2, origin_z)
    # Add other faces...
    glEnd()
    
def draw_object_from_file(filepath, extrusion=1.0):
    """Draw an object using coordinates from a file, extruded along the z-axis."""
    vertices = []
    with open(filepath, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith("Name:"):
                x, y = map(float, line.split())
                vertices.append((x, y))

    #print(vertices)
    # Create front and back faces
    front_face = [(x, y, 0) for x, y in vertices]
    back_face = [(x, y, extrusion) for x, y in vertices]

    # Draw the front and back faces
    glColor3f(0.5, 0.5, 0.5)  # Grey color
    glBegin(GL_QUADS)
    for i in range(len(vertices) - 1):
        # Front face
        glVertex3f(*front_face[i])
        glVertex3f(*front_face[i + 1])
        glVertex3f(*back_face[i + 1])
        glVertex3f(*back_face[i])
    glEnd()

    # Draw edges connecting front and back faces
    glColor3f(0.0, 0.0, 0.0)  # Black color for edges
    glBegin(GL_LINES)
    for i in range(len(vertices)):
        glVertex3f(*front_face[i])
    for i in range(len(vertices)):
        glVertex3f(*back_face[i])
    glEnd()

def draw_patch_fill(patch, color=(0.8, 0.8, 0.9)):
    """Draw from Patch based on geometry mesh"""
    if not patch or not hasattr(patch, 'vertices_flat') or patch.vertices_flat is None:
        logger.error("Drawing patch aborted!")
        return

    glEnableClientState(GL_VERTEX_ARRAY)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(1.0, 1.0)
    glColor3f(*color)

    # Używamy wstępnie przetworzonej tablicy (0 alokacji pamięci w tej klatce!)
    glVertexPointer(3, GL_FLOAT, 0, patch.vertices_flat)
    glDrawArrays(GL_QUADS, 0, len(patch.vertices_flat))

    glDisable(GL_POLYGON_OFFSET_FILL)
    glDisableClientState(GL_VERTEX_ARRAY)