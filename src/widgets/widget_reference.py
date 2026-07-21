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
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, QAbstractItemView,
    QHeaderView, QTableWidget, QTableWidgetItem, QPushButton
    )
from PyQt6.QtCore import Qt, pyqtSignal

class WidgetReference(QWidget):
    referenceStatus = pyqtSignal(bool, str)
    def __init__(self, program=None, project=None, parent=None, airfoil_designer=None, mode='show', references=None):
        super(WidgetReference, self).__init__(parent)
        self.setMinimumSize(200, 100)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.PROGRAM = program
        self.PROJECT = project
        self.AIRFOIL_MODULE = airfoil_designer

        self.references = references
        self.mode = mode
        self.selected_references = []

        self.init_ui()

    def init_ui(self):

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Name", "Format", "Visible"])
        self.table.setMinimumHeight(50)
        
        # Configure table appearance
        self.table.verticalHeader().setVisible(False) # Hide row numbers
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Disable text editing
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 60)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Connect the checkbox change signal
        self.table.itemChanged.connect(self.on_item_changed)

        self.layout.addWidget(self.table)

        options_buttons = QHBoxLayout()
        
        addButton = QPushButton("+")
        addButton.clicked.connect(self.trigger_add)
        addButton.setFixedSize(24, 24)

        delButton = QPushButton("-")
        delButton.clicked.connect(self.trigger_delete)
        delButton.setFixedSize(24, 24)

        ediButton = QPushButton("Edit")
        ediButton.clicked.connect(self.AIRFOIL_MODULE.editReference)
        ediButton.setFixedHeight(24)

        options_buttons.addWidget(addButton)
        options_buttons.addWidget(delButton)
        options_buttons.addStretch()
        
        if self.PROGRAM.preferences['general'].get('beta_features', False):
            options_buttons.addWidget(ediButton)

        self.layout.addLayout(options_buttons)
        self.refresh_table()

    # --- UI Triggers to bridge to Controller ---

    def trigger_add(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", 
            "Accepted file formats (*.ddls; *.txt; *.dat);; Daedalus Database Files (*.ddls);; Selig Format (*.txt);; All Files (*)"
        )
        if fileName:
            self.AIRFOIL_MODULE.addReference(fileName)
            self.refresh_table()

    def trigger_delete(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.logger.warning("First select an airfoil to delete!")
            return
        
        refs_to_delete = []
        for item in selected_items:
            if item.column() == 0:
                refs_to_delete.append(item.data(Qt.ItemDataRole.UserRole))
                
        if refs_to_delete:
            self.AIRFOIL_MODULE.deleteReference(refs_to_delete)
        self.refresh_table()

    def on_item_changed(self, item):
        if item.column() == 2:
            # Get the airfoil object stored in column 0 of the same row
            name_item = self.table.item(item.row(), 0)
            if name_item:
                airfoil_obj = name_item.data(Qt.ItemDataRole.UserRole)
                is_checked = (item.checkState() == Qt.CheckState.Checked)
                self.AIRFOIL_MODULE.toggleReferenceVisibility(airfoil_obj, is_checked)

    # --- Table Population ---

    def refresh_table(self):
        # Block signals briefly so populating the table doesn't trigger on_item_changed
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        
        if self.PROJECT and hasattr(self.PROJECT, 'reference_airfoils'):
            for airfoil in self.PROJECT.reference_airfoils:
                self.add_to_table(airfoil)
                
        self.table.blockSignals(False)
        self.logger.info("Reference Table refreshed")

    def add_to_table(self, airfoil_obj):
        row = self.table.rowCount()
        self.table.insertRow(row)

        name_item = QTableWidgetItem(getattr(airfoil_obj, 'name', 'Unknown'))
        name_item.setData(Qt.ItemDataRole.UserRole, airfoil_obj) 
        
        format_item = QTableWidgetItem(getattr(airfoil_obj, 'format', 'Unknown'))
        format_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        vis_item = QTableWidgetItem()
        vis_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        vis_item.setCheckState(Qt.CheckState.Checked if getattr(airfoil_obj, 'visible', False) else Qt.CheckState.Unchecked)
        
        self.table.setItem(row, 0, name_item)
        self.table.setItem(row, 1, format_item)
        self.table.setItem(row, 2, vis_item)