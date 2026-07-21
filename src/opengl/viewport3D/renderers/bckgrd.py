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
from OpenGL.GLU import gluPerspective  # Add this import

import src.opengl.tools_opengl as tools

import math

#from .test_cube import draw_object_from_file  # Import the new function
logger = logging.getLogger(__name__)

def draw_ruler(self, linewidth=2, size=1000, step=1, zoom = -10):
    glLineWidth(linewidth)
    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_LINES)

    # Adjust scale based on zoom level
    if -zoom < 2:
        scale = 100  
    else:
        scale = 10

    #Drawing ruller lines: main axis
    for i in range(-size, size + 1, step):
        # Vertical lines [ X | Y | Z ]
        glVertex3f(i/scale, 0, 0)
        glVertex3f(i/scale, 0.01*(-zoom), 0)
        # Horizontal lines [ X | Y | Z ]
        glVertex3f(0, i/scale, 0)
        glVertex3f(0.01*(-zoom), i/scale, 0)
    for i in range(0, 40 + 1, step):
        # Depth lines [ X | Y | Z ]
        glVertex3f(0, 0, i/scale)
        glVertex3f(0.01*(-zoom), 0, i/scale)

    for i in range(-size, size + 1, int(step*10)):
        # Vertical lines [ X | Y | Z ]
        glVertex3f(i/10, 0, 0)
        glVertex3f(i/10, 0.2, 0)
        # Horizontal lines [ X | Y | Z ]
        glVertex3f(0, i/10, 0)
        glVertex3f(0.2, i/10, 0)
    for i in range(0, 40 + 1, int(step*10)):
        # Depth lines [ X | Y | Z ]
        glVertex3f(0, 0, i/10)
        glVertex3f(0.2, 0, i/10)

    glVertex3f(-size, 0, 0)
    glVertex3f(size + 1, 0, 0)

    glVertex3f(0, -size, 0)
    glVertex3f(0, size + 1, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 4 + 1)  
    
    glEnd()

def draw_ruler_2d(self, linewidth=2, size=1000, step=1, zoom = -10):
    glLineWidth(linewidth)
    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_LINES)

    # Adjust scale based on zoom level
    if -zoom < 2:
        scale = 100  
    else:
        scale = 10

    #Drawing ruller lines: main axis
    for i in range(-size, size + 1, step):
        # Vertical lines [ X | Y | Z ]
        glVertex3f(i/scale, 0, 0)
        glVertex3f(i/scale, 0.01*(-zoom), 0)
        # Horizontal lines [ X | Y | Z ]
        glVertex3f(0, i/scale, 0)
        glVertex3f(0.01*(-zoom), i/scale, 0)

    for i in range(-size, size + 1, int(step*10)):
        # Vertical lines [ X | Y | Z ]
        glVertex3f(i/10, 0, 0)
        glVertex3f(i/10, 0.2, 0)
        # Horizontal lines [ X | Y | Z ]
        glVertex3f(0, i/10, 0)
        glVertex3f(0.2, i/10, 0)

    glVertex3f(-size, 0, 0)
    glVertex3f(size + 1, 0, 0)

    glVertex3f(0, -size, 0)
    glVertex3f(0, size + 1, 0)
    
    glEnd()

