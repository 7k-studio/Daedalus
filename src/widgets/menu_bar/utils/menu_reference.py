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

from PyQt6.QtWidgets import (
    QFileDialog, QDialog, QVBoxLayout
)

from src.widgets.widget_reference import WidgetReference

def add_reference(menu_obj):
    fileName, _ = QFileDialog.getOpenFileName(menu_obj, "Open File", "", "Accepted file formats (*.ddls; *.arf.ddls; *arf; *.txt; *.dat);; Daedalus Database Files (*.ddls);; Daedalus Airfoil Format (*.arf.ddls);; Daedalus v0.3 Airfoil Format (*.arf);; Cloud of points Files (*.txt; *.dat);; All Files (*)")
    if fileName:
        menu_obj.main_window.AIRFOIL_MODULE.addReference(fileName)
    else:
        menu_obj.logger.error("No file name provided")
        return

def manage_reference(menu_obj):
    dialog = QDialog(menu_obj)
    dialog.setWindowTitle("Reference Airfoils")
    dialog.setMinimumSize(400, 300)
    
    layout = QVBoxLayout(dialog)
    
    # 2. Instantiate your EXACT SAME TableReference widget
    floating_ui = WidgetReference(
        program=menu_obj.main_window.PROGRAM, 
        project=menu_obj.main_window.PROJECT, 
        parent=dialog, 
        airfoil_designer=menu_obj.main_window.AIRFOIL_MODULE
    )
    
    # 3. Add it to the dialog and run it
    layout.addWidget(floating_ui)
    dialog.exec()
        