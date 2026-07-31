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

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QApplication, QFrame, QFileDialog
    )
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon

from src.program.modules.arfdes.airfoil_designer import AirfoilDesigner  # Import the AirfoilDesigner class from the correct module
from src.program.modules.wngdes.wing_designer import WingDesigner
import src.program.project as project

import logging


class HomeScreen(QWidget):
    def __init__(self, program=None):
        super().__init__()
        self.DAEDALUS = program
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle("Home Screen")
        self.setFixedSize(800,500)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 48)
        self.setLayout(layout)

        # Add splash image
        header_card = QFrame()
        header_card.setProperty("CardFrame", "true")
        header_layout = QHBoxLayout(header_card)
        splash_label = QLabel(self)
        pixmap = QPixmap("src/assets/logo.png")
        if pixmap.isNull():
            self.logger.error(" 'logo.png' not found or invalid path.")
        pixmap = pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        splash_label.setPixmap(pixmap)
        splash_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(splash_label)

        labels_layout = QVBoxLayout()
        program_label = QLabel('Daedalus Airfoil & Wing designer')
        program_label.setStyleSheet("font-size: 24px; font-weight: Bold;")
        labels_layout.addWidget(program_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignHCenter)

        version_label = QLabel('v{}'.format(self.DAEDALUS.version))
        version_label.setStyleSheet("font-size: 12px; font-weight: regular;")
        labels_layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignHCenter)
        header_layout.addLayout(labels_layout)
        header_layout.addStretch()
        labels_layout.setContentsMargins(24,8,24,8)
        
        layout.addWidget(header_card)
        # layout.addStretch()
       
        # Add buttons
        main = QHBoxLayout()

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        program_card = QHBoxLayout()
        
        ### NEW FILE ###
        new_file_card = QVBoxLayout()
        new_file_card.setContentsMargins(12, 12, 12, 12)
        new_file_card.setSpacing(10)

        header = self._card_header("NewFile", "New")
        new_file_card.addWidget(header, alignment=Qt.AlignmentFlag.AlignTop)
        new_file_card.addStretch()

        new_from_airfoil_btn = QPushButton(icon = QIcon(f"{self.DAEDALUS.color_scheme['pathToIcons']}/AirfoilIcon.svg"), text="New Airfoil Design")
        new_from_airfoil_btn.clicked.connect(self.new_project_airfoil)
        # button1.setFixedSize(220, 30)  # Set fixed size for the button

        new_from_wing_btn = QPushButton(icon = QIcon(f"{self.DAEDALUS.color_scheme['pathToIcons']}/WingIcon.svg"), text="New Wing Design")
        new_from_wing_btn.clicked.connect(self.new_project_wing)

        new_file_card.addWidget(new_from_airfoil_btn)
        new_file_card.addWidget(new_from_wing_btn)

        ### OPEN FILE ###

        open_file_card = QVBoxLayout()
        open_file_card.setContentsMargins(12, 12, 12, 12)
        open_file_card.setSpacing(10)

        header = self._card_header("OpenFile", "Open")
        open_file_card.addWidget(header, alignment=Qt.AlignmentFlag.AlignTop)
        open_file_card.addStretch()

        open_file_btn = QPushButton(icon = QIcon(f"{self.DAEDALUS.color_scheme['pathToIcons']}/OpenFile.svg"), text="Open Project")
        open_file_btn.clicked.connect(self.open_project)
        # button1.setFixedSize(220, 30)  # Set fixed size for the button

        open_file_card.addWidget(open_file_btn)

        ### ADD TO CARD ###

        # Wrap cards in styled frames
        new_file_frame = self._create_card_frame(new_file_card)
        open_file_frame = self._create_card_frame(open_file_card)

        program_card = QHBoxLayout()
        program_card.addWidget(new_file_frame)
        program_card.addWidget(open_file_frame)

        ### SETTINGS CARD BELOW PROGRAM CARD ###

        settings_btn = QPushButton(icon = QIcon(f"{self.DAEDALUS.color_scheme['pathToIcons']}/Settings.svg"), text="Preferences")
        settings_btn.clicked.connect(self.open_preferences)
        # button2.setFixedSize(220, 30)  # Set fixed size for the button

        left_layout.addLayout(program_card)
        left_layout.addWidget(settings_btn)

        ### MANUAL CARD ###

        manual_card = QVBoxLayout()
        manual_card.setContentsMargins(8, 8, 8, 8)
        manual_card.setSpacing(6)

        header = self._card_header("Manual", "User Manual")
        manual_card.addWidget(header, alignment=Qt.AlignmentFlag.AlignTop)
        manual_card.addStretch()

        manual_btn = QPushButton(icon = QIcon(f"{self.DAEDALUS.color_scheme['pathToIcons']}/Manual.svg"), text="User Manual")
        manual_btn.setFixedHeight(32)
        manual_btn.clicked.connect(self.open_manual)

        manual_card.addWidget(manual_btn)

        ### WEB CARD ###

        web_card = QVBoxLayout()
        web_card.setContentsMargins(8, 8, 8, 8)
        web_card.setSpacing(6)

        header = self._card_header("Web", "Online Access")
        web_card.addWidget(header, alignment=Qt.AlignmentFlag.AlignTop)
        web_card.addStretch()

        notes_btn = QPushButton(icon = QIcon(f"{self.DAEDALUS.color_scheme['pathToIcons']}/Web.svg"), text="Reales Notes")
        notes_btn.setFixedHeight(32)
        notes_btn.clicked.connect(self.open_notes)

        web_btn = QPushButton(icon = QIcon(f"{self.DAEDALUS.color_scheme['pathToIcons']}/Web.svg"), text="Daedalus Web-page")
        web_btn.setFixedHeight(32)
        web_btn.clicked.connect(self.open_web_page)

        web_card.addWidget(notes_btn)
        web_card.addWidget(web_btn)

        # Wrap cards in styled frames
        manual_frame = self._create_card_frame(manual_card)
        manual_frame.setMaximumHeight(140)
        web_frame = self._create_card_frame(web_card)
        web_frame.setMaximumHeight(140)

        right_layout.addWidget(manual_frame)
        right_layout.addWidget(web_frame)
        right_layout.addStretch()  # Push cards to top

        main.addLayout(left_layout)
        main.addLayout(right_layout)

        # Center the buttons
        new_file_card.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(main)

        self.logger.debug("Initialized")

    def _card_header(self, icon_name, card_label):
        header_widget = QFrame()
        header_widget.setObjectName("CardHeader")
        header_widget.setFixedHeight(64)

        header_layout = QHBoxLayout(header_widget)

        icon_label = QLabel()
        new_file_icon = QIcon(f"{self.DAEDALUS.color_scheme['pathToIcons']}/{icon_name}.svg")
        icon_label.setPixmap(new_file_icon.pixmap(42, 42))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignLeft)
        card_title = QLabel(card_label)
        card_title.setStyleSheet("font-size: 18px; font-weight: Bold;")
        header_layout.addWidget(card_title, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignHCenter)

        return header_widget

    def _create_card_frame(self, layout):
        """Create a styled card frame to hold a layout.
        
        Args:
            layout: The QLayout to put inside the card frame
            
        Returns:
            QFrame: A styled card frame widget
        """
        card_frame = QFrame()
        card_frame.setProperty("CardFrame", "true")
        card_frame.setLayout(layout)
        return card_frame

    def new_project(self):
        """Create new DAEDALUS project and open the Wing Designer module."""
        self.logger.info("Creating new project")
        self.PROJECT = project.Project(self.DAEDALUS)
        
        # Create Airfoil Designer module
        self.DAEDALUS.AIRFOILDESIGNER = AirfoilDesigner(parent=self.DAEDALUS.MAIN_WINDOW, program=self.DAEDALUS, project=self.PROJECT)
        
        # Create Wing Designer module
        self.DAEDALUS.WINGDESIGNER = WingDesigner(parent=self.DAEDALUS.MAIN_WINDOW, program=self.DAEDALUS, project=self.PROJECT)
        
        # Add modules to main window
        self.DAEDALUS.MAIN_WINDOW.add_module('airfoil', self.DAEDALUS.AIRFOILDESIGNER)
        self.DAEDALUS.MAIN_WINDOW.add_module('wing', self.DAEDALUS.WINGDESIGNER)
        
        # Set project in main window before switching modules
        self.DAEDALUS.MAIN_WINDOW.set_project(self.PROJECT)

    def new_project_wing(self):

        self.new_project()
        self.DAEDALUS.MAIN_WINDOW.switch_to_module('wing')
        
        #self.close()
    
    def new_project_airfoil(self):
        
        self.new_project()
        self.DAEDALUS.MAIN_WINDOW.switch_to_module('airfoil')

        # self.close()

    def open_project(self):
        """Load DAEDALUS project and open the Wing Designer module."""
        self.logger.info("Opening existing project")
        self.PROJECT = project.Project(self.DAEDALUS)

        # Create Airfoil Designer module
        self.DAEDALUS.AIRFOILDESIGNER = AirfoilDesigner(parent=self.DAEDALUS.MAIN_WINDOW, program=self.DAEDALUS, project=self.PROJECT)
        # Create Wing Designer module
        self.DAEDALUS.WINGDESIGNER = WingDesigner(parent=self.DAEDALUS.MAIN_WINDOW, program=self.DAEDALUS, project=self.PROJECT)

        self.DAEDALUS.MAIN_WINDOW.add_module('airfoil', self.DAEDALUS.AIRFOILDESIGNER)
        self.DAEDALUS.MAIN_WINDOW.add_module('wing', self.DAEDALUS.WINGDESIGNER)

        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Daedalus Database Files (*.ddls);; All Files (*)")
        if filePath:
            self.PROJECT.open(filePath)
        
        # Set project in main window before switching modules
        self.DAEDALUS.MAIN_WINDOW.set_project(self.PROJECT)
        self.DAEDALUS.MAIN_WINDOW.switch_to_module('wing')
        
        self.close()

    def open_preferences(self):
        self.logger.info("Opening preferences")
        self.DAEDALUS.showPreferences()

    def open_manual(self):
        self.logger.info("Opening user manual")
        self.DAEDALUS.showUserManual()

    def open_notes(self):
        self.DAEDALUS.showRealiseNotes()
    
    def open_web_page(self):
        self.DAEDALUS.showDedicatedWebpage()


if __name__ == "__main__":
    import sys
    import os

    root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(root, "src")
    sys.path.insert(0, src_dir)

    from src.program.program import Program
    from main_window import MainWindow
    
    
    app = QApplication(sys.argv)
    home = HomeScreen()
    home.show()
    sys.exit(app.exec_())