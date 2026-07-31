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
    QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QLineEdit, QApplication, QComboBox, 
)
from PyQt6.QtCore import Qt, pyqtSignal

class TableParameters(QTableWidget):
    referenceStatus = pyqtSignal(bool, str)
    parametersChanged = pyqtSignal()

    def __init__(self, program=None, project=None, parent=None, tree_menu=None, open_gl=None, element_type='generic'):
        super(TableParameters, self).__init__(None)
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

        self.init_table()   

    def init_table(self, params=None):
        # Initial Parameters
        self.params = {}

        # Parameter Table
        self.setRowCount(len(self.params))
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Parameter", "Value", "Nominal", "Unit"])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        #self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setColumnWidth(0, 70) # Set width of the first column
        self.setColumnWidth(1, 100)  # Set width of the second column
        self.setColumnWidth(2, 70)  # Set width of the third column
        self.setColumnWidth(3, 50)  # Set width of the forth column

    def add_editable_row(self, row, param_obj):
        """Add an editable row with up/down buttons and input field."""
        # Create a custom widget for editing with up/down buttons and input
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        # Input field for direct keyboard input
        try:
            # Get the display value (converted from SI if needed)
            value = format(param_obj.get(), '.4f')  # Format value to 4 decimal places
        except (TypeError, AttributeError):
            value = str(param_obj)
        value_input = QLineEdit(str(value))
        value_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_input.editingFinished.connect(lambda: self.update_value_from_input(row, value_input))

        # Up button
        up_button = QPushButton("▲")
        up_button.setFixedSize(20, 20)
        up_button.clicked.connect(lambda: self._adjust_value_with_modifiers(row, 1))

        # Down button
        down_button = QPushButton("▼")
        down_button.setFixedSize(20, 20)
        down_button.clicked.connect(lambda: self._adjust_value_with_modifiers(row, -1))

        # Add widgets to layout
        layout.addWidget(down_button)
        layout.addWidget(value_input)
        layout.addWidget(up_button)
        self.setCellWidget(row, 1, container)

    def _adjust_value_with_modifiers(self, row, direction):
            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                delta = 1.0
            elif modifiers & Qt.KeyboardModifier.ControlModifier:
                delta = 0.01
            else:
                delta = 0.1
            self.adjust_value(row, direction * delta)
            
    def update_value_from_input(self, row, value_input):
        # Update parameter/attribute from the input field or dropdown
        param_name = self.item(row, 0).text()
        
        # Check if value_input is a string (from dropdown) or QLineEdit widget (from params)
        if isinstance(value_input, str):
            # Handle string value from attribute dropdown
            new_value = value_input
            if self.current_element and hasattr(self.current_element, 'attrs') and param_name in self.current_element.attrs:
                attr_obj = self.current_element.attrs[param_name]

                # --- For airfoils map the string back to the object ---
                if param_name == 'airfoil':
                    matched_airfoil = next((a for a in self.PROJECT.airfoils if a.name == new_value), None)
                    if matched_airfoil:
                        attr_obj.value = matched_airfoil
                    else:
                        self.logger.warning(f"Could not find airfoil object named {new_value}")
                else:
                    attr_obj.value = new_value

            self.save_current_element_state()
        else:
            # Handle float value from parameter QLineEdit
            try:
                new_value = float(value_input.text())
                
                # Update through the element's params with Param.set()
                if self.current_element and hasattr(self.current_element, 'params') and param_name in self.current_element.params:
                    param_obj = self.current_element.params[param_name]
                    if hasattr(param_obj, 'set'):
                        param_obj.set(new_value)
                    else:
                        self.current_element.params[param_name] = new_value
                else:
                    # Fallback to self.params
                    self.params[param_name] = new_value
                
                self.save_current_element_state()
            except ValueError:
                # Restore the last valid value if input is invalid
                self.logger.warning("Invalid input, restoring last valid value.")
                if self.current_element and hasattr(self.current_element, 'params') and param_name in self.current_element.params:
                    param_obj = self.current_element.params[param_name]
                    if hasattr(param_obj, 'get'):
                        value_input.setText(str(param_obj.get()))
                    else:
                        value_input.setText(str(self.current_element.params[param_name]))
                elif param_name in self.params:
                    value_input.setText(str(self.params[param_name]))

    def adjust_value(self, row, delta):
        # Adjust parameter value by delta
        param_name = self.item(row, 0).text()
        
        # Check if parameter is in the element's params dict
        if self.current_element and hasattr(self.current_element, 'params') and param_name in self.current_element.params:
            param_obj = self.current_element.params[param_name]
            
            # Handle Param objects with get/set methods
            if hasattr(param_obj, 'get') and hasattr(param_obj, 'set'):
                current_value = param_obj.get()
                new_value = current_value + delta
                param_obj.set(new_value)  # This properly updates _value_si
                display_value = param_obj.get()  # Read back to ensure consistency
            else:
                # Fallback for plain values
                new_value = param_obj + delta
                self.current_element.params[param_name] = new_value
                display_value = new_value
        else:
            # Fallback for legacy code
            if param_name in self.params:
                param_obj = self.params[param_name]
                if hasattr(param_obj, 'get') and hasattr(param_obj, 'set'):
                    current_value = param_obj.get()
                    new_value = current_value + delta
                    param_obj.set(new_value)
                    display_value = param_obj.get()
                else:
                    new_value = param_obj + delta
                    self.params[param_name] = new_value
                    display_value = new_value
            else:
                self.logger.error(f"Parameter '{param_name}' not found in current element or params dict")
                return

        # Update the input field display
        display_value_str = format(display_value, '.4f')  # Format value to 4 decimal places
        cell_widget = self.cellWidget(row, 1)
        value_input = cell_widget.findChild(QLineEdit)
        value_input.setText(str(display_value_str))
        self.logger.debug(f"Updated {param_name} to {display_value_str}")

        # Save and update 3D view
        self.save_current_element_state()
    
    def update(self):
        self.populate_table(self.current_element)
        
    def populate_table(self, element_obj):
        """Populate the table with data from an element object."""
        self.logger.debug(f"Populating table with object: {element_obj}")
        self.logger.debug(f"Object attributes: {getattr(element_obj, 'attrs', None)}")
        self.logger.debug(f"Object parameters: {getattr(element_obj, 'params', None)}")
        if not element_obj:
            self.logger.warning("No object provided to populate_table")
            return

        self.setRowCount(0)  # Clear existing rows

        # Default: show all attrs of element
        if hasattr(element_obj, 'attrs'):
            # Attr rows
            for key, attr in element_obj.attrs.items():
                row = self.rowCount()
                self.insertRow(row)
                self.setItem(row, 0, QTableWidgetItem(key))
                attr_dropdown = QComboBox(self)

                if key == 'airfoil':
                    allowed_values = [arf.name for arf in self.PROJECT.airfoils]
                else:
                    allowed_values = attr.allowed_values

                attr_dropdown.addItems(allowed_values)
                if not isinstance(attr.value, str):
                    current_name = attr.value.name
                    nominal_name = attr.nominal.name
                else:
                    current_name = attr.value  # Get value from Attr object, not from element_obj
                    nominal_name = attr.nominal
                
                if current_name in allowed_values:
                    attr_dropdown.setCurrentText(current_name)
                elif allowed_values:
                    attr_dropdown.setCurrentIndex(0)
                
                attr_dropdown.currentTextChanged.connect(lambda new_value, r=row: self.update_value_from_input(r, new_value))
                self.setCellWidget(row, 1, attr_dropdown)
                nominal_value = QTableWidgetItem(str(nominal_name))
                nominal_value.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, 2, nominal_value)
        
        # Default: show all params of element
        if hasattr(element_obj, 'params'):
            # Params rows
            for key, param in element_obj.params.items():
                row = self.rowCount()
                self.insertRow(row)
                self.setItem(row, 0, QTableWidgetItem(key))
                # Pass the Param object to add_editable_row
                if hasattr(param, 'get'):
                    # It's a Param object
                    self.add_editable_row(row, param)
                    unit_text = param.unit.name if hasattr(param, 'unit') else ''
                    nominal_text = param.nominal
                    unit_value = QTableWidgetItem(str(unit_text))
                    unit_value.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.setItem(row, 3, unit_value)
                else:
                    # It's a plain value
                    self.add_editable_row(row, param)

                nominal_value = QTableWidgetItem(str(format(nominal_text, ".4f")))
                nominal_value.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, 2, nominal_value)

    def display_selected_element(self, item, column=None):
        """Display the selected element in the table.
        Supports both wing design elements (segments/wings) and airfoil components (LE/TE/PS/SS).
        """
        if not self.tree_menu:
            return

        if not item:
            return
        
        self.logger.debug(f"ParamTable got: {item.text(0)}, {self.element_type}, {self.tree_menu}")
        
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
            child_label = selected_item.text(0).strip().lower()
            mapping = {
                "leading edge": "LE", "leading_edge": "LE", "leadingedge": "LE", "le": "LE",
                "trailing edge": "TE", "trailing_edge": "TE", "trailingedge": "TE", "te": "TE",
                "pressure side": "PS", "pressure_side": "PS", "pressureside": "PS", "ps": "PS",
                "suction side": "SS", "suction_side": "SS", "suctionside": "SS", "ss": "SS",
            }
            component_attr = mapping.get(child_label)
            top_item = selected_item.parent()
        else:
            top_item = selected_item

        item_index = self.tree_menu.indexOfTopLevelItem(top_item)
        if item_index == -1:
            self.logger.debug("Top-level item index not found for selected item")
            return
            
        selected_airfoil = self.PROJECT.airfoils[item_index]
        
        if component_attr:

            selected_component = getattr(selected_airfoil, component_attr, None)
            if selected_component:
                self.populate_table(selected_component)
                self.current_element = selected_component
                self.params = {key: value for key, value in vars(selected_component).items()}
                # Tell viewport about parent airfoil and component
                if self.open_gl:
                    try:
                        self.open_gl.set_airfoil_to_display(selected_airfoil)
                        if hasattr(self.open_gl, "set_component_to_display"):
                            self.open_gl.set_component_to_display(selected_airfoil, component_attr)
                        self.open_gl.update()
                    except Exception:
                        self.logger.exception("Failed to update viewport for component")
                self.logger.debug(f"Displayed component '{component_attr}' parameters")
            else:
                self.logger.warning(f"Component '{component_attr}' not found on selected airfoil")
        else:
            # Top-level airfoil selected -> show overall params
            self.populate_table(selected_airfoil)
            self.current_element = selected_airfoil
            self.params = {key: value for key, value in vars(selected_airfoil).items() if key != "info"}
            if self.open_gl:
                try:
                    self.open_gl.set_airfoil_to_display(selected_airfoil)
                except Exception:
                    self.logger.exception("Failed to set airfoil to viewport")
            self.logger.debug('Displayed parent airfoil parameters')
            

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
            self.params = {key: value for key, value in vars(element_item).items() if key != "info"}
        
        # ----- LEVEL 3: SEGMENT -----
        elif parent_item and grandparent_item:
            item_index = parent_item.indexOfChild(selected_item)
            parent_index = grandparent_item.indexOfChild(parent_item)
            grandparent_index = self.tree_menu.indexOfTopLevelItem(grandparent_item)

            self.logger.debug(f'Segment at index: {grandparent_index}:{parent_index}:{item_index}')

            element_item = self.PROJECT.components[grandparent_index].wings[parent_index].segments[item_index]

            self.current_element = element_item
            self.populate_table(element_item)
            self.params = {key: value for key, value in vars(element_item).items() if key != "info"}

        # ----- LEVEL 2: WING -----
        elif parent_item and not grandparent_item:
            item_index = parent_item.indexOfChild(selected_item)
            parent_index = self.tree_menu.indexOfTopLevelItem(parent_item)
            
            self.logger.debug(f'Wing at index: {parent_index}:{item_index}')
            
            element_item = self.PROJECT.components[parent_index].wings[item_index]
            self.current_element = element_item
            self.populate_table(element_item)
            self.params = {key: value for key, value in vars(element_item).items() if key != "info"}

        # ----- LEVEL 1: COMPONENT -----
        elif not parent_item and not grandparent_item:
            item_index = self.tree_menu.indexOfTopLevelItem(selected_item)
            
            self.logger.debug(f'Component at index: {item_index}')
            
            element_item = self.PROJECT.components[item_index]
            self.current_element = element_item
            self.populate_table(element_item)
            self.params = {key: value for key, value in vars(element_item).items() if key != "info"}
        
        if self.open_gl:
            self.open_gl.update()


    def save_current_element_state(self):
        """Overwrite the current table data into the selected airfoil object."""
        selected_item = self.tree_menu.currentItem()
            
        if not selected_item:
            return

        parent_item = selected_item.parent()
        grandparent_item = parent_item.parent() if parent_item else None
        great_grandparent_item = grandparent_item.parent() if grandparent_item else None
            
        selected_airfoil = None

        if self.element_type == 'airfoil':
            top_item = selected_item.parent() if selected_item.parent() else selected_item
            item_index = self.tree_menu.indexOfTopLevelItem(top_item)

            if item_index == -1:
                self.logger.error('Failed to determine selected airfoil index for save')
                return

            selected_airfoil = self.PROJECT.airfoils[item_index]
            self.logger.info(f'Airfoil at index: {item_index} saved')

            if selected_item.parent():
                child_label = selected_item.text(0).strip().lower()
                mapping = {
                    'leading edge': 'LE', 'leading_edge': 'LE', 'leadingedge': 'LE', 'le': 'LE',
                    'trailing edge': 'TE', 'trailing_edge': 'TE', 'trailingedge': 'TE', 'te': 'TE',
                    'pressure side': 'PS', 'pressure_side': 'PS', 'pressureside': 'PS', 'ps': 'PS',
                    'suction side': 'SS', 'suction_side': 'SS', 'suctionside': 'SS', 'ss': 'SS',
                }
                component_attr = mapping.get(child_label)
                if component_attr and hasattr(selected_airfoil, component_attr):
                    element_item = getattr(selected_airfoil, component_attr)
                else:
                    element_item = selected_airfoil
            else:
                element_item = selected_airfoil

            self.current_element = element_item
        
        else:
            # ----- AIRFOIL UPDATE -----
            if great_grandparent_item:
                
                item_index = grandparent_item.indexOfChild(parent_item)
                parent_index = great_grandparent_item.indexOfChild(grandparent_item)
                grandparent_index = self.tree_menu.indexOfTopLevelItem(great_grandparent_item)

                self.logger.info(f'Airfoil inside Segment at index: {grandparent_index}:{parent_index}:{item_index} saved')
                
                segment_item = self.PROJECT.components[grandparent_index].wings[parent_index].segments[item_index]
                element_item = segment_item.attrs['airfoil'].value
                try:
                    element_item.update()
                    self.PROJECT.components[grandparent_index].wings[parent_index].segments[item_index].update()
                    self.PROJECT.components[grandparent_index].wings[parent_index].update()
                except Exception as e:
                    self.logger.warning(f'Failed to transform segment: {e}')

            # ----- SEGMENT UPDATE -----
            elif parent_item and grandparent_item:

                item_index = parent_item.indexOfChild(selected_item)
                parent_index = grandparent_item.indexOfChild(parent_item)
                grandparent_index = self.tree_menu.indexOfTopLevelItem(grandparent_item)

                self.logger.info(f'Segment at index: {grandparent_index}:{parent_index}:{item_index} saved')
                
                element_item = self.PROJECT.components[grandparent_index].wings[parent_index].segments[item_index]

            # ----- WING UPDATE -----
            elif parent_item and not grandparent_item:

                item_index = parent_item.indexOfChild(selected_item)
                parent_index = self.tree_menu.indexOfTopLevelItem(parent_item)

                self.logger.info(f'Wing at index: {parent_index} >>> {item_index} saved')

                element_item = self.PROJECT.components[parent_index].wings[item_index]
            
            # ----- COMPONENT UPDATE -----
            elif not parent_item and not grandparent_item:

                item_index = self.tree_menu.indexOfTopLevelItem(selected_item)

                self.logger.info(f'WNGWB > Save_state > Component at index: {item_index} saved')

                element_item = self.PROJECT.components[item_index]

        # Update the airfoil object with table data
        for row in range(self.rowCount()):
            key = self.item(row, 0).text()
            # Retrieve the value from the QLineEdit inside the custom widget
            cell_widget = self.cellWidget(row, 1)
            if cell_widget:
                combo_box = self.cellWidget(row, 1) if isinstance(self.cellWidget(row, 1), QComboBox) else None
                line_edit = cell_widget.findChild(QLineEdit)

                if combo_box:
                    value = combo_box.currentText()
                    if key == "anchor":
                        element_item.anchor = value
                        self.logger.info(f"WNGWB > Save_state > Saved anchor: {value}")
                    if key == "airfoil":
                        selected_name = combo_box.currentText()
                        matched_airfoil = next(
                            (a for a in self.PROJECT.airfoils if a.name == selected_name),
                            None
                        )
                        if matched_airfoil:
                            # Safely set the airfoil
                            if hasattr(element_item, 'attrs') and 'airfoil' in element_item.attrs:
                                element_item.attrs['airfoil'].value = matched_airfoil
                            else:
                                element_item.airfoil = matched_airfoil
                                
                            self.logger.info(f"Set airfoil: {matched_airfoil.name}")
                            
                            # --- UPDATE THE TREE MENU NODE ---
                            if selected_item and selected_item.childCount() > 0:
                                selected_item.child(0).setText(0, matched_airfoil.name)
                        else:
                            self.logger.warning(f"Airfoil '{selected_name}' not found!")
                    else:
                        self.logger.warning(f"Skipped unknown ComboBox: {key}")

                elif line_edit:
                    try:
                        value = float(line_edit.text())
                        if hasattr(element_item, "params") and key in element_item.params:
                            param_obj = element_item.params[key]
                            # Check if it's a Param object with a set() method
                            if hasattr(param_obj, 'set'):
                                param_obj.set(value)
                            else:
                                element_item.params[key] = value
                        else:
                            setattr(element_item, key, value)
                    except ValueError:
                        self.logger.error(f"Invalid value for parameter '{key}', skipping update.")
        
        # Get the 'name' attribute, or fall back to the class name if 'name' is missing
        element_name = getattr(element_item, 'name', element_item.__class__.__name__)
        self.logger.info(f"Saved params of: {element_name}")

        # ----- CASCADE UPDATES -----
        if self.element_type != 'airfoil':          
            # Level 4: Airfoil triggers Segment update
            if great_grandparent_item:
                updated_airfoil = element_item
                self._update_all_segments_with_airfoil(updated_airfoil)

            # Level 3: Segment update
            elif parent_item and grandparent_item:
                try:
                    self.PROJECT.components[grandparent_index].wings[parent_index].segments[item_index].update()
                    self.PROJECT.components[grandparent_index].wings[parent_index].update()
                except:
                    self.logger.warning('No segment to transform')

            # Level 2: Wing update
            elif parent_item and not grandparent_item:
                for i in range(len(self.PROJECT.components[parent_index].wings[item_index].segments)):
                    try:
                        self.PROJECT.components[parent_index].wings[item_index].segments[i].update()
                    except:
                        self.logger.warning('No segment to transform')
                    try:
                        self.PROJECT.components[parent_index].wings[item_index].update()
                    except:
                        self.logger.warning('No wing to transform')

            # Level 1: Component update
            elif not parent_item and not grandparent_item:
                for w in range(len(self.PROJECT.components[item_index].wings)):
                    for i in range(len(self.PROJECT.components[item_index].wings[w].segments)):
                        try:
                            self.PROJECT.components[item_index].wings[w].segments[i].update()
                        except:
                            self.logger.warning('No segment to transform')
                        try:
                            self.PROJECT.components[item_index].wings[w].update()
                        except:
                            self.logger.warning('No wing to transform')
                        try:
                            self.PROJECT.components[item_index].update()
                        except:
                            self.logger.warning('No component to transform')

        if self.element_type == 'airfoil' and selected_airfoil is not None:
            try:
                selected_airfoil.update()
                self._update_all_segments_with_airfoil(selected_airfoil)
            except Exception:
                self.logger.exception('Failed to update parent airfoil after saving')

        if self.element_type == 'airfoil' and self.open_gl and selected_airfoil is not None:
            try:
                self.open_gl.set_airfoil_to_display(selected_airfoil)
            except Exception:
                self.logger.exception('Failed to set airfoil to display after saving')

        if self.open_gl:
            self.open_gl.update()
        
        self.parametersChanged.emit()
        
    
    def _update_all_segments_with_airfoil(self, target_airfoil):
        """Iterates through the project and updates any segment sharing the target_airfoil."""
        if not self.PROJECT:
            return

        for component in self.PROJECT.components:
            for wing in component.wings:
                wing_needs_update = False
                for segment in wing.segments:
                    # Check if the segment uses this specific airfoil
                    if hasattr(segment, 'attrs') and 'airfoil' in segment.attrs:
                        if segment.attrs['airfoil'].value == target_airfoil:
                            try:
                                segment.update()
                                wing_needs_update = True
                                self.logger.debug(f"Updated segment '{segment.name}' due to airfoil change.")
                            except Exception as e:
                                self.logger.warning(f"Failed to update segment '{segment.name}': {e}")
                
                # Only update the wing if one of its segments was modified
                if wing_needs_update:
                    try:
                        wing.update()
                        self.logger.debug(f"Updated wing '{wing.name}' due to segment change.")
                    except Exception as e:
                        self.logger.warning(f"Failed to update wing '{wing.name}': {e}")