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
from PyQt6.QtCore import Qt


class PanTool:
    """Simple pan interaction for the 2D viewport."""

    def __init__(self, viewport):
        self.viewport = viewport

    def mouse_press(self, event):
        self.viewport.lastPos = event.position()

    def mouse_move(self, event):
        pos = event.position()
        dx = pos.x() - self.viewport.lastPos.x()
        dy = pos.y() - self.viewport.lastPos.y()

        if event.buttons() & Qt.MouseButton.LeftButton:
            aspect = self.viewport.width() / max(1, self.viewport.height())
            world_width = 2 * self.viewport.camera.zoom * aspect
            world_height = 2 * self.viewport.camera.zoom

            self.viewport.camera.center[0] -= dx * world_width / self.viewport.width()
            self.viewport.camera.center[1] += dy * world_height / self.viewport.height()

        self.viewport.lastPos = pos
        self.viewport.update()

    def mouse_release(self, event):
        self.viewport.update()
