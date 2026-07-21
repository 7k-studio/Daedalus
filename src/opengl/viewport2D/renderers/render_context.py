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

from dataclasses import dataclass


@dataclass
class RenderContext:
    """Shared state passed to viewport renderers."""

    camera: object
    width: int
    height: int
    viewport_settings: dict
    airfoil_settings: dict
    bg_color: tuple
    grid_color: tuple
    minor_grid_color: tuple
    ruler_color: tuple
    text_color: tuple
    text_renderer: object = None
    daedalus: object = None
    project: object = None

    @classmethod
    def from_viewport(cls, viewport):
        return cls(
            camera=viewport.camera,
            width=viewport.width(),
            height=viewport.height(),
            viewport_settings=getattr(viewport, "viewport_settings", {}),
            airfoil_settings=getattr(viewport, "airfoil_settings", {}),
            bg_color=getattr(viewport, "bg_color", (0, 0, 0)),
            grid_color=getattr(viewport, "grid_color", (0, 0, 0)),
            minor_grid_color=getattr(viewport, "minor_grid_color", (0, 0, 0)),
            ruler_color=getattr(viewport, "ruler_color", (0, 0, 0)),
            text_color=getattr(viewport, "text_color", (255, 255, 255)),
            text_renderer=getattr(viewport, "text_renderer", None),
            daedalus=getattr(viewport, "DAEDALUS", None),
            project=getattr(viewport, "PROJECT", None),
        )
