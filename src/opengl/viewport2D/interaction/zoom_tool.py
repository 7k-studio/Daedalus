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

class ZoomTool:
    """Simple zoom interaction for the 2D viewport."""

    def __init__(self, viewport):
        self.viewport = viewport

    def wheel(self, event):
        factor = 0.9 if event.angleDelta().y() > 0 else 1.1
        self.viewport.camera.zoom *= factor
        self.viewport.update()
