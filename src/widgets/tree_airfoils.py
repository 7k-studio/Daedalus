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
#System imports
import logging

#PyQt6 imports
from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem 
    )
from PyQt6.QtCore import Qt, pyqtSignal


class TreeAirfoil(QTreeWidget):
    referenceStatus = pyqtSignal(bool, str)
    selectedAirfoilChanged = pyqtSignal(object, int)

    def __init__(self, program=None, project=None, parent=None, open_gl=None, airfoil_designer=None):
        super(TreeAirfoil, self).__init__(parent)
        self.setMinimumSize(200, 200)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.DAEDALUS = program
        self.PROJECT = project
        self.main_window = parent
        self.AIRFOILDESIGNER = airfoil_designer

        self.selected = None
        self.selected_airfoil = None

        # Connect selection events only once
        self.itemClicked.connect(self.on_select)
        self.update()

    def on_select(self, item, column):
        
        if not item:
            # Determine if a child node was clicked
            item = self.currentItem()

        # Handle item click events
        try:
            self.logger.debug(f"Clicked on: {item.text(0)}")
        except Exception:
            self.logger.debug("Clicked on tree item")

        if item:
            component_attr = None
            if item.parent():
                # child clicked -> map its label to component attribute
                child_label = item.text(0).strip().lower()
                mapping = {
                    "leading edge": "LE", "leading_edge": "LE", "leadingedge": "LE", "le": "LE",
                    "trailing edge": "TE", "trailing_edge": "TE", "trailingedge": "TE", "te": "TE",
                    "pressure side": "PS", "pressure_side": "PS", "pressureside": "PS", "ps": "PS",
                    "suction side": "SS", "suction_side": "SS", "suctionside": "SS", "ss": "SS",
                }
                component_attr = mapping.get(child_label)
                self.top_item = item.parent()
            else:
                self.top_item = item

            self.selected_airfoil_index = self.indexOfTopLevelItem(self.top_item)
            if self.selected_airfoil_index == -1:
                self.logger.debug("Top-level item index not found for selected item")
                return

            self.selected_airfoil = self.PROJECT.airfoils[self.selected_airfoil_index]
            self.selected_airfoil.update()

            if component_attr:
                self.selected = getattr(self.selected_airfoil, component_attr)
            else:
                self.selected = self.selected_airfoil
    
            if self.AIRFOILDESIGNER.OPEN_GL:
                    # Always set the full airfoil; if viewport supports component-highlight, call it
                    self.AIRFOILDESIGNER.OPEN_GL.set_airfoil_to_display(self.selected_airfoil)
                    if component_attr and hasattr(self.AIRFOILDESIGNER.OPEN_GL, "set_component_to_display"):
                        try:
                            self.AIRFOILDESIGNER.OPEN_GL.set_component_to_display(self.selected_airfoil, component_attr)
                        except Exception:
                            self.logger.exception("Viewport failed to set component display")
                    # force repaint so component selection is immediately visible
                    try:
                        self.AIRFOILDESIGNER.OPEN_GL.update()
                    except Exception:
                        self.logger.exception("Failed to request viewport update")
                    self.logger.debug('Passed airfoil (and component if any) to be displayed')
            else:
                self.logger.exception("Failed to set airfoil to viewport")
        else:
            self.logger.debug("Top-level item index not found")

        if item:
            self.logger.debug(f"Selected item: {item.text(0)}")
            self.logger.debug(f"Selected airfoil index: {self.selected_airfoil_index}")
            self.logger.debug(f"Selected airfoil object: {self.selected_airfoil}")
            self.logger.debug(f"Selected component attribute: {component_attr}")

            # Emit a selection event for external table widgets to update parameters
            self.logger.debug(f"Emitting selectedAirfoilChanged with: {self.selected}")
            self.selectedAirfoilChanged.emit(item, column) # changed from actual object 'self.selected' to tree item

    def add_to_tree(self, airfoil_obj=None):
        """Add an airfoil to the list and tree menu."""
        name = airfoil_obj.name
        modification_date = airfoil_obj.info.get('modification_date', 'Unknown')
        creation_date = airfoil_obj.info.get('creation_date', 'Unknown')
        tree_item = QTreeWidgetItem([airfoil_obj.name, None, str(modification_date), str(creation_date)])
        self.addTopLevelItem(tree_item)

        if airfoil_obj.LE:
            name = 'Leading Edge'
            type = airfoil_obj.LE.type.value
            le_item = QTreeWidgetItem([str(name), str(type)])
            le_item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            tree_item.addChild(le_item)
        if airfoil_obj.TE:
            name = 'Trailing Edge'
            type = airfoil_obj.TE.type.value
            te_item = QTreeWidgetItem([str(name), str(type)])
            te_item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            tree_item.addChild(te_item)
        if airfoil_obj.PS:
            name = 'Pressure Side'
            type = airfoil_obj.PS.type.value
            ps_item = QTreeWidgetItem([str(name), str(type)])
            ps_item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            tree_item.addChild(ps_item)
        if airfoil_obj.SS:
            name = 'Suction Side'
            type = airfoil_obj.SS.type.value
            ss_item = QTreeWidgetItem([str(name), str(type)])
            ss_item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            tree_item.addChild(ss_item)

        self.logger.info(f"Airfoil '{name}' added to the tree")
    
    def remove_from_tree(self, name):
        try:
            self.selected_airfoil = None
            # Remove the item from the tree menu and Update index after removal
            for i in range(self.topLevelItemCount() - 1, -1, -1):
                item = self.topLevelItem(i)
                if item.text(0) == name or (i < self.selected_airfoil_index and item.hasChildren()):
                    self.takeTopLevelItem(i)
                    break
            
        except (ValueError, AttributeError, TypeError) as e:
            self.logger.error(f'Failed to remove airfoil from tree! {e}')
            return 
        
    def update(self):
        """Update the tree based on the current self.PROJECT.airfoils."""
        self.clear()  # Clear existing items

        if self.PROJECT is None:
            return

        # Set up tree columns
        self.setColumnCount(4)  # Adjust the number of columns
        self.setHeaderLabels(["Airfoil", "Type", "Last modification", "Creation Date"])  # Set column headers
        self.setMinimumHeight(100)  # Set minimum height for the tree menu
        self.setColumnWidth(0, 120) # Set width of the first column
        self.setColumnWidth(1, 35)  # Set width of the second column
        self.setColumnWidth(2, 100)  # Set width of the third column
        self.setColumnWidth(3, 100)  # Set width of the forth column

        for airfoil in self.PROJECT.airfoils:
            self.logger.debug(f"Processing airfoil: {airfoil.name}")
            self.add_to_tree(airfoil)

        self.logger.debug("Tree refreshed")
            
    def mark_edited(self):
        self.top_item.setText(0, f"{self.selected_airfoil.name}*")

    
               
     
        
