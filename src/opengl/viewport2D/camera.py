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

import numpy as np


class Camera2D:
    def __init__(self):
        self.center = np.array([0.0, 0.0], dtype=float)
        self.zoom = 2.0

    @property
    def aspect(self, width, height):
        aspect = width / max(1, height)

        return aspect

    def world_bounds(self, width, height):
        aspect = width / max(1, height)

        left = self.center[0] - self.zoom * aspect
        right = self.center[0] + self.zoom * aspect

        bottom = self.center[1] - self.zoom
        top = self.center[1] + self.zoom

        return left, right, bottom, top

    def screen_to_world(self, sx, sy, width, height):

        left, right, bottom, top = self.world_bounds(width, height)
        x = left + sx / width * (right - left)
        y = top - sy / height * (top - bottom)

        return np.array([x, y])

    def world_to_screen(self, x, y, width, height):

        left, right, bottom, top = self.world_bounds(width, height)
        sx = (x - left) / (right - left) * width
        sy = (top - y) / (top - bottom) * height

        # Helper to map world x->screen x and world y->screen y
        # def worldx_to_screen(wx):
        #     return (wx - left) / (right - left) * width if right != left else 0

        # def worldy_to_screen(wy):
        #     # screen Y goes from 0 (top) to height (bottom) because ortho set that way
        #     return height - ( (wy - bottom) / (top - bottom) * height ) if top != bottom else height/2

        return sx, sy

    def fit_bbox(self, xmin, xmax, ymin, ymax, width, height, margin=0.05, optical_shift=0.08):

        aspect = self.aspect()

        bbox_w = xmax - xmin
        bbox_h = ymax - ymin

        bbox_w *= (1 + margin)
        bbox_h *= (1 + margin)

        zoom_x = bbox_w / (2 * aspect)
        zoom_y = bbox_h / 2

        self.zoom = max(zoom_x, zoom_y)

        chord = xmax - xmin

        self.center[:] = (
            (xmin + xmax) * 0.5 - optical_shift * chord,
            (ymin + ymax) * 0.5,
        )