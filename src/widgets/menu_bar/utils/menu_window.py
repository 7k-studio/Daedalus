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

def update_action_state(menu_obj, action, dock_widget):
    """Update the state of the given action based on the dock widget's visibility."""
    action.setChecked(dock_widget.isVisible())

def toggle_airfoil(menu_obj):
    """Toggle the description widget."""
    if menu_obj.parent():
        menu_obj.parent().toggle_airfoil()  # Call the correct method in AirfoilDesigner

def toggle_parameters(menu_obj):
    """Toggle the description widget."""
    if menu_obj.parent():
        menu_obj.parent().toggle_parameters()  # Call the correct method in AirfoilDesigner

def toggle_statistics(menu_obj):
    """Toggle the description widget."""
    if menu_obj.parent():
        menu_obj.parent().toggle_statistics()  # Call the correct method in AirfoilDesigner

def toggle_reference(menu_obj):
    """Toggle the description widget."""
    if menu_obj.parent():
        menu_obj.parent().toggle_reference()  # Call the correct method in AirfoilDesigner

def toggle_description(menu_obj):
    """Toggle the description widget."""
    if menu_obj.parent():
        menu_obj.parent().toggle_description()  # Call the correct method in AirfoilDesigner

def toggle_logger(menu_obj):
    """Toggle the description widget."""
    if menu_obj.parent():
        menu_obj.parent().toggle_logger()  # Call the correct method in AirfoilDesigner
        