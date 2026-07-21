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
import logging

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QDialog, QDialogButtonBox
from PyQt6.QtCore import pyqtSignal

class WidgetDescription(QWidget):
    closed = pyqtSignal()  # Signal emitted when the widget is closed

    def __init__(self, parent=None, program=None, project=None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.DAEDALUS = program
        self.PROJECT = project
        self.selected_airfoil = None
        self.selected_tree_item = None

        self.widget()

    def widget(self):
        self.setWindowTitle("Description Widget")
        self.setMinimumSize(200, 50)

        # Layout
        layout = QVBoxLayout(self)

        # Text area
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)  # Initially read-only
        layout.addWidget(self.text_area)

        # Buttons
        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit", self)
        self.edit_button.clicked.connect(self.edit_dialog)
        button_layout.addWidget(self.edit_button)

        layout.addLayout(button_layout)

    def edit_dialog(self):
        """Open a dialog to edit the description."""
        dialog = EditDescriptionDialog(self.text_area.toPlainText(), self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_desc = dialog.get_text()
            self.PROJECT.description = new_desc
            self.text_area.setPlainText(new_desc)
            self.logger.info("Description edited succesfully!")

    def set_description(self, text=None):
        """Set the description text."""
        if text:
            self.text_area.setPlainText(text)
        else:
            if self.PROJECT:
                self.text_area.setPlainText(self.PROJECT.description)

class EditDescriptionDialog(QDialog):
    def __init__(self, initial_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Project Description")
        self.setMinimumSize(400, 300)
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout(self)
        self.edit_area = QTextEdit(self)
        self.edit_area.setPlainText(initial_text)
        layout.addWidget(self.edit_area)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel, self)
        layout.addWidget(button_box)

        button_box.accepted.connect(lambda: self._save_description(self.edit_area, self))
        button_box.rejected.connect(self.reject)

    def _save_description(self, edit_area, dialog):
        """Save the edited description."""
        new_desc = edit_area.toPlainText()
        self.edit_area.setPlainText(new_desc)

        dialog.accept()

    def closeEvent(self, event):
        """Handle the close event and emit the closed signal."""
        self.closed.emit()
        super().closeEvent(event)
        self.logger.info("Aborted")
    
    def get_text(self):
        return self.edit_area.toPlainText()