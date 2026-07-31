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
from OpenGL.GL import (
    glEnableClientState, glDisableClientState,
    glVertexPointer, glDrawArrays, glColor3f, glColor4f,
    glEnable, glDisable, glLineStipple,
    GL_VERTEX_ARRAY, GL_FLOAT, GL_LINE_STRIP, GL_LINE_STIPPLE
)

# Słownik wzorów bitowych (16-bitowych) oraz bazowych skali
# (skala, pattern_16bit)
LINE_STYLES = {
    'solid':   (1, 0xFFFF), # Ciągła
    'dashed':  (2, 0x00FF), # Kreskowana: 8px linia, 8px przerwa
    'dotted':  (1, 0x5555), # Kropkowana: 1px linia, 1px przerwa (lub 0x1111)
    'dashdot': (2, 0x1E3F), # Kreska-kropka: długa kreska, spacja, kropka, spacja
}

def draw_styled_line(points, color=None, style='solid', factor=0.5):
    """
    Rysuje linię z określonym stylem (solid, dashed, dotted, dashdot).
    Dzięki glLineStipple wzór linii jest liczony w pikselach ekranu, 
    więc jest w pełni odporny na skalowanie/zoom w rzutni.
    Jak dostosować długości kresek i kropek?Wzorzec pattern to 16-bitowa liczba szesnastkowa:
    0x00FF = 0000000011111111 --> 8 bitów pustych, 8 bitów rysowanych (klasyczny dash).
    0x5555 = 0101010101010101 --> gęste kropki (1 piksel rysowany, 1 wygaszony).
    Parametr factor w glLineStipple(factor, pattern) działa jak mnożnik pikseli. Przy factor = 2 każdy bit wzoru zajmuje 2 piksele na Twoim monitorze.
    
    :param points: punkty linii (NumPy array lub lista)
    :param color: tuple/list koloru (RGB lub RGBA)
    :param style: 'solid', 'dashed', 'dotted', 'dashdot'
    :param factor: mnożnik gęstości wzoru (np. factor=2 podwoi długość kresek)
    """
    if points is None:
        return

    vertices = np.asarray(points, dtype=np.float32)
    if vertices.size == 0:
        return

    if vertices.ndim == 1:
        vertices = vertices.reshape(1, -1)
    elif vertices.ndim == 2 and vertices.shape[0] in (2, 3) and vertices.shape[1] not in (2, 3):
        vertices = vertices.T

    if vertices.ndim != 2 or vertices.shape[1] not in (2, 3):
        return

    # 1. Ustawienie koloru
    if color is not None:
        if len(color) >= 4:
            glColor4f(*color)
        else:
            glColor3f(*color)

    # 2. Ustawienie stipplingu (stylu linii)
    is_stippled = style != 'solid' and style in LINE_STYLES
    if is_stippled:
        base_factor, pattern = LINE_STYLES[style]
        glEnable(GL_LINE_STIPPLE)
        # stipple_factor określa ile pikseli na ekranie odpowiada 1 bitowi wzoru
        glLineStipple(int(base_factor * factor), pattern)

    # 3. Rysowanie geometrii
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(vertices.shape[1], GL_FLOAT, 0, vertices)
    glDrawArrays(GL_LINE_STRIP, 0, len(vertices))
    glDisableClientState(GL_VERTEX_ARRAY)

    # 4. Wyłączenie stipplingu dla reszty renderowania
    if is_stippled:
        glDisable(GL_LINE_STIPPLE)