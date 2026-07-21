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

import src.opengl.tools_lines as lines

logger = logging.getLogger(__name__)

def draw_wireframe(PROJECT, component_idx, wing_idx, segment_idx):
    """Draw airfoil wireframe from segment.airfoil spline geometry."""
    
    glLineWidth(2)

    wing = PROJECT.components[component_idx].wings[wing_idx]
    segment = PROJECT.components[component_idx].wings[wing_idx].segments[segment_idx]
    
    # Access spline geometry from airfoil
    le = segment.le_spline.geom
    te = segment.te_spline.geom
    ps = segment.ps_spline.geom
    ss = segment.ss_spline.geom

    if not all(arr is not None and len(arr) > 0 for arr in [le, te, ps, ss]):
        logger.error("Invalid airfoil data")
        return
    
    # Define colors for each spline element
    color_map = {
        'le': [0.0, 0.0, 1.0],   # Blue
        'te': [1.0, 1.0, 0.0],   # Yellow
        'ps': [0.0, 1.0, 0.0],   # Green
        'ss': [1.0, 0.0, 0.0],   # Red
    }
    
    # Draw each spline curve
    spline_data = {
        'le': le,
        'te': te,
        'ps': ps,
        'ss': ss,
    }
    
    for key, geom in spline_data.items():
        if geom is not None and len(geom) > 0 and len(geom[0]) > 0:
            lines._draw_solid_line(geom, color_map[key])

    try:
        le_ps = wing.LE_PS.geom
        le_ss = wing.LE_SS.geom
        te_ps = wing.TE_PS.geom
        te_ss = wing.TE_SS.geom

        if not all(arr is not None and len(arr) > 0 for arr in [le_ps, le_ss, te_ps, te_ss]):
            logger.error("Invalid airfoil data")
            return
        
        # Define colors for each spline element
        color_map = {
            'le_ps': [0.5, 0.5, 0.5],
            'te_ps': [0.5, 0.5, 0.5],
            'le_ss': [0.5, 0.5, 0.5],
            'te_ss': [0.5, 0.5, 0.5],
        }
        
        # Draw each spline curve
        connection_data = {
            'le_ps': le_ps,
            'te_ps': te_ps,
            'le_ss': le_ss,
            'te_ss': te_ss
        }
        
        for key, geom in connection_data.items():
            if geom is not None and len(geom) > 0 and len(geom[0]) > 0:
                lines._draw_solid_line(geom, color_map[key])

    except AttributeError:
        logger.warning("No connection between segments")

def draw_airfoil_wireframe(self, component_idx, wing_idx, segment_idx):
    """Draw an airfoil using coordinates from a file, extruded along the z-axis."""
    from program.project import PROJECT
    glLineWidth(2)

    segment = PROJECT.project_components[component_idx].wings[wing_idx].segments[segment_idx]
    le = segment.geom['le']
    te = segment.geom['te']
    ps = segment.geom['ps']
    ss = segment.geom['ss']

    if not all(arr is not None and len(arr) > 0 for arr in [le, te, ps, ss]):
        logger.error("Invalid airfoil data")
        return
    
    color = {'le': [0.0, 0.0, 1.0], 
             'te': [1.0, 1.0, 0.0], 
             'ps': [0.0, 1.0, 0.0], 
             'ss': [1.0, 0.0, 0.0], 
             'le_ps': [0.0, 1.0, 0.0], 
             'le_ss': [1.0, 0.0, 0.0],
             'te_ps': [0.0, 1.0, 0.0],
             'te_ss': [1.0, 0.0, 0.0]}

    for key in ['le', 'te', 'ps', 'ss', 'le_ps', 'le_ss', 'te_ps', 'te_ss']:
        if len(segment.geom[key]) > 0:
            # Draw edges connecting front and back faces
            glColor3f(color[key][0], color[key][1], color[key][2])
            glBegin(GL_LINES)
            lines._draw_solid_line(segment.geom[key], color[key])
            # for i in range(len(le[0])-1):
            #     glVertex3f(segment.geom[key][0][i], segment.geom[key][1][i], segment.geom[key][2][i])
            #     glVertex3f(segment.geom[key][0][i+1], segment.geom[key][1][i+1], segment.geom[key][2][i+1])
            # glEnd()


def draw_connection_wireframe(self, segment):
    """Draw an airfoil using coordinates from a file, extruded along the z-axis."""
    glLineWidth(2)
    le_ps = segment.geom['le_ps']
    te_ps = segment.geom['te_ps']
    le_ss = segment.geom['le_ss']
    te_ss = segment.geom['te_ss']

    if not all(arr is not None and len(arr) > 0 for arr in [le_ps, te_ps, le_ss, te_ss]):
        logger.error("Invalid airfoil data:", segment.geom)
        return

    # Draw edges connecting front and back faces
    glColor3f(0.0, 0.0, 1.0)  # Blue color for leading edge
    glBegin(GL_LINES)
    for i in range(len(le_ps[0])-1):
        glVertex3f(le_ps[0][i], le_ps[1][i], segment.params['origin_Z'])
        glVertex3f(le_ps[0][i+1], le_ps[1][i+1], segment.params['origin_Z'])
    glEnd()

    glColor3f(0.0, 1.0, 0.0)  # Green color for presssure side
    glBegin(GL_LINES)
    for i in range(len(te_ps[0])-1):
        glVertex3f(te_ps[0][i], te_ps[1][i], segment.params['origin_Z'])
        glVertex3f(te_ps[0][i+1], te_ps[1][i+1], segment.params['origin_Z'])
    glEnd()

    glColor3f(1.0, 0.0, 0.0)  # Red color for suction side
    glBegin(GL_LINES)
    for i in range(len(le_ss[0])-1):
        glVertex3f(le_ss[0][i], le_ss[1][i], segment.params['origin_Z'])
        glVertex3f(le_ss[0][i+1], le_ss[1][i+1], segment.params['origin_Z'])
    glEnd()

    glColor3f(1.0, 1.0, 0.0)  # Yellow color for trailing edge
    glBegin(GL_LINES)
    for i in range(len(te_ss[0])-1):
        glVertex3f(te_ss[0][i], te_ss[1][i], segment.params['origin_Z'])
        glVertex3f(te_ss[0][i+1], te_ss[1][i+1], segment.params['origin_Z'])
    glEnd()