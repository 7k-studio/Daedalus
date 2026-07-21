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
import logging
from pathlib import Path
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal, QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

class TreeObject(QTreeWidget):
    
    selectedObjectChanged = pyqtSignal(object, int)

    def __init__(self, program=None, project=None, parent=None, wing_designer=None):
        super(TreeObject, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.PROJECT = project
        self.main_window = parent
        self.wing_designer = wing_designer

        self.selected_component = None
        self.selected_wing = None
        self.selected_segment = None
        self.setIconSize(QSize(18, 18))
        self.setIndentation(12)

        # Connect selection events only once
        self.itemClicked.connect(self.on_select)
        self.update()

    def _icon_path(self, icon_name):
        icon_dir = Path(__file__).resolve().parents[1] / "assets" / "IconPack" / "Classic_Black"
        candidates = [
            icon_dir / f"{icon_name}.svg",
            icon_dir / f"{icon_name}.SVG",
            icon_dir / f"{icon_name}.Svg",
            icon_dir / f"{icon_name}.png",
        ]

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        for candidate in icon_dir.glob("*.svg"):
            if candidate.stem.lower() == icon_name.lower():
                return str(candidate)

        return ""

    def _fallback_icon(self, item_type):
        colors = {
            "Component": QColor("#5f7c4d"),
            "Wing": QColor("#8a5d3b"),
            "Segment": QColor("#4d6a7a"),
            "Airfoil": QColor("#7c4d5f"),
        }
        color = colors.get(item_type, QColor("#5f7c4d"))
        pixmap = QPixmap(18, 18)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(color)
        painter.setPen(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(1, 1, 16, 16, 4, 4)
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, item_type[0])
        painter.end()

        return QIcon(pixmap)

    def set_item_icon(self, tree_item, item_type):
        icon_path = self._icon_path(item_type)
        if icon_path:
            icon = QIcon(icon_path)
            if not icon.isNull():
                tree_item.setIcon(0, icon)
                return

        tree_item.setIcon(0, self._fallback_icon(item_type))

    def update(self):
        """Update the tree menu based on the current self.PROJECT.components."""
        self.clear()  # Clear existing items

        if self.PROJECT is None:
            return
        
        # Set up tree columns
        self.setColumnCount(3)  # Adjust the number of columns
        self.setHeaderLabels(["Object", "Last modification", "Creation Date"])  # Set column headers
        self.setMinimumHeight(100)  # Set minimum height for the tree menu
        self.setColumnWidth(0, 140)  # Set width of the first column
        self.setColumnWidth(1, 105)  # Set width of the second column
        self.setColumnWidth(2, 105)  # Set width of the third column

        for component in self.PROJECT.components:
            name = component.name
            modification_date = component.info.get('modification_date', 'Unknown')
            creation_date = component.info.get('creation_date', 'Unknown')
            tree_item = QTreeWidgetItem([str(name), str(modification_date), str(creation_date)])
            self.set_item_icon(tree_item, "Component")
            self.addTopLevelItem(tree_item)

            for wing in component.wings:
                wing_name = wing.name
                modification_date = component.info.get('modification_date', 'Unknown')
                creation_date = component.info.get('creation_date', 'Unknown')
                wing_item = QTreeWidgetItem([str(wing_name), str(modification_date), str(creation_date)])
                self.set_item_icon(wing_item, "Wing")
                tree_item.addChild(wing_item)
                tree_item.setExpanded(True)

                for segment in wing.segments:
                    segment_name = segment.name
                    modification_date = component.info.get('modification_date', 'Unknown')
                    creation_date = component.info.get('creation_date', 'Unknown')
                    segment_item = QTreeWidgetItem([str(segment_name), str(modification_date), str(creation_date)])
                    self.set_item_icon(segment_item, "Segment")
                    wing_item.addChild(segment_item)
                    wing_item.setExpanded(True)

                    # Add Airfoil as a child of Segment
                    if hasattr(segment, 'attrs') and 'airfoil' in segment.attrs:
                        airfoil_obj = segment.attrs['airfoil'].value
                        if airfoil_obj:
                            airfoil_name = airfoil_obj.name
                            airfoil_item = QTreeWidgetItem([str(airfoil_name), str(modification_date), str(creation_date)])
                            self.set_item_icon(airfoil_item, "Airfoil")
                            segment_item.addChild(airfoil_item)
                            segment_item.setExpanded(True)
                        # NOTE: Do NOT add LE, TE, PS, SS, CHORD as children - they are implementation details

    def on_select(self, item, column):
        # Handle item click events
        self.logger.debug(f"Clicked on: {item.text(column)}")
        
        # Determine the level and set selected items
        parent = item.parent()
        grandparent = parent.parent() if parent else None
        great_grandparent = grandparent.parent() if grandparent else None
        
        if parent is None:
            # Top-level: Component
            self.selected_component = self.PROJECT.components[self.indexOfTopLevelItem(item)]
            self.selected_wing = None
            self.selected_segment = None
            self.logger.debug(f"Selected Component: {self.selected_component.name}")
            
        elif grandparent is None:
            # Wing level (parent is component)
            component_index = self.indexOfTopLevelItem(parent)
            self.selected_component = self.PROJECT.components[component_index]
            wing_index = parent.indexOfChild(item)
            self.selected_wing = self.selected_component.wings[wing_index]
            self.selected_segment = None
            self.logger.debug(f"Selected Wing: {self.selected_wing.name}")
            
        elif great_grandparent is None:
            # Segment level (parent is wing, grandparent is component)
            component_index = self.indexOfTopLevelItem(grandparent)
            self.selected_component = self.PROJECT.components[component_index]
            wing_index = grandparent.indexOfChild(parent)
            self.selected_wing = self.selected_component.wings[wing_index]
            segment_index = parent.indexOfChild(item)
            self.selected_segment = self.selected_wing.segments[segment_index]
            self.logger.debug(f"Selected Segment: {self.selected_segment.name}")
            
        else:
            # Airfoil level (parent is segment, grandparent is wing, great_grandparent is component)
            component_index = self.indexOfTopLevelItem(great_grandparent)
            self.selected_component = self.PROJECT.components[component_index]
            wing_index = great_grandparent.indexOfChild(grandparent)
            self.selected_wing = self.selected_component.wings[wing_index]
            segment_index = grandparent.indexOfChild(parent)
            self.selected_segment = self.selected_wing.segments[segment_index]
            # Airfoil is accessed through segment
            self.selected_airfoil = self.selected_segment.attrs['airfoil'].value
            self.logger.debug(f"Selected Airfoil: {self.selected_airfoil.name}")
            self.selected_segment.update()
        
        if self.wing_designer and hasattr(self.wing_designer, 'NODE_TREE'):
            self.wing_designer.NODE_TREE.update_for_selection(self, item)

        # Emit a generic selection changed event for external components like ParamTabele
        self.logger.debug(f"Emitting selectedObjectChanged with item: {item}, column: {column}")
        self.selectedObjectChanged.emit(item, column)
    
    def add_component_to_tree(self, component_obj):
        """Add a component to the list and tree menu."""
        
        name = component_obj.name
        modification_date = component_obj.info.get('modification_date', 'Unknown')
        creation_date = component_obj.info.get('creation_date', 'Unknown')
        tree_item = QTreeWidgetItem([str(name), str(modification_date), str(creation_date)])
        self.set_item_icon(tree_item, "Component")
        self.addTopLevelItem(tree_item)

    def add_wing_to_tree(self, wing_obj):
        """Add a wing to the selected component in the list."""

        name = wing_obj.name
        tree_item = QTreeWidgetItem([str(name)])
        self.set_item_icon(tree_item, "Wing")
        
        item = self.currentItem()
        if item is not None:
            item.addChild(tree_item)
            item.setExpanded(True) # Expand the parent item to show the new child 

    def add_segment_to_tree(self, segment_obj):
        """Add a segment to the wing and attach its airfoil as a child item."""
        
        segment_item = QTreeWidgetItem([str(segment_obj.name)])
        self.set_item_icon(segment_item, "Segment")

        airfoil_item = QTreeWidgetItem([str(segment_obj.attrs['airfoil'].value.name)])
        self.set_item_icon(airfoil_item, "Airfoil")
        segment_item.addChild(airfoil_item)
        
        item = self.currentItem()

        if item:
            parent_item = item.parent() #Find parent item
            if parent_item:
                wing_index = parent_item.indexOfChild(item)
                component_index = self.indexOfTopLevelItem(parent_item)

                if wing_index != -1 and component_index != -1:
                    
                    item.addChild(segment_item)

                    # Expand the parent item to show the new child
                    item.setExpanded(True)
                    segment_item.setExpanded(True)
                    airfoil_item.setExpanded(True)

            
    def delete(self):
        try:
            if self.selected_airfoil is None:
                self.logger.error('No valid airfoil selected!')
                return False, None
            
            name = self.selected_airfoil.name
            
            # Remove from project airfoils
            self.PROJECT.airfoils.remove(self.selected_airfoil)
            
            # If it's in nominal_airfoils, remove from there too
            if self.selected_airfoil in self.PROJECT.nominal_airfoils:
                self.PROJECT.nominal_airfoils.remove(self.selected_airfoil)
            
            # Remove the item from the tree menu
            self.tree.takeTopLevelItem(self.selected_airfoil_index)
            
            self.logger.info(f"Deleted airfoil: {name}") 
            self.AIRFOILDESIGNER.OPEN_GL.clear()
            return True, name
        except (ValueError, AttributeError, TypeError):
            self.logger.error('Failed to delete airfoil!')
            return False, None  
        
    def mark_edited(self):
        self.top_item.setText(0, f"{self.selected_airfoil.name}*")