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
from PyQt6.QtWidgets import QFileDialog, QMessageBox

def fit2ref(menu_obj):
    """Open the reference-fitting dialog for the selected airfoil."""
    menu_obj.logger.info("Opening Fit2Ref window...")
    module = menu_obj.main_window.AIRFOIL_MODULE
    if module:
        module.fit2Reference()

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

def duplicate_airfoil(menu_obj):
    menu_obj.main_window.AIRFOIL_MODULE.duplicateAirfoil()

def delete_airfoil(menu_obj):
    msg = QMessageBox.question(None, "Delete Airfoil", "Are you sure you want to delete the airfoil? Current version of the program does not have an Undo button!", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    if msg == QMessageBox.StandardButton.Yes:
        menu_obj.main_window.AIRFOIL_MODULE.deleteAirfoil()

def delete_component(menu_obj):
    msg = QMessageBox.question(None, "Delete Component", "Are you sure you want to delete the component? Current version of the program does not have an Undo button!", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    if msg == QMessageBox.StandardButton.Yes:
        menu_obj.main_window.WING_MODULE.deleteComponent()

def delete_wing(menu_obj):
    msg = QMessageBox.question(None, "Delete Wing", "Are you sure you want to delete the wing? Current version of the program does not have an Undo button!", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    if msg == QMessageBox.StandardButton.Yes:
        menu_obj.main_window.WING_MODULE.deleteWing()

def delete_segment(menu_obj):
    msg = QMessageBox.question(None, "Delete Segment", "Are you sure you want to delete the segment? Current version of the program does not have an Undo button!", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    if msg == QMessageBox.StandardButton.Yes:
        menu_obj.main_window.WING_MODULE.deleteSegment()
