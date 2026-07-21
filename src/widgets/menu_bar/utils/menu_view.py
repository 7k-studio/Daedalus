'''

Copyright (C) 2025-2026 Jakub Kamyk

This file is part of PROGRAM.

PROGRAM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

PROGRAM is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PROGRAM.  If not, see <http://www.gnu.org/licenses/>.

'''

def showCurvComb(menu_obj):
    pass

def showCamberline(menu_obj):
    pass

def chgPersp(menu_obj):
    menu_obj.open_gl.toggle_projection()

def view_X_up(menu_obj):
    menu_obj.open_gl.position_view(90.0,0.0)

def view_Y_up(menu_obj):
    menu_obj.open_gl.position_view(0,90)

def view_Z_up(menu_obj):
    menu_obj.open_gl.position_view(0.0,0.0)

def view_X_down(menu_obj):
    menu_obj.open_gl.position_view(-90.0,0.0)

def view_Y_down(menu_obj):
    menu_obj.open_gl.position_view(0,-90)

def view_Z_down(menu_obj):
    menu_obj.open_gl.position_view(0.0,180.0)

def placeholder(menu_obj):
    menu_obj.logger.info("Placeholder action triggered")
        