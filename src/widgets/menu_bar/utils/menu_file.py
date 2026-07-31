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

from PyQt6.QtWidgets import (
    QFileDialog, QApplication, QMessageBox, QDialog
)

from src.widgets.widget_description import EditDescriptionDialog

def new_project(self):
    if self.main_window.PROJECT:
        msg = QMessageBox.question(self, "New Project", "Do you want to create a new project?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if msg == QMessageBox.StandardButton.Yes:
            self.logger.info("Creating new project...")
            self.main_window.PROJECT.new()
            if self.current_module == 'airfoil' and self.main_window.AIRFOIL_MODULE:
                self.main_window.AIRFOIL_MODULE.refresh()
            elif self.current_module == 'wing' and self.main_window.WING_MODULE:
                if hasattr(self.main_window.WING_MODULE, 'init_tree'):
                    self.main_window.WING_MODULE.init_tree()

def open_project(self):
    if self.main_window.PROJECT:
        # options = QFileDialog.Option.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Daedalus Database Files (*.ddls);; All Files (*)")
        if fileName:
            self.main_window.PROJECT.open(fileName)
            if self.current_module == 'airfoil' and self.main_window.AIRFOIL_MODULE:
                if hasattr(self.main_window.AIRFOIL_MODULE, 'refresh'):
                    self.main_window.AIRFOIL_MODULE.refresh()
            if self.current_module == 'wing' and self.main_window.WING_MODULE:
                if hasattr(self.main_window.WING_MODULE, 'refresh'):
                    self.main_window.WING_MODULE.refresh()
            self.logger.info(f"Opened file: {fileName}")

def save_project(self):
    if self.main_window.PROJECT:
        if self.main_window.PROJECT.path:
            self.main_window.PROJECT.save()
        else:
            save_as_project(self)

def save_as_project(self):

    if self.main_window.PROJECT:
        default_name = f"{self.main_window.PROJECT.name}.ddls" if self.main_window.PROJECT.name else f"Untitled.ddls"
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", default_name, "Daedalus Database Files (*.ddls);; All Files (*)")
        print('filepath', filePath)
        print('_', _)
        if filePath:
            self.main_window.PROJECT.save_as(filePath)
            self.logger.info(f"Saved file: {filePath}")

def edit_description_project(self):
    """Edit the description of the project"""
    self.logger.info("Editing description of the project...")
    
    if self.main_window.PROJECT:

        dialog = EditDescriptionDialog(self.main_window.PROJECT.description, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_text = dialog.get_text()
            self.main_window.PROJECT.set_description(new_text)

            if self.main_window.current_module == 'airfoil':
                dock_wrapper = self.main_window.dock_widgets.get('airfoil_description_text')
            if self.main_window.current_module == 'wing':
                dock_wrapper = self.main_window.dock_widgets.get('wing_description_text')
            
            if dock_wrapper:
                desc_widget = dock_wrapper.widget()
                if desc_widget:
                    desc_widget.set_description()
    else: 
        self.logger.error("No PROJECT asigned!")

def export_project(self):
    if self.main_window.PROJECT:
        fileName, _ = QFileDialog.getSaveFileName(self, "Export File", "", "STEP AP203 (*.step;*.stp);")
        if fileName:
            import src.utils.step as step
            base_name = os.path.basename(fileName)
            step.export_3d_segment_wing(fileName, base_name)
            self.logger.info(f"Exported file: {fileName}")

def exit_program(self):
    msg = QMessageBox.question(None, "Exit program", "Do you really want to quit a program?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    if msg == QMessageBox.StandardButton.Yes:
        self.logger.info("Exit")
        QApplication.quit()