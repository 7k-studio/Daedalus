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
from PyQt6.QtCore import QPoint
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluOrtho2D, gluProject  # Add this import

#from .test_cube import draw_object_from_file  # Import the new function
from .renderers.text_renderer import FreetypeTextRenderer
from .renderers import grid_renderer, ruler_renderer, airfoil_renderer
from .renderers.render_context import RenderContext
from .interaction.pan_tool import PanTool
from .interaction.zoom_tool import ZoomTool

import src.opengl.tools_opengl as tools
from .camera import Camera2D

class ViewportOpenGL(QOpenGLWidget):
    def __init__(self, program=None, project=None, parent=None):
        super(ViewportOpenGL, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.PROJECT = project
        self.camera = Camera2D()

        self.translation = [-0.5, 0, 0]
        self.lastPos = QPoint()
        self.airfoil = None
        self.viewport_settings = self.DAEDALUS.preferences["airfoil_designer"]["viewport"]
        self.airfoil_settings = self.DAEDALUS.preferences["airfoil_designer"]["airfoil"]

        self.bg_color = self.DAEDALUS.AD_viewport_color[self.DAEDALUS.preferences['airfoil_designer']['viewport'].get('color_scheme', 'Bright')]['background']
        self.grid_color = self.DAEDALUS.AD_viewport_color[self.DAEDALUS.preferences['airfoil_designer']['viewport'].get('color_scheme', 'Bright')]['grid']
        self.minor_grid_color = self.DAEDALUS.AD_viewport_color[self.DAEDALUS.preferences['airfoil_designer']['viewport'].get('color_scheme', 'Bright')]['minor_grid']
        self.ruler_color = self.DAEDALUS.AD_viewport_color[self.DAEDALUS.preferences['airfoil_designer']['viewport'].get('color_scheme', 'Bright')]['ruler']
        self.text_color = self.DAEDALUS.AD_viewport_color[self.DAEDALUS.preferences['airfoil_designer']['viewport'].get('color_scheme', 'Bright')]['text']
        
        # Initialize Freetype text renderer
        self.text_renderer = FreetypeTextRenderer(font_size=10)
        self.pan_tool = PanTool(self)
        self.zoom_tool = ZoomTool(self)
    
    def clear(self):
        self.airfoil = None
        self.update()

    def set_airfoil_to_display(self, airfoil):
        self.airfoil = airfoil
        self.update()

    def initializeGL(self):
        glutInit()  # Initialize GLUT to enable text rendering
        glClearColor(self.bg_color[0]/255, self.bg_color[1]/255, self.bg_color[2]/255, 1)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        context = RenderContext.from_viewport(self)

        self._prepare_world_projection(context)

        if self.viewport_settings["grid"]["show"]:
            grid_renderer.draw(context)

        if self.airfoil:
            airfoil_renderer.draw_airfoil(self, self.airfoil)
            if self.airfoil_settings["control_points"]["show"]:
                airfoil_renderer.draw_cp_net(self, self.airfoil, self.camera.zoom)
            if self.airfoil_settings["construction"]["show"]:
                airfoil_renderer.draw_dashed_line(self, self.airfoil, 0.01, self.camera.zoom)
        
        if self.PROJECT.reference_airfoils:
            for reference in self.PROJECT.reference_airfoils:
                if reference.visible:
                    airfoil_renderer.draw_reference(self, reference)

        self._prepare_overlay_projection()

        glDisable(GL_DEPTH_TEST)
        if self.viewport_settings["ruler"]["show"]:
            ruler_renderer.draw(context)
        glEnable(GL_DEPTH_TEST)

        self._restore_projection_state()

    def _prepare_world_projection(self, context):
        left, right, bottom, top = self.camera.world_bounds(context.width, context.height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(left, right, bottom, top)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def _prepare_overlay_projection(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), self.height(), 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

    def _restore_projection_state(self):
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def world_to_screen(self, x, y):
        """Map OpenGL world coords → Qt screen coords for text placement."""
        model = glGetDoublev(GL_MODELVIEW_MATRIX)
        proj = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        winX, winY, winZ = gluProject(x, y, 0.0, model, proj, viewport)
        return winX, self.height() - winY  # flip Y for Qt

    def mousePressEvent(self, event):
        self.pan_tool.mouse_press(event)

    def mouseMoveEvent(self, event):
        self.pan_tool.mouse_move(event)

    def wheelEvent(self, event):
        self.zoom_tool.wheel(event)

    def mouseReleaseEvent(self, event):
        self.pan_tool.mouse_release(event)

    def toggle_projection(self):
        """Toggle between perspective and orthogonal views."""
        self.orthogonal = not self.orthogonal
        #self.resizeGL(self.width(), self.height())  # Ensure projection matrix is updated
        self.resizeGL(1200, 800)
        self.update()
    
    def fit_to_airfoil(self):
        if self.airfoil:
            ymax = max(self.airfoil.PS.spline.geom[1])
            ymin = min(self.airfoil.SS.spline.geom[1])
            xmax = min(self.airfoil.LE.spline.geom[0])
            xmin = max(self.airfoil.TE.spline.geom[0])

            self.logger.debug(f'\n| ymax | ymin | xmax | xmin |\n | {ymax} | {ymin} | {xmax} | {xmin} |')
            
            width = xmin - xmax
            height = ymax - ymin
            self.camera.zoom = max(width, height) * 0.6
            self.translation = [-(xmax + xmin) / 2, -(ymax + ymin) / 2, 0]
            self.resizeGL(self.width(), self.height())
            self.logger.info("Fitted to an airfoil")
        self.update()