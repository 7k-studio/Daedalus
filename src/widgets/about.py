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

from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTextEdit
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

class About(QDialog):
    
    def __init__(self, program_version, copyright_text):
        super().__init__()
        self.setWindowTitle("About")
        self.setFixedSize(400, 400)

        # Logo
        logo_label = QLabel(self)
        #pixmap = QPixmap("src/assets/text_logo.png")
        #logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel('DAEDALUS')
        title_label.setFont(QFont("Cambria", 36))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version_label = QLabel(f"Version: {program_version}")
        version_label.setFont(QFont("Cambria", 12))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        copyright_label = QLabel(copyright_text)
        copyright_label.setFont(QFont("Cambria", 8))
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Optional description
        about_text = ["Program is created using Python: 3.11.8",
                      "STEP export is done via proprietary script",
                      "There are some exteral librieries used:",
                       # A
                       # B
                       # C
                       # D
                      "dataclasses", "datetime",
                       # E
                      "ezdxf: https://ezdxf.readthedocs.io/en/stable/",
                       # F
                       # G
                      "geomdl",
                       # H
                       # I
                       # J
                       "json",
                       # K
                       # L
                       "logging",
                       # M
                       # N
                       "numpy",
                       # O
                       "os",
                       # P
                      "PIL", "Pyinstaller", "PyQt6: https://doc.qt.io/qtforpython-6/", "PyOpenGL", "PyOpenGL_accelerate", 
                       # Q
                       # R
                       # S
                       "scipy",
                       # T
                       # U
                       # V
                       # W
                       "webbrowser",
                       # X
                       # Y
                       # Z
                       ]

        description_text = QTextEdit()
        description_text.setReadOnly(True)
        description_text.setPlainText('\n'.join(about_text))
        
        description_label = QLabel("DAEDALUS is a program for parametricaly designing airfoils and wings.")
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setWordWrap(True)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(100)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(copyright_label)
        layout.addWidget(description_text)

        bottom_layout = QHBoxLayout()
        bottom_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        bottom_layout.addWidget(close_button)
        bottom_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        layout.addLayout(bottom_layout)
        self.setLayout(layout)
        self.exec()