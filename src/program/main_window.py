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
from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QDockWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from src.widgets.menu_bar.menu_bar import MenuBar
from src.widgets.tool_bar import ToolBar, WingToolBar, AirfoilToolBar
from src.program.home_screen import HomeScreen
import src.widgets.menu_bar.utils.menu_file as utils_file
import src.widgets.menu_bar.utils.menu_edit as utils_edit


class MainWindow(QMainWindow):
    """Main window with dockable panels and module switching."""

    def __init__(self, program=None, project=None):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.PROGRAM = program
        self.PROJECT = project

        # Module references
        self.AIRFOIL_MODULE = None
        self.WING_MODULE = None
        self.current_module = None

        self.MENU_BAR = None
        self.BASIC_TOOL_BAR = None
        self.MODULE_TOOL_BAR = None

        # Dock widgets storage
        self.dock_widgets = {}
        self.module_docks = {'airfoil': [], 'wing': []}

        self._build_ui()

    def _build_ui(self):
        """Build the Blender-style UI."""
        self.setWindowTitle(f"{self.PROGRAM.name}")
        self.setWindowIcon(QIcon('src/assets/logo.png'))
        self.window_width, self.window_height = 1400, 900
        self.setMinimumSize(self.window_width, self.window_height)

        # Create central widget with stacked layout for modules
        self.central_stacked = QStackedWidget()
        self.setCentralWidget(self.central_stacked)

        # Create placeholder central widget with centered alignment
        home_screen = HomeScreen(program=self.PROGRAM)
        home_container = QWidget()
        home_container.setProperty("HomeContainer", "true")
        home_layout = QVBoxLayout(home_container)
        home_layout.setContentsMargins(0, 0, 0, 0)
        home_layout.addWidget(home_screen, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.central_stacked.addWidget(home_container)

        # Create menu bar
        self._create_menu_bar()

        # Create toolbar with hamburger menu
        self._create_toolbar()

    def _create_menu_bar(self):
        """Create the menu bar with module switching options."""
        self.MENU_BAR = MenuBar(main_window=self)
        self.setMenuBar(self.MENU_BAR)

    def _create_toolbar(self):
        """Create toolbar with module indicator."""
        
        self.BASIC_TOOL_BAR = ToolBar(
            program=self.PROGRAM,
            new_file_callback=lambda: utils_file.new_project(self.MENU_BAR), 
            open_file_callback=lambda: utils_file.open_project(self.MENU_BAR), 
            save_file_callback=lambda: utils_file.save_project(self.MENU_BAR), 
            edit_descr_callback=lambda: utils_file.edit_description_project(self.MENU_BAR)
            )
        self.addToolBar(self.BASIC_TOOL_BAR)
        self.BASIC_TOOL_BAR.addSeparator()

        # Store toolbar reference
        self.main_toolbar = self.BASIC_TOOL_BAR

    def _reset_dock_layout(self):
        """Reset dock layout to default positions."""
        # Hide all docks first
        for dock in self.dock_widgets.values():
            dock.hide()

        # Show current module's docks in default positions
        if self.current_module:
            self._setup_module_docks(self.current_module)

    def add_module(self, module_name, module_instance):
        """Add a module with its widgets and docks.

        Args:
            module_name: 'airfoil' or 'wing'
            module_instance: module instance with 'central_widget' and 'dock_widgets' attributes
        """
        if module_name == 'airfoil':
            self.AIRFOIL_MODULE = module_instance
            self.central_stacked.addWidget(module_instance.central_widget)
        elif module_name == 'wing':
            self.WING_MODULE = module_instance
            self.central_stacked.addWidget(module_instance.central_widget)

        # Store dock widgets
        for dock_name, dock_widget in module_instance.dock_widgets.items():
            self.dock_widgets[dock_name] = dock_widget
            self.module_docks[module_name].append(dock_name)

    def switch_to_module(self, module_name):
        """Switch to the specified module.

        Args:
            module_name: 'airfoil' or 'wing'
        """
        # Hide current module's docks
        if self.current_module:
            for dock_name in self.module_docks[self.current_module]:
                if dock_name in self.dock_widgets:
                    self.dock_widgets[dock_name].hide()

        if self.MODULE_TOOL_BAR:
            self.removeToolBar(self.MODULE_TOOL_BAR)

        # Switch central widget
        if module_name == 'airfoil' and self.AIRFOIL_MODULE:
            self.central_stacked.setCurrentWidget(self.AIRFOIL_MODULE.central_widget)
            self.current_module = 'airfoil'
            # self.module_label.setText("Airfoil Designer")
            self.setWindowTitle(f"{self.PROGRAM.name}: Airfoil Designer")
            self._setup_module_docks('airfoil')
            self.MENU_BAR.set_module('airfoil')
            # Refresh module state to show any airfoils created in other modules
            if hasattr(self.AIRFOIL_MODULE, 'set_project'):
                self.AIRFOIL_MODULE.set_project(self.PROJECT)

            self.MODULE_TOOL_BAR = AirfoilToolBar(program=self.PROGRAM,
                                                  new_airfoil_callback=self.AIRFOIL_MODULE.addAirfoil, 
                                                  append_airfoil_callback=lambda: utils_edit.append_airfoil(self.MENU_BAR), 
                                                  delete_airfoil_callback=self.AIRFOIL_MODULE.deleteAirfoil, 
                                                  flip_airfoil_callback=self.AIRFOIL_MODULE.flipAirfoil, 
                                                  save_airfoil_callback=self.AIRFOIL_MODULE.saveAirfoil)
            self.addToolBar(self.MODULE_TOOL_BAR)
            
            # Module indicator
            # self.module_label = QLabel("No Module")
            # self.module_label.setStyleSheet("font-weight: bold; padding: 0 10px;")
            # self.MODULE_TOOL_BAR.addWidget(self.module_label)

            self.MODULE_TOOL_BAR.addSeparator()

            self.logger.info("Switched to Airfoil Designer")
        elif module_name == 'wing' and self.WING_MODULE:
            self.central_stacked.setCurrentWidget(self.WING_MODULE.central_widget)
            self.current_module = 'wing'
            # self.module_label.setText("Wing Designer")
            self.setWindowTitle(f"{self.PROGRAM.name}: Wing Designer")
            self._setup_module_docks('wing')
            self.MENU_BAR.set_module('wing')
            # Refresh module state
            if hasattr(self.WING_MODULE, 'set_project'):
                self.WING_MODULE.set_project(self.PROJECT)
            
            self.MODULE_TOOL_BAR = WingToolBar(
                program=self.PROGRAM,
                add_comp_callback=self.WING_MODULE.addComponent, 
                del_comp_callback=self.WING_MODULE.deleteComponent, 
                add_wing_callback=self.WING_MODULE.addWing, 
                del_wing_callback=self.WING_MODULE.deleteWing,
                add_segm_callback=self.WING_MODULE.addSegment, 
                del_segm_callback=self.WING_MODULE.deleteSegment,
                )
            self.addToolBar(self.MODULE_TOOL_BAR)

            # Module indicator
            # self.module_label = QLabel("No Module")
            # self.module_label.setStyleSheet("font-weight: bold; padding: 0 10px;")
            # self.MODULE_TOOL_BAR.addWidget(self.module_label)

            self.MODULE_TOOL_BAR.addSeparator()

            self.logger.info("Switched to Wing Designer")

    def _setup_module_docks(self, module_name):
        """Setup dock widgets for the specified module."""
        if module_name not in self.module_docks:
            return

        # Show module-specific docks
        for dock_name in self.module_docks[module_name]:
            if dock_name in self.dock_widgets:
                dock = self.dock_widgets[dock_name]
                dock.show()

                # Set default positions based on dock name
                name_lower = dock_name.lower()
                if 'tree' in name_lower or 'object' in name_lower or 'reference' in name_lower:
                    self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
                elif 'parameters' in name_lower or 'table' in name_lower:
                    self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
                elif 'description' in name_lower or 'statistics' in name_lower:
                    self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
                elif 'log' in name_lower:
                    self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
                else:
                    # Default to left if no explicit category matches
                    self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def set_project(self, project):
        """Set the project for the current and all modules.

        Args:
            project: The project object to set
        """
        self.PROJECT = project

        if self.AIRFOIL_MODULE and hasattr(self.AIRFOIL_MODULE, 'set_project'):
            self.AIRFOIL_MODULE.set_project(project)

        if self.WING_MODULE and hasattr(self.WING_MODULE, 'set_project'):
            self.WING_MODULE.set_project(project)

    def add_dock_widget(self, name, widget, title="", area=Qt.DockWidgetArea.LeftDockWidgetArea):
        """Add a dock widget to the main window.

        Args:
            name: Unique name for the dock
            widget: The widget to put in the dock
            title: Dock title
            area: Default dock area
        """
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)

        self.dock_widgets[name] = dock
        self.addDockWidget(area, dock)

        return dock
