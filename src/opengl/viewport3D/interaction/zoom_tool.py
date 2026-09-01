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

import math

from PyQt6 import QtCore


class ZoomTool:
    """Zoom interaction for the 3D viewport."""

    def __init__(self, viewport):
        self.viewport = viewport
        self._last_pos = None

    def mouse_press(self, event):
        self._last_pos = event.position()
        self.viewport.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)

    def mouse_move(self, event):
        if self._last_pos is None:
            return

        pos = event.position()
        dy = pos.y() - self._last_pos.y()

        self.viewport.camera.dolly(dy)
        self._last_pos = pos
        self.viewport.update()

    def mouse_release(self, event):
        self._last_pos = None
        self.viewport.unsetCursor()
        self.viewport.update()

    def wheel(self, event):
        delta_steps = event.angleDelta().y() / 120.0
        factor = math.pow(0.9, delta_steps)
        self.viewport.camera.distance = max(0.05, self.viewport.camera.distance * factor)
        self.viewport.update()
