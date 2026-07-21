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

def nice_tick_spacing(span, target_ticks=10):
    """
    span: visible world range (max - min)
    target_ticks: desired number of ticks on screen
    """
    raw = span / target_ticks
    exp = math.floor(math.log10(raw))
    base = raw / (10 ** exp)

    if base <= 1:
        nice = 1
    elif base <= 2:
        nice = 2
    elif base <= 5:
        nice = 5
    else:
        nice = 10

    return nice * (10 ** exp)

def precision_from_spacing(spacing):
    if spacing >= 1:
        return 0
    return max(0, -int(math.floor(math.log10(spacing))))

def compute_2D_world_bounds(width, height, zoom, translation_X, translation_Y):
    aspect = width / height if height > 0 else 1.0
    half_w = zoom * aspect
    half_h = zoom
    tx = translation_X
    ty = translation_Y

    left = -half_w - tx
    right = half_w - tx
    bottom = -half_h - ty
    top = half_h - ty

    return left, right, bottom, top