'''

Copyright (C) 2025 Jakub Kamyk

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

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon

import logging


class SplashScreen(QWidget):
    def __init__(self, program=None):
        super().__init__()
        self.DAEDALUS = program
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle("Splash Screen")
        self.setFixedSize(500, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add splash image
        splash_label = QLabel(self)
        pixmap = QPixmap("src/assets/logo.png")
        if pixmap.isNull():
            self.logger.error(" 'logo.png' not found or invalid path.")
        splash_label.setPixmap(pixmap)
        splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(splash_label)

        program_label = QLabel('Daedalus Airfoil & Wing designer')
        program_label.setStyleSheet("font-size: 12px; font-weight: regular;")
        layout.addWidget(program_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        version_label = QLabel('v{}'.format(self.DAEDALUS.version))
        version_label.setStyleSheet("font-size: 12px; font-weight: regular;")
        layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        copyright_label = QLabel('Copyright © 2025-2026 Jakub Kamyk')
        copyright_label.setStyleSheet("font-size: 9px; font-weight: regular;")
        layout.addWidget(copyright_label, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        
        self.logger.debug("SplashScreen initialized")
       
        # self.close()