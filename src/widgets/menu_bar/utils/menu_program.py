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

from PyQt6.QtWidgets import QMessageBox
from src.program.preferences import PreferencesWindow

def show_preferences(self):        
    """Open the preferences dialog."""
    msg = QMessageBox(None)
    msg.setWindowTitle("WARNING!")
    msg.setText(f"If you changed the preferences, you need to restart the application for the changes to take effect.")
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)

    msg.exec()

    self.logger.info("Showing preferences window")
    
    self.preferences_dialog = PreferencesWindow(self.main_window.PROGRAM)
    self.preferences_dialog.show()        

def show_about(self):
    self.main_window.PROGRAM.showAboutDialog()

def show_manual(self):
    self.main_window.PROGRAM.showUserManual()