'''

Copyright (C) 2026 Jakub Kamyk

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

#System imports
import os
import sys
from datetime import date
import logging
import json

#PyQt5 imports
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, 
    QWidget, QLabel, QFileDialog, 
    QDockWidget, QWidget, QFileDialog, 
    QApplication, QLabel, QInputDialog
    )

#Self imports
import src.utils.dxf as dxf

from src.obj.class_airfoil import Airfoil
from src.utils.tools_program import convert_list_to_ndarray, convert_ndarray_to_list, decode_json, get_archive_version
from src.utils.tools_airfoil import Reference_load, flip_airfoil_horizontally, load_ddls_airfoil_030, load_ddls_airfoil
from src.utils.tools_reference import load_ddls_as_reference, load_xy_points_as_reference, load_ddls_030_as_reference
from src.widgets.widget_reference import WidgetReference

from src.widgets.widget_log import LogViewer
from src.widgets.tree_airfoils import TreeAirfoil
from src.widgets.table_parameters import TableParameters
from src.widgets.table_statistics import TableStatistics
from src.widgets.widget_description import WidgetDescription

from src.opengl.viewport2D.viewport2d import ViewportOpenGL


class AirfoilDesigner:
    ''' Airfoil Designer module that creates dockable widgets and central viewport. '''

    def __init__(self, parent=None, program=None, project=None):
        self.name = "Airfoil Designer"
        self.time = date.today().strftime("%Y-%m-%d")
        self.logger = logging.getLogger(self.__class__.__name__)

        self.PROGRAM = program
        self.PROJECT = project
        self.main_window = parent

        # Module components
        self.central_widget = None
        self.dock_widgets = {}
        self.menu_bar = None
        self.tool_bar = None

        self._create_module_components()

    def _create_module_components(self):
        """Create all components for this module."""
        self._create_central_widget()
        self._create_dock_widgets()
        self._create_toolbars()

    def _create_central_widget(self):
        """Create the central viewport widget."""
        # Main container
        central_container = QWidget()
        main_layout = QVBoxLayout(central_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create top toolbar
        # self.TOOL_BAR = ToolBar(program=self.PROGRAM, project=self.PROJECT, parent=central_container, 
        #                         new_callback=self.newAirfoil, append_callback=self.appendAirfoil,
        #                         delete_callback=self.deleteAirfoil, flip_callback=self.flipAirfoil,
        #                         save_callback=self.saveAirfoil)
        # main_layout.addWidget(self.TOOL_BAR)

        # Create the OpenGL viewport
        self.VIEWPORT = QWidget()
        self.OPEN_GL = ViewportOpenGL(program=self.PROGRAM, project=self.PROJECT, parent=self.VIEWPORT)
        viewport_layout = QVBoxLayout(self.VIEWPORT)
        viewport_layout.setContentsMargins(0, 0, 0, 0)
        viewport_layout.addWidget(self.OPEN_GL)
        main_layout.addWidget(self.VIEWPORT)

        self.central_widget = central_container

    def _create_dock_widgets(self):
        """Create all dockable widgets for this module."""
        # Left side tree airfoil
        self.TREE_AIRFOIL = TreeAirfoil(program=self.PROGRAM, project=self.PROJECT, parent=None, airfoil_designer=self)
        dock_airfoil = QDockWidget("Airfoil Tree", None)
        dock_airfoil.setWidget(self.TREE_AIRFOIL)
        dock_airfoil.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_airfoil.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['airfoil_tree'] = dock_airfoil

        # Left side tree reference
        self.WIDGET_REFERENCE = WidgetReference(program=self.PROGRAM, project=self.PROJECT, parent=None, airfoil_designer=self)
        dock_reference = QDockWidget("Reference Table", None)
        dock_reference.setWidget(self.WIDGET_REFERENCE)
        dock_reference.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_reference.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['airfoil_reference_table'] = dock_reference

        # Left side parameters table
        self.TABLE_PARAMETERS = TableParameters(program=self.PROGRAM, project=self.PROJECT, parent=self, tree_menu=self.TREE_AIRFOIL, open_gl=self.OPEN_GL, element_type='airfoil')
        dock_parameters = QDockWidget("Parameters Table", None)
        dock_parameters.setWidget(self.TABLE_PARAMETERS)
        dock_parameters.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_parameters.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['airfoil_parameters_table'] = dock_parameters

        # Right side description textarea
        self.TEXT_DESCRIPTION = WidgetDescription(parent=None, program=self.PROGRAM, project=self.PROJECT)
        self.TEXT_DESCRIPTION.set_description()
        dock_description = QDockWidget("Description", None)
        dock_description.setWidget(self.TEXT_DESCRIPTION)
        dock_description.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_description.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['airfoil_description_text'] = dock_description

        # Right side statistics table
        self.TABLE_STATISTICS = TableStatistics(program=self.PROGRAM, project=self.PROJECT, parent=self, tree_menu=self.TREE_AIRFOIL, open_gl=self.OPEN_GL, element_type='airfoil')
        dock_statistics = QDockWidget("Statistics Table", None)
        dock_statistics.setWidget(self.TABLE_STATISTICS)
        dock_statistics.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_statistics.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['airfoil_statistics_table'] = dock_statistics

        # Log Viewer Widget
        self.LOG_VIEWER = LogViewer(log_file="toolout.log", parent=None, program=self.PROGRAM)
        dock_logger = QDockWidget("Logger Console", None)
        dock_logger.setWidget(self.LOG_VIEWER)
        dock_logger.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_logger.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['airfoil_logger_console'] = dock_logger

        # Connect signals
        self.TREE_AIRFOIL.selectedAirfoilChanged.connect(self.TABLE_PARAMETERS.display_selected_element)
        self.TREE_AIRFOIL.selectedAirfoilChanged.connect(self.TABLE_STATISTICS.display_selected_element)
        self.TABLE_PARAMETERS.parametersChanged.connect(self.TABLE_STATISTICS.update)
        # self.TABLE_PARAMETERS.parametersChanged.connect(self.TREE_AIRFOIL.update)

        # Initialize with default airfoil if no project airfoils
        if self.PROJECT and not self.PROJECT.airfoils:
            self.addAirfoil()

    def _create_toolbars(self):
        """Create toolbars for this module."""
        pass

    def handleReferenceToggle(self, state, filename):
        """Handle reference airfoil toggle."""
        selected_item = self.TREE_AIRFOIL.currentItem()
        if not selected_item:
            return

        airfoil_index = self.TREE_AIRFOIL.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return

        if state:
            reference_airfoil = Reference_load(filename)
            if reference_airfoil != None:
                self.logger.info(f"Reference enabled with file: '{filename}'")
                self.OPEN_GL.set_reference_to_display(reference_airfoil)
            else:
                self.logger.error('Failed to load reference!')
        else:
            self.logger.info("Reference disabled")
            self.OPEN_GL.set_reference_to_display(None)

    def set_project(self, project):
        """Set the project for this module."""
        self.PROJECT = project

        # Update all components with new project
        self.OPEN_GL.PROJECT = self.OPEN_GL.project = self.PROJECT
        # self.TOOL_BAR.PROJECT = self.TOOL_BAR.project = self.PROJECT
        self.TREE_AIRFOIL.PROJECT = self.TREE_AIRFOIL.project = self.PROJECT
        self.WIDGET_REFERENCE.PROJECT = self.WIDGET_REFERENCE.project = self.PROJECT
        self.TABLE_PARAMETERS.PROJECT = self.TABLE_PARAMETERS.project = self.PROJECT
        self.TEXT_DESCRIPTION.PROJECT = self.TEXT_DESCRIPTION.project = self.PROJECT
        self.TABLE_STATISTICS.PROJECT = self.TABLE_STATISTICS.project = self.PROJECT
        # self.MENU_BAR.PROJECT = self.MENU_BAR.project = self.PROJECT

        if not self.PROJECT.airfoils:
            self.addAirfoil()
        
        # Refresh UI to show all airfoils (including those created in other modules)
        self.refresh() ## 17.07.2026 I don't think I need it here with current code

    def refresh(self):
        """Refresh all module components."""
        self.TREE_AIRFOIL.update()
        self.WIDGET_REFERENCE.update()
        self.TABLE_PARAMETERS.update()
        self.TABLE_STATISTICS.update()
        self.TEXT_DESCRIPTION.set_description()
        self.OPEN_GL.clear()

    #===================================================#
    #              AIRFOIL DESIGNER ACTIONS             #    
    #                      AIRFOIL                      #
    # Module action methods (called from menu/toolbars) #
    #===================================================#

    def addAirfoil(self):
        """ Creates new airfoil out of initial parameters"""
        if self.PROJECT is None:
            self.logger.error("Cannot add airfoil: PROJECT is not set")
            return
        
        self.logger.info("Creating new airfoil...")

        airfoil_obj = Airfoil(self.PROGRAM)
        airfoil_obj.name = "Airfoil"  # Ensure the name is set
        airfoil_obj.info['creation_date'] = self.time
        airfoil_obj.info['modification_date'] = self.time

        self.PROJECT._ensure_unique_airfoil_name(airfoil_obj)

        self.PROJECT.airfoils.append(airfoil_obj)
        self.TREE_AIRFOIL.add_to_tree(airfoil_obj)

    def appendAirfoil(self, filePath):
        """load the airfoil data from a JSON format file."""
        from  src.obj.class_airfoil import Airfoil
        
        if not filePath:
            self.logger.error("File path not specified or incorrect!")
            return

        self.logger.info(f"Open archive airfoil: {filePath}")
        data = decode_json(filePath)
        file_version = get_archive_version(data)

        # Check compatibility
        self.logger.debug("Checking compatibility...")
        program_version = self.PROGRAM.version
        program_version = program_version.split("-")[0].split(".")

        if int(file_version[0]) == 0 and int(file_version[1]) < 4:
            self.logger.warning("There were critical changes to airfoil definition. Program will try to recreate saved airfoil to latest format. Checing the appending results is advised!")
            # Load airfoils from in-memory JSON
            self.logger.info("Loading airfoil using legacy approach...")
            arf_obj = load_ddls_airfoil_030(data, self.PROGRAM, filePath)

        else:
            self.logger.info("Loading airfoil...")
            
            try:
                project_data = data["Project"]
                airfoil_entries = project_data.get("airfoils", [])
                print(airfoil_entries)
                for airfoil_entry in airfoil_entries:
                    airfoil_data = airfoil_entry["data"]
                    self.logger.debug("Loading airfoil using 0.4.X version importer...")
                    arf_obj = load_ddls_airfoil(Airfoil(self.PROGRAM), airfoil_data)
            except KeyError as e:
                self.logger.error(f"Missing key in ARF data - {e}")
                self.logger.warning("File may not load properly or is not compatible with DAEDALUS")
                return
            
        if arf_obj:
            self.logger.debug(f"Found airfoil: {arf_obj.name}")
            self.PROJECT._ensure_unique_airfoil_name(arf_obj)  # Ensure unique name
            self.PROJECT.airfoils.append(arf_obj)
            arf_obj.update()
            self.TREE_AIRFOIL.add_to_tree(arf_obj)
            self.logger.info("Appending '{arf_obj.name}' airfoil was sucessful!")

    def deleteAirfoil(self):
        self.logger.info("Deleting selected airfoil...")
        if self.TREE_AIRFOIL:

            if self.TREE_AIRFOIL.selected_airfoil is None:
                self.logger.error('No valid airfoil selected!')
                return
            
            name = self.TREE_AIRFOIL.selected_airfoil.name
            
            try:
                self.PROJECT.airfoils.remove(self.TREE_AIRFOIL.selected_airfoil) # Remove from project airfoils
                self.TREE_AIRFOIL.remove_from_tree(name)

                self.logger.info(f"Deleted airfoil: {name}")
            except Exception as e:
                self.logger.error(f"Failed to delete! {e}")

            # Clear only the last airfoil from viewport instead of all
            if hasattr(self.OPEN_GL, 'set_display'):
                self.OPEN_GL.set_display(None)
                self.OPEN_GL.clear()
            
                self.logger.info(f"Successfully deleted airfoil: {name}")
                self.refresh()  

    def saveAirfoil(self, airfoil, filePath):
        """Save the airfoil data to a JSON format file."""
        
        airfoil.name = os.path.basename(filePath).split('.')[0]
        airfoil.path = filePath
        airfoil_data = self.PROJECT._serialize_airfoil_to_json(filePath, airfoil)

        Daedalus = {
            "program name": self.PROGRAM.name,
            "program version": self.PROGRAM.version,
        }

        Project = {
            "name": self.PROJECT.name if self.PROJECT.name else "Not assigned",
            "path": filePath,
            "creation date": self.PROJECT.creation_date,
            "modification date": self.PROJECT.modification_date,
            "description": self.PROJECT.description,
            "airfoils": airfoil_data
        }

        data = {
            "Program": Daedalus,
            "Project": Project
        }

        # Convert numpy arrays to lists before saving
        data = convert_ndarray_to_list(data)

        json_object = json.dumps(data, indent=1)

        with open(f"{filePath}", "w") as outfile:
            outfile.write(json_object)
            self.logger.info(f"Saved airfoil: {filePath}")

        self.PROJECT._ensure_unique_airfoil_name(airfoil)
        self.refresh()

    def exportAirfoil(self, airfoil, filePath):
        """Export the airfoil data to a DXF format file."""
        self.logger.info("Exporting selected airfoil...")

        dxf.export_airfoil_to_dxf(airfoil, filePath)
        self.logger.info(f"Exported file: {filePath}")

    def renameAirfoil(self):
        """Rename currently selected airfoil."""
        self.logger.info("Renaming selected airfoil...")
        self.le = QLabel()

        try:
            selected_airfoil = self.TREE_AIRFOIL.selected_airfoil

            text, ok = QInputDialog.getText(None, 'Change Airfoils Name', 'Enter airfoil\'s new name:', text=selected_airfoil.name)
            if ok:
                self.le.setText(str(text))
            if text:
                selected_airfoil.name = text
                self.PROJECT._ensure_unique_airfoil_name(selected_airfoil)
                selected_airfoil.name = selected_airfoil.name
                selected_airfoil.info['modification_date'] = date.today().strftime("%Y-%m-%d")

            self.refresh()
            self.logger.info("Airfoil renamed")

        except Exception as e:
            self.logger.error(f"Could not rename airfoil: {e}")

    def flipAirfoil(self):
        """Flip the currently selected airfoil."""

        airfoil_idx = self.TREE_AIRFOIL.selected_airfoil_index

        current_airfoil = self.PROJECT.airfoils[airfoil_idx]

        flipped_airfoil = flip_airfoil_horizontally(current_airfoil)

        if flipped_airfoil:
            self.PROJECT.airfoils[airfoil_idx] = flipped_airfoil
            self.logger.info(f"Airfoil '{flipped_airfoil.name}' flipped...")
            self.OPEN_GL.set_airfoil_to_display(self.PROJECT.airfoils[airfoil_idx])
            self.OPEN_GL.update()
            self.TABLE_PARAMETERS.update()
            self.TABLE_STATISTICS.update()
        else:
            self.logger.error("Something went wrong, airfoil not flipped!")

    #==================================================#
    #              AIRFOIL DESIGNER ACTIONS            #    
    #                     REFERENCE                    #
    #==================================================#

    def addReference(self, filePath):
        """ Appends the reference airfoil from a given filename """
        reference = None

        if not filePath:
            self.logger.error("File path not specified or incorrect!")
            return

        if filePath.endswith(".arf.ddls"):
            try:
                data = decode_json(filePath)
                file_version = get_archive_version(data)
        
                # Check compatibility
                self.logger.debug("Checking compatibility...")
                program_version = self.PROGRAM.version.split("-")[0].split(".")
        
                if int(file_version[0]) == 0 and int(file_version[1]) < 4:
                    self.logger.warning("There were critical changes to airfoil definition. Program will try to recreate saved airfoil to latest format. Checing the appending results is advised!")
                    # Load airfoils from in-memory JSON
                    self.logger.info("Loading airfoil using legacy approach...")
                    reference = load_ddls_030_as_reference(data, self.PROGRAM, filePath)
                else:
                    project_data = data["Project"]
                    airfoil_data = project_data.get("airfoils", [])

                    reference = load_ddls_as_reference(airfoil_data, self.PROGRAM, filePath)

            except Exception as e:
                self.logger.error(f"Failed to load an airfoil: {e}")
                return

        elif filePath.endswith(".arf"):
            try:
                data = decode_json(filePath)
        
                reference = load_ddls_030_as_reference(data, self.PROGRAM, filePath)
            
            except Exception as e:
                self.logger.error(f"Failed to load an airfoil: {e}")
                return

        else:
            try:
                reference = load_xy_points_as_reference(filePath)
            except Exception as e:
                self.logger.error(f"Failed to load an airfoil: {e}")
                return

        if reference:
            self.PROJECT.reference_airfoils.append(reference)
            self.logger.info(f"Loaded reference airfoil from file: '{filePath}'")

            if hasattr(self, 'WIDGET_REFERENCE'):
                self.WIDGET_REFERENCE.refresh_table()
            self.OPEN_GL.update()
            self.main_window.MENU_BAR._rebuild_reference_menu()
            
    
    def deleteReference(self, airfoils_to_remove):
        """ Deletes a list of reference airfoil objects """
        for ref in airfoils_to_remove:
            if ref in self.PROJECT.reference_airfoils:
                self.PROJECT.reference_airfoils.remove(ref)
                self.logger.info(f"Deleted reference: {getattr(ref, 'name', 'Unknown')}")
                
        if hasattr(self, 'WIDGET_REFERENCE'):
            self.WIDGET_REFERENCE.refresh_table()
        self.OPEN_GL.update()
        self.main_window.MENU_BAR._rebuild_reference_menu()

    def toggleReferenceVisibility(self, airfoil_obj, is_visible):
        """ Updates the visibility of a specific reference airfoil """
        airfoil_obj.visible = is_visible

        self.main_window.MENU_BAR._rebuild_reference_menu()
        if hasattr(self, 'WIDGET_REFERENCE'):
            self.WIDGET_REFERENCE.refresh_table()
        self.OPEN_GL.update()
    
    def editReference():
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = AirfoilDesigner()
    viewer.show()
    sys.exit(app.exec_())
