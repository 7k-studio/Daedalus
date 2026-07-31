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
import logging

from PyQt6.QtCore import Qt


import src.obj.class_component
import src.obj.class_wing
import src.obj.class_segment


from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QDockWidget
)

from src.opengl.viewport3D.viewport3d import Viewport3D

from src.widgets.widget_log import LogViewer
from src.widgets.tree_objects import TreeObject
from src.widgets.table_parameters import TableParameters
from src.widgets.table_statistics import TableStatistics
from src.widgets.widget_description import WidgetDescription

from datetime import date

class WingDesigner:
    ''' Wing Designer module that creates dockable widgets and central viewport. '''

    def __init__(self, parent=None, program=None, project=None):
        self.name = "Wing Designer"
        self.logger = logging.getLogger(self.__class__.__name__)

        self.DAEDALUS = program
        self.PROJECT = project
        self.main_window = parent

        # Module components
        self.central_widget = None
        self.dock_widgets = {}
        self.menu_bar = None

        self._create_module_components()
    
    def _create_module_components(self):
        """Create all components for this module."""
        self._create_central_widget()
        self._create_dock_widgets()

    def _create_central_widget(self):
        """Create the central viewport widget."""
        # Main container
        central_container = QWidget()
        main_layout = QVBoxLayout(central_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create the OpenGL viewport
        self.VIEWPORT = QWidget()
        self.OPEN_GL = Viewport3D(program=self.DAEDALUS, parent=self.VIEWPORT, project=self.PROJECT)
        viewport_layout = QVBoxLayout(self.VIEWPORT)
        viewport_layout.setContentsMargins(0, 0, 0, 0)
        viewport_layout.addWidget(self.OPEN_GL)
        main_layout.addWidget(self.VIEWPORT)

        self.central_widget = central_container

    def _create_dock_widgets(self):
        """Create all dockable widgets for this module."""
        # Left side tree object
        self.TREE_OBJECT = TreeObject(program=self.DAEDALUS, project=self.PROJECT, parent=None, wing_designer=self)
        dock_tree = QDockWidget("Object Tree", None)
        dock_tree.setWidget(self.TREE_OBJECT)
        dock_tree.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_tree.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['wing_object_tree'] = dock_tree

        # Right side parameters table
        self.TABLE_PARAMETERS = TableParameters(program=self.DAEDALUS, project=self.PROJECT, tree_menu=self.TREE_OBJECT, open_gl=self.OPEN_GL)
        dock_parameters = QDockWidget("Parameters Table", None)
        dock_parameters.setWidget(self.TABLE_PARAMETERS)
        dock_parameters.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_parameters.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['wing_parameters_table'] = dock_parameters

        # Right side description textarea
        self.TEXT_DESCRIPTION = WidgetDescription(parent=None, program=self.DAEDALUS, project=self.PROJECT)
        self.TEXT_DESCRIPTION.set_description()
        dock_description = QDockWidget("Description", None)
        dock_description.setWidget(self.TEXT_DESCRIPTION)
        dock_description.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_description.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['wing_description_text'] = dock_description

        # Right side statistics table
        self.TABLE_STATISTICS = TableStatistics(program=self.DAEDALUS, project=self.PROJECT, parent=self, tree_menu=self.TREE_OBJECT, open_gl=self.OPEN_GL, element_type='wing')
        dock_statistics = QDockWidget("Statistics Table", None)
        dock_statistics.setWidget(self.TABLE_STATISTICS)
        dock_statistics.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_statistics.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['wing_statistics_table'] = dock_statistics

        # Log Viewer Widget
        self.LOG_VIEWER = LogViewer(log_file="toolout.log", parent=None, program=self.DAEDALUS)
        dock_logger = QDockWidget("Logger Console", None)
        dock_logger.setWidget(self.LOG_VIEWER)
        dock_logger.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock_logger.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_widgets['wing_logger_console'] = dock_logger

        # Connect signals
        self.TREE_OBJECT.selectedObjectChanged.connect(self.TABLE_PARAMETERS.display_selected_element)
        self.TREE_OBJECT.selectedObjectChanged.connect(self.TABLE_STATISTICS.display_selected_element)


        # Initialize with default component if no project components (moved to _populate_ui)
        # if self.PROJECT and not self.PROJECT.components:
        #     self.addComponent()

    def _update_header(self):
        """Update window title (handled by main window now)."""
        pass

    def _populate_ui(self):
        """Populate the UI with project data."""
        # assign into both styles if code expects either attribute
        self.OPEN_GL.PROJECT = self.OPEN_GL.project = self.PROJECT
        self.TREE_OBJECT.PROJECT = self.TREE_OBJECT.project = self.PROJECT
        self.TABLE_PARAMETERS.PROJECT = self.TABLE_PARAMETERS.project = self.PROJECT
        # self.MENU_BAR.PROJECT = self.MENU_BAR.project = self.PROJECT

        if self.TREE_OBJECT:
            self.TREE_OBJECT.update()

        if not self.PROJECT:
            return

        if not self.PROJECT.components:
            # Initialize with a default component
            self.addComponent()

    def update_menu_bar_state(self, *args):
        """Update menu bar state (not used in single-window mode)."""
        pass

    def set_project(self, project):
        self.PROJECT = project

        if not self.PROJECT:
            return

        self._populate_ui()
        self.refresh()

    def refresh(self):
        self.TREE_OBJECT.update()
        self.TEXT_DESCRIPTION.set_description()
    
    def addComponent(self):
        """Add a new component to the tree menu."""
        component_obj = src.obj.class_component.Component(self.DAEDALUS, self.PROJECT)
        component_obj.name = 'Component'
        self.PROJECT._ensure_unique_object_name(component_obj)
        component_obj.info['creation_date'] = date.today().strftime("%Y-%m-%d")
        component_obj.info['modification_date'] = date.today().strftime("%Y-%m-%d")
        self.PROJECT.components.append(component_obj)
        self.TREE_OBJECT.add_component_to_tree(component_obj)
        self.OPEN_GL.update()

    def addWing(self):
        """Add a new wing to the selected component."""
        selected_item = self.TREE_OBJECT.currentItem()
        if selected_item:
            # Find the index of the selected item
            index = self.TREE_OBJECT.indexOfTopLevelItem(selected_item)
            if index != -1:
                # Add the wing as a child of the selected component
                component_obj = self.PROJECT.components[index]

                wing_obj = src.obj.class_wing.Wing(self.DAEDALUS, self.PROJECT, component_obj)
                wing_obj.name = 'Wing'
                self.PROJECT._ensure_unique_object_name(wing_obj)
                wing_obj.info['creation_date'] = date.today().strftime("%Y-%m-%d")
                wing_obj.info['modification_date'] = date.today().strftime("%Y-%m-%d")

                component_obj.wings.append(wing_obj)

                self.TREE_OBJECT.add_wing_to_tree(wing_obj)
                self.OPEN_GL.update()
                self.logger.info(f"Added '{wing_obj.name}' as a part of '{component_obj.name}'.")
            else:
                self.logger.error("Cannot set wing to selected item!")
        else:
            self.logger.error("Component NOT selected!")

    def addSegment(self):
        """Add a new Segment to the selected wing."""
        selected_item = self.TREE_OBJECT.currentItem()
        if not selected_item:
            self.logger.error("Component/Wing NOT selected!")
            return

        parent_item = selected_item.parent()
        if not parent_item:
            self.logger.error("Wing NOT selected!")
            return

        wing_index = parent_item.indexOfChild(selected_item)
        component_index = self.TREE_OBJECT.indexOfTopLevelItem(parent_item)

        if wing_index == -1 or component_index == -1:
            self.logger.error("Cannot set segment to selected item!")
            return

        target_wing = self.PROJECT.components[component_index].wings[wing_index]
        segment_index = selected_item.childCount()

        airfoil_obj = src.obj.class_airfoil.Airfoil(self.DAEDALUS, self.PROJECT)
        airfoil_obj.name = "Airfoil"
        self.PROJECT._ensure_unique_airfoil_name(airfoil_obj)
        airfoil_obj.info['creation_date'] = date.today().strftime("%Y-%m-%d")
        airfoil_obj.info['modification_date'] = date.today().strftime("%Y-%m-%d")
        airfoil_obj.update()
        self.PROJECT.airfoils.append(airfoil_obj)
        
        segment_obj = src.obj.class_segment.Segment(self.DAEDALUS, self.PROJECT)
        segment_obj.name = "Segment"
        self.PROJECT._ensure_unique_object_name(segment_obj)
        segment_obj.info['creation_date'] = date.today().strftime("%Y-%m-%d")
        segment_obj.info['modification_date'] = date.today().strftime("%Y-%m-%d")

        segment_obj.attrs['airfoil'].value = self.PROJECT.airfoils[-1]

        if segment_index > 0:
            prev_seg = target_wing.segments[segment_index - 1]
            segment_obj.params['position_X'].value = prev_seg.params['position_X'].value
            segment_obj.params['position_Y'].value = prev_seg.params['position_Y'].value
            segment_obj.params['span'].value = prev_seg.params['span'].value + 0.2
        else:
            segment_obj.params['span'].value = 0.0

        segment_obj.parent = target_wing
        target_wing.segments.append(segment_obj)
    
                    
        segment_obj.update()
        if segment_index > 0:
            target_wing.update()

        self.TREE_OBJECT.add_segment_to_tree(segment_obj)
        self.OPEN_GL.update()
    
    def deleteComponent(self):
        """Delete the selected component."""
        selected_item = self.TREE_OBJECT.currentItem()
        if selected_item:
            index = self.TREE_OBJECT.indexOfTopLevelItem(selected_item)
            if index != -1:
                self.TREE_OBJECT.takeTopLevelItem(index)
                del self.PROJECT.components[index]
                self.logger.info(f"Deleted component at index {index}.")
                self.TREE_OBJECT.update()
                self.OPEN_GL.update()
            else:
                self.logger.error("Invalid selection.")
        else:
            self.logger.error("Component NOT selected!")

    def deleteWing(self):
        """Delete the selected wing."""
        selected_item = self.TREE_OBJECT.currentItem()
        if selected_item:
            parent_item = selected_item.parent()
            if parent_item:
                wing_index = parent_item.indexOfChild(selected_item)
                component_index = self.TREE_OBJECT.indexOfTopLevelItem(parent_item)
                if wing_index != -1 and component_index != -1:
                    del self.PROJECT.components[component_index].wings[wing_index]
                    self.logger.info(f"Deleted wing at index {component_index}:{wing_index}.")
                    self.TREE_OBJECT.update()
                    self.OPEN_GL.update()
                else:
                    self.logger.error("Cannot delete selected wing!")
            else:
                self.logger.error("Wing NOT selected!")
        else:
            self.logger.error("Component NOT found!")

    def deleteSegment(self):
        """Delete the selected segment."""
        selected_item = self.TREE_OBJECT.currentItem()
        if selected_item:
            parent_item = selected_item.parent()
            if parent_item:
                grandparent_item = parent_item.parent()
                great_grandparent_item = grandparent_item.parent()
                if grandparent_item and not great_grandparent_item:
                    segment_index = parent_item.indexOfChild(selected_item)
                    wing_index = grandparent_item.indexOfChild(parent_item)
                    component_index = self.TREE_OBJECT.indexOfTopLevelItem(grandparent_item)
                    del self.PROJECT.components[component_index].wings[wing_index].segments[segment_index]
                    self.logger.info(f"Deleted segment at index {component_index}:{wing_index}:{segment_index}.")
                    self.TREE_OBJECT.update()
                    self.OPEN_GL.update()
                else:
                    self.logger.error("Cannot delete selected segment!")
            else:
                self.logger.error("Segment NOT selected!")
        else:
            self.logger.error("Component NOT found!")
    
    def toggle_logger(self):
        """Toggle the logger widget."""
        dock_logger = self.dock_widgets.get('logger_console')
        if dock_logger:
            if dock_logger.isVisible():
                dock_logger.close()  # Close the dock widget
            else:
                dock_logger.show()  # Show the dock widget
            
    def update_menu_bar_state(self, dock_widget):
        """Update the menu bar state when a dock widget's visibility changes."""
        if dock_widget == self.dock_widgets.get('logger_console'):
            self.MENU_BAR.update_action_state(self.MENU_BAR.loggerWidgetAction, dock_widget)

