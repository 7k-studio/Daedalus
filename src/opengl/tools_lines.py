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
from OpenGL.GL import *
from OpenGL.GLUT import *

import numpy as np


def _draw_solid_line(points, color=None):
    """Draw a solid line connecting the given points using a vertex array."""
    if color is not None:
        if len(color) >= 4:
            glColor4f(*color)
        else:
            glColor3f(*color)

    if points is None:
        return

    vertices = np.asarray(points, dtype=np.float32)
    if vertices.size == 0:
        return

    if vertices.ndim == 1:
        vertices = vertices.reshape(1, -1)
    elif vertices.ndim == 2 and vertices.shape[0] in (2, 3) and vertices.shape[1] not in (2, 3):
        vertices = vertices.T

    if vertices.ndim != 2 or vertices.shape[1] not in (2, 3):
        return

    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(vertices.shape[1], GL_FLOAT, 0, vertices)
    glDrawArrays(GL_LINE_STRIP, 0, len(vertices))
    glDisableClientState(GL_VERTEX_ARRAY)