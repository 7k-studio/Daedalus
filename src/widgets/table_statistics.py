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
    QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal

class TableStatistics(QTableWidget):
    referenceStatus = pyqtSignal(bool, str)

    def __init__(self, program=None, project=None, parent=None, tree_menu=None, open_gl=None, element_type='generic'):
        super(TableStatistics, self).__init__(None)
        self.setMinimumSize(200, 200)

        self.logger = logging.getLogger(self.__class__.__name__)

        self.DAEDALUS = program
        self.PROJECT = project
        self.MODULE = parent
        self.open_gl = open_gl
        self.tree_menu = tree_menu
        self.element_type = element_type  # 'generic', 'airfoil', 'wing', 'segment', 'component'

        # Track the currently selected element
        self.current_element = None

        self.init_tabele()

    def init_tabele(self, stats=None):
        # Initial Parameters
        self.stats = {}

        # Properly initialize the table without overwriting `self`
        self.setRowCount(len(self.stats))
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Statistic", "Value", "Nominal", "Unit"])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        #self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setColumnWidth(0, 100) # Set width of the first column
        self.setColumnWidth(1, 100)  # Set width of the second column
        self.setColumnWidth(2, 70)  # Set width of the third column
        self.setColumnWidth(3, 50)  # Set width of the forth column

    def update(self):
        self.populate_table(self.current_element)

    def populate_table(self, element_obj=None):
        """Populate the table with data from an airfoil object."""
        
        if not element_obj:
            self.logger.warning("No object provided to populate_table")
            return

        self.logger.debug(f"Populating table with object: {element_obj}")
        self.logger.debug(f"Object statistics: {getattr(element_obj, 'stats', None)}")
        
        self.setRowCount(0)  # Clear existing rows

        # Default: show all stats of element
        if hasattr(element_obj, 'stats'):
            # Stats rows
            for key, stat_obj in element_obj.stats.items():
                row = self.rowCount()
                self.insertRow(row)
                self.setItem(row, 0, QTableWidgetItem(key))
                # Pass the Param object to add_editable_row
                if hasattr(stat_obj, 'get'):
                    value = stat_obj.get()
                    nominal_text = stat_obj.nominal
                    unit_text = stat_obj.unit.name if hasattr(stat_obj, 'unit') else ''
                else:
                    # Fallback for plain values
                    value = stat_obj
                    unit_text = 'm'  # Default to meters
                    nominal_text = 'N/A'

                value = format(value, '.4f')

                airfoil_value = QTableWidgetItem(str(value))
                airfoil_value.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, 1, airfoil_value)

                nominal_value = QTableWidgetItem(str(nominal_text))
                nominal_value.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, 2, nominal_value)
                
                unit_value = QTableWidgetItem(str(unit_text))
                unit_value.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, 3, unit_value)

    def display_selected_element(self, item, column=None):
        """Display the selected elements's data in the table.
        Supports both wing design elements (segments/wings) and airfoil components (LE/TE/PS/SS).
        Accepts (item, column) from QTreeWidget.itemClicked. If a child node was clicked,
        show parameters for the corresponding component (LE/TE/PS/SS).
        """
        if not self.tree_menu:
            self.logger.warning("No tree_menu assigned to TableStatistics")
            return

        if not item:
            self.logger.warning("No item selected in TreeAirfoil")
            return
        
        self.logger.debug(f"TableStatistics got: {item.text(0)}, {self.element_type}, {self.tree_menu}")
        
        # Handle airfoil components if element_type is 'airfoil'
        if self.element_type == 'airfoil':
            self._display_airfoil_element(item)
        else:
            # Handle wing/segment elements
            self._display_wing_element()

    def _display_airfoil_element(self, item):
        """Display airfoil or its components (LE/TE/PS/SS)."""

        selected_item = item if item is not None else self.tree_menu.currentItem()
        
        if not selected_item:
            return
    
        # Detect if a child node was clicked
        component_attr = None
        if selected_item.parent():
            # child clicked -> map its label to component attribute
            # child_label = selected_item.text(0).strip().lower()
            # mapping = {
            #     "leading edge": "LE", "leading_edge": "LE", "leadingedge": "LE", "le": "LE",
            #     "trailing edge": "TE", "trailing_edge": "TE", "trailingedge": "TE", "te": "TE",
            #     "pressure side": "PS", "pressure_side": "PS", "pressureside": "PS", "ps": "PS",
            #     "suction side": "SS", "suction_side": "SS", "suctionside": "SS", "ss": "SS",
            # }
            # component_attr = mapping.get(child_label)

            top_item = selected_item.parent()
        else:
            top_item = selected_item

        # Get the index of the top-level item (the Airfoil)
        item_index = self.tree_menu.indexOfTopLevelItem(top_item)
        if item_index == -1:
            self.logger.debug("Top-level item index not found for selected item")
            return
            
        selected_airfoil = self.PROJECT.airfoils[item_index]
        self.populate_table(selected_airfoil)
        self.current_element = selected_airfoil

        # Update self.stats
        self.stats = {key: value for key, value in vars(selected_airfoil).items() if key != "info"}
        self.logger.debug('Displayed parent airfoil statistics')
        # if component_attr:

        #     selected_component = getattr(selected_airfoil, component_attr, None)
        #     if selected_component:
        #         self.populate_table(selected_component)
        #         self.current_element = selected_component
        #         self.stats = {key: value for key, value in vars(selected_component).items()}
        #         self.logger.debug(f"Displayed component '{component_attr}' statistics")
        #     else:
        #         self.logger.warning(f"Component '{component_attr}' not found on selected airfoil")
        # else:
        #     # Top-level airfoil selected -> show overall stats
        #     self.populate_table(selected_airfoil)
        #     self.current_element = selected_airfoil
        #     self.stats = {key: value for key, value in vars(selected_airfoil).items() if key != "info"}
        #     self.logger.debug('Displayed parent airfoil statistcs')
            

    def _display_wing_element(self):
        selected_item = self.tree_menu.currentItem()
        
        if not selected_item:
            return

        parent_item = selected_item.parent()
        grandparent_item = parent_item.parent() if parent_item else None
        great_grandparent_item = grandparent_item.parent() if grandparent_item else None

        # ----- LEVEL 4: AIRFOIL (Inside a Segment) -----
        if great_grandparent_item:
            item_index = grandparent_item.indexOfChild(parent_item) # Segment index
            parent_index = great_grandparent_item.indexOfChild(grandparent_item) # Wing index
            grandparent_index = self.tree_menu.indexOfTopLevelItem(great_grandparent_item) # Component index

            self.logger.debug(f'Airfoil inside Segment at index: {grandparent_index}:{parent_index}:{item_index}')

            # Fetch the Segment, then get its linked master Airfoil object
            segment_item = self.PROJECT.components[grandparent_index].wings[parent_index].segments[item_index]
            element_item = segment_item.attrs['airfoil'].value

            self.current_element = element_item
            self.populate_table(element_item)
            self.stats = {key: value for key, value in vars(element_item).items() if key != "info"}
        
        # ----- LEVEL 3: SEGMENT -----
        elif parent_item and grandparent_item:
            item_index = parent_item.indexOfChild(selected_item)
            parent_index = grandparent_item.indexOfChild(parent_item)
            grandparent_index = self.tree_menu.indexOfTopLevelItem(grandparent_item)

            self.logger.debug(f'Segment at index: {grandparent_index}:{parent_index}:{item_index}')

            element_item = self.PROJECT.components[grandparent_index].wings[parent_index].segments[item_index]

            self.current_element = element_item
            self.populate_table(element_item)
            self.stats = {key: value for key, value in vars(element_item).items() if key != "info"}

        # ----- LEVEL 2: WING -----
        elif parent_item and not grandparent_item:
            item_index = parent_item.indexOfChild(selected_item)
            parent_index = self.tree_menu.indexOfTopLevelItem(parent_item)
            
            self.logger.debug(f'Wing at index: {parent_index}:{item_index}')
            
            element_item = self.PROJECT.components[parent_index].wings[item_index]
            self.current_element = element_item
            self.populate_table(element_item)
            self.stats = {key: value for key, value in vars(element_item).items() if key != "info"}

        # ----- LEVEL 1: COMPONENT -----
        elif not parent_item and not grandparent_item:
            item_index = self.tree_menu.indexOfTopLevelItem(selected_item)
            
            self.logger.debug(f'Component at index: {item_index}')
            
            element_item = self.PROJECT.components[item_index]
            self.current_element = element_item
            self.populate_table(element_item)
            self.stats = {key: value for key, value in vars(element_item).items() if key != "info"}