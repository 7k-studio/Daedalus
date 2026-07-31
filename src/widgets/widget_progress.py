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

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QCoreApplication

class ProgressDialog(QDialog):
    def __init__(self, title="Loading Project...", parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setFixedSize(400, 110)

        self.value = 0
        self.max_value = 100
        
        # Ustawiamy flagi: niezależne okienko dialogowe z tytułem (bez przycisku zamykania X, żeby użytkownik nie przerwał wczytywania)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Używamy Layoutu zamiast setGeometry
        layout = QVBoxLayout(self)

        self.task_label = QLabel("Initializing...", self)
        layout.addWidget(self.task_label)
        
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(self.max_value)
        self.progressBar.setValue(self.value)
        layout.addWidget(self.progressBar)

    def set_progress(self, value: int, message: str = None):
        """Aktualizuje pasek postępu i wymusza odświeżenie interfejsu (UI)."""
        self.progressBar.setValue(value)
        if message:
            self.task_label.setText(message)
        
        # Kluczowe! Odświeża UI w trakcie trwania pętli w Pythonie
        QCoreApplication.processEvents()

    def increase_progress(self, increasement: int, message: str = None):
        """Aktualizuje pasek postępu i wymusza odświeżenie interfejsu (UI)."""
        self.value = self.value+increasement
        self.progressBar.setValue(self.value)
        if message:
            self.task_label.setText(message)
                
        # Kluczowe! Odświeża UI w trakcie trwania pętli w Pythonie
        QCoreApplication.processEvents()