def draw_ruler(self, bg_color, ruler_color, grid_color,size=20):
    """Draws a ruler with tick marks and labels using OpenGL."""
    # GUI sizing
    margin = 6
    gui_w, gui_h = 40, 40
    width = float(self.width())
    height = float(self.height())
    tick_px_height = max(6.0, gui_h * 0.4)
    tick_px_width = max(6.0, gui_w * 0.4)

    # Draw GUI background rectangles (top horizontal and left vertical)
    glDisable(GL_DEPTH_TEST)
    # horizontal bar (top)
    glBegin(GL_QUADS)
    glColor3f(self.bg_color[0]/255, self.bg_color[1]/255, self.bg_color[2]/255)
    glVertex2f(gui_w, height)
    glVertex2f(gui_w, height - gui_h)
    glVertex2f(width, height - gui_h)
    glVertex2f(width, height)
    glEnd()

    # vertical bar (left)
    glBegin(GL_QUADS)
    glColor3f(self.bg_color[0]/255, self.bg_color[1]/255, self.bg_color[2]/255)
    glVertex2f(0, 0)
    glVertex2f(0, height - gui_h)
    glVertex2f(gui_w, height - gui_h)
    glVertex2f(gui_w, 0)
    glEnd()

    glColor3f(self.ruler_color[0]/255, self.ruler_color[1]/255, self.ruler_color[2]/255)

    left, right, bottom, top = self.camera.world_bounds(self.width(),self.height())
    # Determine tick spacing based on zoom magnitude
    world_span_x = right - left
    world_span_y = top - bottom

    tick_spacing = tools.nice_tick_spacing(world_span_x, target_ticks=10)
    minor_spacing = tick_spacing / 5
    precision = tools.precision_from_spacing(tick_spacing)
    label_fmt = f"{{:.{precision}f}}"

    # Helper to map world x->screen x and world y->screen y
    def worldx_to_screen(wx):
        return (wx - left) / (right - left) * width if right != left else 0

    def worldy_to_screen(wy):
        # screen Y goes from 0 (top) to height (bottom) because ortho set that way
        return height - ( (wy - bottom) / (top - bottom) * height ) if top != bottom else height/2

    glLineWidth(1.0)

    # Draw minor ticks
    mx = math.floor(left / minor_spacing) * minor_spacing
    while mx <= right:
        sx = worldx_to_screen(mx)
        glBegin(GL_LINES)
        glVertex2f(sx, height - gui_h)
        glVertex2f(sx, height - gui_h + tick_px_height * 0.4)
        glEnd()
        mx += minor_spacing

    my = math.floor(bottom / minor_spacing) * minor_spacing
    while my <= top:
        sy = worldy_to_screen(my)
        glBegin(GL_LINES)
        glVertex2f(gui_w - tick_px_width * 0.4, sy)
        glVertex2f(gui_w, sy)
        glEnd()
        my += minor_spacing

    # Draw X major ticks (top horizontal ruler)
    start_x = math.floor(left / tick_spacing) * tick_spacing
    x = start_x
    while x <= right:
        sx = worldx_to_screen(x)
        # draw small vertical tick into the top ruler area
        glColor3f(self.ruler_color[0]/255, self.ruler_color[1]/255, self.ruler_color[2]/255)  # Set color each iteration
        glBegin(GL_LINES)
        glVertex2f(sx, height - gui_h)
        glVertex2f(sx, height - gui_h + tick_px_height)
        glEnd()
        # label below tick inside top bar
        if abs(x) < tick_spacing * 0.5: # abs(x) > 1e-9:
            label = 0 # f"{x:.1f}"
        else:
            label = label_fmt.format(x) # "0"
        self.draw_text(label, sx + 0, height - gui_h + tick_px_height + 12, centered=True)
        x += tick_spacing

    # Draw Y major ticks (left vertical ruler)
    start_y = math.floor(bottom / tick_spacing) * tick_spacing
    y = start_y
    while y <= top:
        sy = worldy_to_screen(y)
        # draw small horizontal tick into the left ruler area
        glColor3f(self.ruler_color[0]/255, self.ruler_color[1]/255, self.ruler_color[2]/255)  # Set color each iteration
        glBegin(GL_LINES)
        glVertex2f(gui_w - tick_px_width, sy)
        glVertex2f(gui_w, sy)
        glEnd()
        if abs(y) < tick_spacing * 0.5:
            label = 0
        else:
            label = label_fmt.format(y)
        self.draw_text(label, gui_w - tick_px_width - 12, sy+0, angle=90, centered=True) # Add label
        y += tick_spacing
    
    glLineWidth(1.0)  # Reset line width

    # crop overlapping bottom
    glBegin(GL_QUADS)
    glColor3f(self.bg_color[0]/255, self.bg_color[1]/255, self.bg_color[2]/255)
    glVertex2f(0, height)
    glVertex2f(gui_w, height)
    glVertex2f(gui_w, height - gui_h)
    glVertex2f(0, height - gui_h)
    glEnd()

    # decorative with unit symbol
    glBegin(GL_LINE_STRIP)
    glColor3f(self.ruler_color[0]/255, self.ruler_color[1]/255, self.ruler_color[2]/255)
    glVertex2f(margin, height - gui_h + margin)
    glVertex2f(gui_w-margin, height - gui_h + margin)
    glVertex2f(gui_w-margin, height - margin)
    glVertex2f(margin, height - margin)
    glVertex2f(margin, height - gui_h + margin)
    glEnd()
    self.draw_text(self.DAEDALUS.preferences['general']['units']['length'], 20, self.height()-20, centered=True)

    # decorative cut-off from viewport
    glBegin(GL_LINE_STRIP)
    glColor3f(self.grid_color[0]/255, self.grid_color[1]/255, self.grid_color[2]/255)
    glVertex2f(gui_w, height - gui_h)
    glVertex2f(width, height - gui_h)
    glEnd()
    glBegin(GL_LINE_STRIP)
    glColor3f(self.grid_color[0]/255, self.grid_color[1]/255, self.grid_color[2]/255)
    glVertex2f(gui_w, height - gui_h)
    glVertex2f(gui_w, 0)
    glEnd()
    
    glEnable(GL_DEPTH_TEST)