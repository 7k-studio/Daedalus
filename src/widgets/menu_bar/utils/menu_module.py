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

def change_to_wing_module(menu_obj):
    menu_obj.main_window.switch_to_module('wing')

def change_to_airfoil_module(menu_obj):
    menu_obj.main_window.switch_to_module('airfoil')