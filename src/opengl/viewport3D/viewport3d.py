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
import sys
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

# PyOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *

from .renderers import controlpoints_renderer, grid_renderer, coordinate_renderer, wireframe_renderer, surface_renderer
from .camera import Camera3D
from .interaction.pan_tool import PanTool
from .interaction.zoom_tool import ZoomTool


class Viewport3D(QOpenGLWidget):
    """
    Simple CAD-like OpenGL viewport with:
      - Orbit rotation around a center (target)
      - Pan/translate view
      - Zoom (mouse wheel or right-drag)

    Controls:
      - Left Mouse Drag: Orbit (yaw/pitch)
      - Middle Mouse Drag: Pan (translate target in view plane)
      - Right Mouse Drag: Dolly Zoom (forward/back)
      - Mouse Wheel: Zoom in/out
      - Double-click Left: Reset view
    """

    def __init__(self, program=None, parent=None, project=None):
        super().__init__(None)

        self.DAEDALUS = program
        self.WINGDESIGNER = parent
        self.PROJECT = project

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.viewport_settings = self.DAEDALUS.preferences["wing_designer"]["viewport"]
        self.wing_settings = self.DAEDALUS.preferences["wing_designer"]["wing"]

        self.camera = Camera3D()
        self.pan_tool = PanTool(self)
        self.zoom_tool = ZoomTool(self)

        # Interaction
        self._last_pos = None
        self._active_button = None

        # Pan offsets are stored by moving the target in world space
        # but we compute deltas in view space and transform to world

    # -------- OpenGL setup --------
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_CULL_FACE)
        #glCullFace(GL_BACK)

        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glClearColor(1.0, 1.0, 1.0, 1.0)  # dark background

        # Light (very simple)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 8.0, 5.0, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.9, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))

    def resizeGL(self, w, h):
        h = max(1, h)
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera.fov_y, w / float(h), self.camera.near, self.camera.far)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        if getattr(self.PROJECT, 'is_recalculating', False):
            return
    
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set up camera (orbit around target)
        eye = self.camera.eye_position()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(eye.x(), eye.y(), eye.z(),
                  self.camera.target.x(), self.camera.target.y(), self.camera.target.z(),
                  0.0, 1.0, 0.0)

        if self.viewport_settings["grid"]["show"]:
            grid_renderer._draw_grid()
        #self._draw_demo_geometry()

        # Drawing objects
        for i, component in enumerate(self.PROJECT.components):

            coordinate_renderer.draw_origin_arrows(
                self, 
                zoom=self.camera.distance, 
                origin_x=component.params['origin_X'].get(), 
                origin_y=component.params['origin_Y'].get(), 
                origin_z=component.params['origin_Z'].get()
            )

            for j, wing in enumerate(component.wings):
                
                #controlpoints_renderer.draw_cp_net(PROJECT.components[i].wings[j], self.camera.distance)
                
                for k, segment in enumerate(wing.segments):
                    self.logger.debug(f"Drawing objects from Component idx: {i}, Wing idx: {j}, Segment idx {k}")
                    try:
                        
                        if self.wing_settings["wireframe"]["show"]:
                            self.logger.debug(f"Drawing wireframe")
                            wireframe_renderer.draw_wireframe(self.PROJECT, i, j, k)
                    except Exception as e:
                        self.logger.error(f"An error occured during wireframe drawing: {e}")

                        
                    if len(wing.segments) > 1 and wing.skin:

                        patch_keys = ["PS", "SS", "LE", "TE"]

                        if self.wing_settings["grid"]["show"]:
                            for key in patch_keys:
                                patch = getattr(wing.skin, key, None)
                                if patch and getattr(patch, 'control_grid', None):
                                    try:
                                        controlpoints_renderer.draw_cp_grid(patch.control_grid)
                                    except Exception as e:
                                        self.logger.error(f"An error occured during CP Grid drawing: {e}")

                        if self.wing_settings["solid"]["show"]:
                            for key in patch_keys:
                                patch = getattr(wing.skin, key, None)
                                if patch and getattr(patch, 'geom', None):
                                    try:
                                        surface_renderer.draw_patch_fill(patch)
                                    except Exception as e:
                                        self.logger.error(f"An error occured during surface drawing: {e}")

        # Check for errors after drawing
        error = glGetError()
        if error != GL_NO_ERROR:
            self.logger.error(f"OpenGL Error after airfoil: {(error)}") #gluErrorString

    # -------- Interaction --------
    def mousePressEvent(self, event):
        self._active_button = event.button()
        if self._active_button == QtCore.Qt.MouseButton.MiddleButton:
            self.pan_tool.mouse_press(event)
        else:
            self._last_pos = event.position()
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        self._active_button = None
        self._last_pos = None
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.pan_tool.mouse_release(event)
        else:
            self.unsetCursor()

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.reset_view()

    def mouseMoveEvent(self, event):
        pos = event.position()

        if self._last_pos is None and self._active_button != QtCore.Qt.MouseButton.MiddleButton:
            return

        if self._active_button == QtCore.Qt.MouseButton.LeftButton:
            dx = pos.x() - self._last_pos.x()
            dy = pos.y() - self._last_pos.y()
            self.camera.yaw -= dx * 0.4
            self.camera.pitch += dy * 0.3
            self.camera.pitch = max(-89.5, min(89.5, self.camera.pitch))
            self._last_pos = pos
            self.update()

        elif self._active_button == QtCore.Qt.MouseButton.MiddleButton:
            self.pan_tool.mouse_move(event)

        elif self._active_button == QtCore.Qt.MouseButton.RightButton:
            dx = pos.x() - self._last_pos.x()
            dy = pos.y() - self._last_pos.y()
            self._dolly(dy)
            self._last_pos = pos
            self.update()

    def wheelEvent(self, event):
        self.zoom_tool.wheel(event)

    def reset_view(self):
        self.camera.reset()
        self.update()
    
    def position_view(self, yaw, pitch):
        self.camera.position(yaw, pitch)
        self.update()

    # -------- Helpers --------
    def _spherical_to_cartesian(self, r, yaw_rad, pitch_rad):
        return self.camera.spherical_to_cartesian(r, yaw_rad, pitch_rad)

    def _camera_basis(self):
        return self.camera.basis()

    def _pan(self, dx, dy):
        self.camera.pan(dx, dy, self.width(), self.height())

    def _dolly(self, dy):
        self.camera.dolly(dy)

    def _draw_demo_geometry(self):
        # A lit cube at the origin, so you can see rotation around target
        glPushMatrix()
        glTranslatef(0.0, 0.5, 0.0)
        glScalef(1.0, 1.0, 1.0)
        glColor3f(0.85, 0.85, 0.88)
        self._draw_unit_cube()
        glPopMatrix()

    def _draw_unit_cube(self):
        # Draw a unit cube centered at origin spanning [-0.5, 0.5]
        vertices = [
            (-0.5, -0.5,  0.5), ( 0.5, -0.5,  0.5), ( 0.5,  0.5,  0.5), (-0.5,  0.5,  0.5),  # front
            (-0.5, -0.5, -0.5), ( 0.5, -0.5, -0.5), ( 0.5,  0.5, -0.5), (-0.5,  0.5, -0.5),  # back
        ]
        faces = [
            (0, 1, 2, 3, (0, 0, 1)),   # front
            (1, 5, 6, 2, (1, 0, 0)),   # right
            (5, 4, 7, 6, (0, 0, -1)),  # back
            (4, 0, 3, 7, (-1, 0, 0)),  # left
            (3, 2, 6, 7, (0, 1, 0)),   # top
            (4, 5, 1, 0, (0, -1, 0)),  # bottom
        ]
        glBegin(GL_QUADS)
        for (a, b, c, d, n) in faces:
            glNormal3f(*n)
            glVertex3f(*vertices[a])
            glVertex3f(*vertices[b])
            glVertex3f(*vertices[c])
            glVertex3f(*vertices[d])
        glEnd()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAD-like OpenGL Viewport (PyQt6)")
        self.resize(1000, 700)

        self.viewport = Viewport3D(self)
        self.setCentralWidget(self.viewport)

        # Status bar with quick hints
        self.status = self.statusBar()
        self.status.showMessage("LMB: Orbit | MMB: Pan | RMB/Wheel: Zoom | Double LMB: Reset")


def configure_surface_format():
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    fmt.setStencilBufferSize(8)
    fmt.setVersion(2, 1)  # compatibility profile is fine for fixed-function
    fmt.setProfile(QSurfaceFormat.Profile.CompatibilityProfile)
    fmt.setSamples(4)  # MSAA
    QSurfaceFormat.setDefaultFormat(fmt)


def main():
    configure_surface_format()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
