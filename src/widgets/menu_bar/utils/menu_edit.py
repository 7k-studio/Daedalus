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
import os
from PyQt6.QtWidgets import QFileDialog

def fit2ref(menu_obj):
    """Fit the currently selected airfoil in airfoils_menu to the reference_airfoil by optimizing its parameters."""
    menu_obj.logger.info("Opening Fit2Ref window...")
    if menu_obj.main_window.AIRFOIL_MODULE:
        # Get selected item and corresponding airfoil object
        selected_items = menu_obj.main_window.AIRFOIL_MODULE.TREE_AIRFOIL.tree.selectedItems()
        if not selected_items:
            menu_obj.logger.warning("No airfoil selected in the tree menu.")
            return None
        selected_item = selected_items[0]
        airfoil_name = selected_item.text(0)
        # Find airfoil object by name
        current_airfoil = None
        import src.program.program as globals
        for af in globals.PROJECT.project_airfoils:
            if af.info.get('name', '') == airfoil_name:
                current_airfoil = af
                break
        if current_airfoil is None:
            menu_obj.logger.warning("Selected airfoil object not found.")
            return None
        
        # Open the Fit2RefWindow dialog
        import program.modules.arfdes.fit_2_reference as fit_2_reference
        dlg = fit_2_reference.Fit2RefWindow(parent=menu_obj.main_window.AIRFOIL_MODULE, current_airfoil=current_airfoil, reference_airfoil=menu_obj.main_window.AIRFOIL_MODULE.reference_airfoil)
        dlg.exec_()

def placeholder(menu_obj):
    menu_obj.logger.info("Placeholder action triggered")

def save_airfoil(menu_obj):
    airfoil = menu_obj.main_window.AIRFOIL_MODULE.TREE_AIRFOIL.selected_airfoil
    if not airfoil:
        menu_obj.logger.error("No valid airfoil selected!")
        return

    raw_name = airfoil.name if airfoil.name else "Untitled"
    clean_name = raw_name.split('.')[0]
    default_name = f"{clean_name}"

    filePath, _ = QFileDialog.getSaveFileName(None, "Save File", default_name, "DAEDALUS Airfoil Format (*.arf.ddls);;All Files (*)")
    menu_obj.logger.debug(f"Filepath: {filePath} /\n basename: {os.path.basename(filePath).split('.')[0]}")
    if filePath:
        while filePath.endswith(".arf.ddls.arf.ddls"):
            filePath = filePath[:-len(".arf.ddls")]

        if not filePath.endswith(".arf.ddls"):
            filePath += ".arf.ddls"
        print(filePath)
        menu_obj.main_window.AIRFOIL_MODULE.saveAirfoil(airfoil, filePath)

def append_airfoil(menu_obj):
    menu_obj.logger.info("Appending airfoil...")
    filePath, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Daedalus Airfoil Format (*.arf.ddls;*.arf);;All Files (*)")

    if filePath:
        menu_obj.main_window.AIRFOIL_MODULE.appendAirfoil(filePath)
    else:
        menu_obj.logger.error("No valid file path provided")
        return

def export_airfoil(menu_obj):

    airfoil = menu_obj.main_window.AIRFOIL_MODULE.TREE_AIRFOIL.selected_airfoil
    if not airfoil:
        menu_obj.logger.error("No valid airfoil selected!")

    default_name = f"{airfoil.name}.dxf" if airfoil.name else "Untitled.dxf"
    filePath, _ = QFileDialog.getSaveFileName(None, "Export File to DXF format", default_name, "DXF Format (*.dxf);;All Files (*)")
    if filePath:
        menu_obj.main_window.AIRFOIL_MODULE.exportAirfoil(airfoil, filePath)
    else:
        menu_obj.logger.error("No valid file path provided")
        return
        