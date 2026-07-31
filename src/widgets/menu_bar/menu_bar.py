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
import logging

from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction

import src.widgets.menu_bar.utils.menu_file as utils_file
import src.widgets.menu_bar.utils.menu_edit as utils_edit
import src.widgets.menu_bar.utils.menu_view as utils_view
import src.widgets.menu_bar.utils.menu_program as utils_program
import src.widgets.menu_bar.utils.menu_module as utils_module
import src.widgets.menu_bar.utils.menu_window as utils_window
import src.widgets.menu_bar.utils.menu_reference as utils_reference

class MenuBar(QMenuBar):
    def __init__(self, main_window):
        super(MenuBar, self).__init__(main_window)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.main_window = main_window

        self.current_module = None

        self.build_menu_bar()

    def build_menu_bar(self):
        self.file_menu = self.addMenu('File')
        self.edit_menu = self.addMenu('Edit')
        self.reference_menu = self.addMenu("Reference")
        self.view_menu = self.addMenu('View')
        self.window_menu = self.addMenu('Window')
        self.module_menu = self.addMenu('Module')
        self.program_menu = self.addMenu('Program')

        self._createFileMenu()
        self._rebuild_edit_menu()
        self._rebuild_view_menu()
        self._createWindowMenu()
        self._createModuleMenu()
        self._createProgramMenu()

        if self.reference_menu is not None:
            self._rebuild_reference_menu()

    def _createFileMenu(self):
        newAction = QAction('New', self)
        openAction = QAction('Open', self)
        saveAction = QAction('Save', self)
        saveAsAction = QAction('Save As', self)
        editDescAction = QAction('Edit project description', self)
        exportAction = QAction('Export', self)
        exitAction = QAction('Exit', self)

        newAction.triggered.connect(lambda: utils_file.new_project(self))
        openAction.triggered.connect(lambda: utils_file.open_project(self))
        saveAction.triggered.connect(lambda: utils_file.save_project(self))
        saveAsAction.triggered.connect(lambda: utils_file.save_as_project(self))
        editDescAction.triggered.connect(lambda: utils_file.edit_description_project(self))
        exportAction.triggered.connect(lambda: utils_file.export_project(self))
        exitAction.triggered.connect(lambda: utils_file.exit_program(self))

        self.file_menu.addAction(newAction)
        self.file_menu.addAction(openAction)
        self.file_menu.addAction(saveAction)
        self.file_menu.addAction(saveAsAction)
        self.file_menu.addSeparator()
        self.file_menu.addAction(editDescAction)
        self.file_menu.addSeparator()
        self.file_menu.addAction(exportAction)
        self.file_menu.addSeparator()
        self.file_menu.addAction(exitAction)

    def _rebuild_edit_menu(self):
        self.edit_menu.clear()
        if self.current_module == 'airfoil':
            newAirfoilAction = QAction('Add Airfoil', self)
            newAirfoilAction.triggered.connect(lambda: self.main_window.AIRFOIL_MODULE.addAirfoil() if self.main_window.AIRFOIL_MODULE else None)
            self.edit_menu.addAction(newAirfoilAction)

            appendAirfoilAction = QAction('Append Airfoil', self)
            appendAirfoilAction.triggered.connect(lambda: utils_edit.append_airfoil(self)) # this one need QFileDialog
            self.edit_menu.addAction(appendAirfoilAction)

            deleteAirfoilAction = QAction('Delete Airfoil', self)
            deleteAirfoilAction.triggered.connect(lambda: self.main_window.AIRFOIL_MODULE.deleteAirfoil() if self.main_window.AIRFOIL_MODULE else None)
            self.edit_menu.addAction(deleteAirfoilAction)

            saveAirfoilAction = QAction('Save Airfoil', self)
            saveAirfoilAction.triggered.connect(lambda: utils_edit.save_airfoil(self))
            self.edit_menu.addAction(saveAirfoilAction)

            exportAirfoilAction = QAction('Export Airfoil', self)
            exportAirfoilAction.triggered.connect(lambda: utils_edit.export_airfoil(self))
            self.edit_menu.addAction(exportAirfoilAction)

            flipAirfoilAction = QAction('Flip Airfoil', self)
            flipAirfoilAction.triggered.connect(lambda: self.main_window.AIRFOIL_MODULE.flipAirfoil() if self.main_window.AIRFOIL_MODULE else None)
            self.edit_menu.addAction(flipAirfoilAction)

            renameAirfoilAction = QAction('Rename Airfoil', self)
            renameAirfoilAction.triggered.connect(lambda: self.main_window.AIRFOIL_MODULE.renameAirfoil() if self.main_window.AIRFOIL_MODULE else None)
            self.edit_menu.addAction(renameAirfoilAction)

            if self.main_window.PROGRAM.preferences['general']['beta_features']:
                fit2refAction = QAction('Fit2Reference', self)
                fit2refAction.triggered.connect(self.fit2ref)
                self.edit_menu.addAction(fit2refAction)

        elif self.current_module == 'wing':
            addComponentAction = QAction('Add Component', self)
            addComponentAction.triggered.connect(lambda: self.main_window.WING_MODULE.addComponent() if self.main_window.WING_MODULE else None)
            self.edit_menu.addAction(addComponentAction)

            deleteComponentAction = QAction('Delete Component', self)
            deleteComponentAction.triggered.connect(lambda: self.main_window.WING_MODULE.deleteComponent() if self.main_window.WING_MODULE else None)
            self.edit_menu.addAction(deleteComponentAction)

            self.edit_menu.addSeparator()

            addWingAction = QAction('Add Wing', self)
            addWingAction.triggered.connect(lambda: self.main_window.WING_MODULE.addWing() if self.main_window.WING_MODULE else None)
            self.edit_menu.addAction(addWingAction)

            deleteWingAction = QAction('Delete Wing', self)
            deleteWingAction.triggered.connect(lambda: self.main_window.WING_MODULE.deleteWing() if self.main_window.WING_MODULE else None)
            self.edit_menu.addAction(deleteWingAction)

            self.edit_menu.addSeparator()

            addSegmentAction = QAction('Add Segment', self)
            addSegmentAction.triggered.connect(lambda: self.main_window.WING_MODULE.addSegment() if self.main_window.WING_MODULE else None)
            self.edit_menu.addAction(addSegmentAction)

            deleteSegmentAction = QAction('Delete Segment', self)
            deleteSegmentAction.triggered.connect(lambda: self.main_window.WING_MODULE.deleteSegment() if self.main_window.WING_MODULE else None)
            self.edit_menu.addAction(deleteSegmentAction)

    def _rebuild_reference_menu(self):
        self.reference_menu.clear()

        if self.current_module == 'airfoil':
            newReferenceAction = QAction('Add Reference', self)
            newReferenceAction.triggered.connect(utils_reference.add_reference)
            self.reference_menu.addAction(newReferenceAction)

            manageReferenceAction = QAction('Manage Reference', self)
            manageReferenceAction.triggered.connect(utils_reference.manage_reference)
            self.reference_menu.addAction(manageReferenceAction)

            # Ensure you are using the correct variable name here!
            project_refs = getattr(self.main_window.PROJECT, 'reference_airfoils', [])

            if project_refs:
                self.reference_menu.addSeparator()
                for reference in project_refs:
                    action = QAction(getattr(reference, 'name', 'Unknown'), self)
                    action.setCheckable(True)
                    action.setChecked(getattr(reference, 'visible', False))
                    # Route this through your controller to ensure OpenGL and Tables update!
                    action.triggered.connect(
                        lambda checked, d=reference: self.main_window.AIRFOIL_MODULE.toggleReferenceVisibility(d, checked)
                    )
                    self.reference_menu.addAction(action)

    def _rebuild_view_menu(self):
        self.view_menu.clear()
        if self.current_module == 'airfoil':
            fitViewAction = QAction('Fit view', self)
            fitViewAction.triggered.connect(lambda: self.main_window.AIRFOIL_MODULE.OPEN_GL.fit_to_airfoil() if self.main_window.AIRFOIL_MODULE else None)
            self.view_menu.addAction(fitViewAction)

            if self.main_window.PROGRAM.preferences['general']['beta_features']:
                self.showCurvCombAction = QAction('Show curvature comb', self)
                self.showCurvCombAction.setCheckable(True)
                self.showCurvCombAction.setChecked(False)
                self.showCurvCombAction.triggered.connect(utils_view.showCurvComb)
                self.view_menu.addAction(self.showCurvCombAction)

                self.showCamberlineAction = QAction('Show camberline', self)
                self.showCamberlineAction.setCheckable(True)
                self.showCamberlineAction.setChecked(False)
                self.showCamberlineAction.triggered.connect(utils_view.showCamberline)
                self.view_menu.addAction(self.showCamberlineAction)

        elif self.current_module == 'wing':
            viewXupAction = QAction('X +', self)
            viewXupAction.triggered.connect(lambda: self.main_window.WING_MODULE.OPEN_GL.position_view(90.0, 0.0) if self.main_window.WING_MODULE else None)
            self.view_menu.addAction(viewXupAction)

            viewYupAction = QAction('Y +', self)
            viewYupAction.triggered.connect(lambda: self.main_window.WING_MODULE.OPEN_GL.position_view(0, 90) if self.main_window.WING_MODULE else None)
            self.view_menu.addAction(viewYupAction)

            viewZupAction = QAction('Z +', self)
            viewZupAction.triggered.connect(lambda: self.main_window.WING_MODULE.OPEN_GL.position_view(0.0, 0.0) if self.main_window.WING_MODULE else None)
            self.view_menu.addAction(viewZupAction)

            viewXdownAction = QAction('X -', self)
            viewXdownAction.triggered.connect(lambda: self.main_window.WING_MODULE.OPEN_GL.position_view(-90.0, 0.0) if self.main_window.WING_MODULE else None)
            self.view_menu.addAction(viewXdownAction)

            viewYdownAction = QAction('Y -', self)
            viewYdownAction.triggered.connect(lambda: self.main_window.WING_MODULE.OPEN_GL.position_view(0, -90) if self.main_window.WING_MODULE else None)
            self.view_menu.addAction(viewYdownAction)

            viewZdownAction = QAction('Z -', self)
            viewZdownAction.triggered.connect(lambda: self.main_window.WING_MODULE.OPEN_GL.position_view(0.0, 180.0) if self.main_window.WING_MODULE else None)
            self.view_menu.addAction(viewZdownAction)

    def _createWindowMenu(self):
        self.loggerWidgetAction = QAction('Logger Console', self)
        self.loggerWidgetAction.setCheckable(True)
        self.loggerWidgetAction.setChecked(True)
        self.loggerWidgetAction.triggered.connect(utils_window.toggle_logger)
        self.window_menu.addAction(self.loggerWidgetAction)
        
        # Call rebuild to add dock toggles
        self._rebuild_window_menu()
    
    def _rebuild_window_menu(self):
        """Rebuild window menu with current dock widgets."""
        # Clear everything after Logger Console
        actions = self.window_menu.actions()
        if len(actions) > 1:
            for action in actions[1:]:
                self.window_menu.removeAction(action)
        
        # Add toggle actions for docks
        if self.current_module == 'airfoil' and self.main_window.AIRFOIL_MODULE.dock_widgets:
            self.window_menu.addSeparator()
            for dock_name, dock_widget in self.main_window.AIRFOIL_MODULE.dock_widgets.items():
                action = QAction(dock_name.replace('_', ' ').title(), self)
                action.setCheckable(True)
                action.setChecked(dock_widget.isVisible())
                action.triggered.connect(lambda checked, d=dock_widget: d.setVisible(checked))
                self.window_menu.addAction(action)

        if self.current_module == 'wing' and self.main_window.WING_MODULE.dock_widgets:
            self.window_menu.addSeparator()
            for dock_name, dock_widget in self.main_window.WING_MODULE.dock_widgets.items():
                action = QAction(dock_name.replace('_', ' ').title(), self)
                action.setCheckable(True)
                action.setChecked(dock_widget.isVisible())
                action.triggered.connect(lambda checked, d=dock_widget: d.setVisible(checked))
                self.window_menu.addAction(action)
        
        # Reset layout
        self.window_menu.addSeparator()
        reset_action = QAction('Reset Layout', self)
        reset_action.triggered.connect(self.main_window._reset_dock_layout)
        self.window_menu.addAction(reset_action)

    def _createModuleMenu(self):
        AirfoilModule = QAction('Airfoil Module', self)
        AirfoilModule.triggered.connect(lambda: utils_module.change_to_airfoil_module(self))
        self.module_menu.addAction(AirfoilModule)

        WingModule = QAction('Wing Module', self)
        WingModule.triggered.connect(lambda: utils_module.change_to_wing_module(self))
        self.module_menu.addAction(WingModule)

    def _createProgramMenu(self):
        manualAction = QAction('User Manual', self)
        aboutAction = QAction('About', self)
        preferencesAction = QAction('Preferences', self)

        manualAction.triggered.connect(lambda: utils_program.show_manual(self))
        aboutAction.triggered.connect(lambda: utils_program.show_about(self))
        preferencesAction.triggered.connect(lambda: utils_program.show_preferences(self))

        self.program_menu.addAction(manualAction)
        self.program_menu.addAction(aboutAction)
        self.program_menu.addSeparator()
        self.program_menu.addAction(preferencesAction)

    def set_module(self, module_name):
        self.current_module = module_name
        self.update_menu_visibility()
        self._rebuild_edit_menu()
        self._rebuild_view_menu()
        self._rebuild_window_menu()

    def update_menu_visibility(self):
        """ Call this function whenever you switch modules! """
        is_airfoil = (self.current_module == 'airfoil')
        
        # This is the magic trick to hide/show top-level menus dynamically
        self.reference_menu.menuAction().setVisible(is_airfoil)
        
        # If we just switched to the airfoil module, populate the menu items
        if is_airfoil:
            self._rebuild_reference_menu()
        