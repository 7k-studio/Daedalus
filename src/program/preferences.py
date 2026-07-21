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
import os
import logging
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QCheckBox, QLabel, QDialog, QPushButton, QHBoxLayout, QComboBox, QSlider
)
from PyQt6.QtCore import Qt
import json

class PreferencesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.DAEDALUS = parent
        self.setWindowTitle("Preferences")
        self.resize(300, 200)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.tabs = QTabWidget()
        self.general_tab = QWidget()
        self.airfoil_tab = QWidget()
        self.wing_tab = QWidget()

        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.airfoil_tab, "Airfoil")
        self.tabs.addTab(self.wing_tab, "Wing")

        self.init_general_tab()
        self.init_airfoil_tab()
        self.init_wing_tab()

        btn_box = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Close")
        btn_box.addWidget(self.save_btn)
        btn_box.addWidget(self.cancel_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addLayout(btn_box)
        self.setLayout(layout)

        self.save_btn.clicked.connect(self.save_preferences)
        self.cancel_btn.clicked.connect(self.reject)

    def init_general_tab(self):
        layout = QVBoxLayout()
        perf_layout = QHBoxLayout()
        length_layout = QHBoxLayout()
        angle_layout = QHBoxLayout()
        color_layout = QHBoxLayout()

        units_text = QLabel("Units:")
        units_text.setToolTip("Select the unit for the application.")

        # ComboBox for units
        length_text = QLabel("Length:")
        self.length_combo_box = QComboBox()
        self.length_combo_box.addItems(["meters"])
        self.length_combo_box.setCurrentText(self.DAEDALUS.preferences['general']['units'].get("length", "meters"))

        # ComboBox for units
        angle_text = QLabel("Angle:")
        self.angle_combo_box = QComboBox()
        self.angle_combo_box.addItems(["rad"])
        self.angle_combo_box.setCurrentText(self.DAEDALUS.preferences['general']['units'].get("angle", "rad"))
        self.length_combo_box.setCurrentText(self.DAEDALUS.preferences['general']['units'].get("length", "meters"))
        # ComboBox for Color Scheme
        color_text = QLabel("Color Scheme:")
        self.color_combo_box = QComboBox()
        styles_dir = os.path.join("src", "assets", "styles")
        try:
            # List files in styles_dir and add them without their extension
            style_files = [os.path.splitext(f)[0] for f in os.listdir(styles_dir) if os.path.isfile(os.path.join(styles_dir, f))]
            self.color_combo_box.addItems(style_files)
        except Exception as e:
            self.logger.warning("Could not list styles directory '%s': %s", styles_dir, e)

        # Select saved preference case-insensitively
        pref = self.DAEDALUS.preferences['general'].get("color_scheme", "Daedalus-Light")
        for i in range(self.color_combo_box.count()):
            if self.color_combo_box.itemText(i).lower() == str(pref).lower():
                self.color_combo_box.setCurrentIndex(i)
                break

        perf_text = QLabel("General Performance:")
        perf_text.setToolTip("Select the general performance level for the application.")

        # Slider for performance (10% - 100%)
        self.general_performance_slider = QSlider(Qt.Orientation.Horizontal)
        self.general_performance_slider.setMinimum(10)
        self.general_performance_slider.setMaximum(100)
        self.general_performance_slider.setTickInterval(10)
        self.general_performance_slider.setSingleStep(10)
        self.general_performance_slider.setValue(self.DAEDALUS.preferences['general']['performance'])  # Set initial value

        # Label to show % value
        self.general_performance_label = QLabel(f"{self.general_performance_slider.value()}%")

        self.general_performance_slider.valueChanged.connect(self.on_performance_changed)

        self.general_beta_features = QCheckBox("Beta Features")
        self.general_beta_features.setChecked(self.DAEDALUS.preferences['general']['beta_features'])

        layout.addWidget(units_text)

        length_layout.addWidget(length_text)
        length_layout.addWidget(self.length_combo_box)

        angle_layout.addWidget(angle_text)
        angle_layout.addWidget(self.angle_combo_box)

        perf_layout.addWidget(perf_text)
        perf_layout.addWidget(self.general_performance_slider)
        perf_layout.addWidget(self.general_performance_label)

        color_layout.addWidget(color_text)
        color_layout.addWidget(self.color_combo_box)

        layout.addLayout(length_layout)
        layout.addLayout(angle_layout)
        layout.addLayout(perf_layout)
        layout.addLayout(color_layout)
        layout.addWidget(self.general_beta_features)
        layout.addStretch()
        self.general_tab.setLayout(layout)

    def on_performance_changed(self, value):
        self.general_performance_label.setText(f"{value}%")
        self.DAEDALUS.preferences['general']["performance"] = value

    def init_airfoil_tab(self):
        layout = QVBoxLayout()
        color_layout = QHBoxLayout()

        viewport_text = QLabel("Viewport:")
        viewport_text.setToolTip("")

        # ComboBox for units
        color_text = QLabel("Viewport color:")
        self.a_color_combo_box = QComboBox()
        self.a_color_combo_box.addItems(["Bright", "Dark", "Blueprint", "Greenprint"])
        self.a_color_combo_box.setCurrentText(self.DAEDALUS.preferences['airfoil_designer']['viewport'].get("color_scheme", "Bright"))

        self.a_viewport_show_grid = QCheckBox("Show grid")
        self.a_viewport_show_grid.setChecked(self.DAEDALUS.preferences['airfoil_designer']['viewport']['grid']['show'])

        self.a_viewport_show_ruller = QCheckBox("Show ruler")
        self.a_viewport_show_ruller.setChecked(self.DAEDALUS.preferences['airfoil_designer']['viewport']['ruler']['show'])

        airfoil_text = QLabel("Airfoil:")
        airfoil_text.setToolTip("")

        self.airfoil_show_control_points = QCheckBox("Show control points")
        self.airfoil_show_control_points.setChecked(self.DAEDALUS.preferences['airfoil_designer']['airfoil']['control_points']['show'])
        self.airfoil_show_construction = QCheckBox("Show construction")
        self.airfoil_show_construction.setChecked(self.DAEDALUS.preferences['airfoil_designer']['airfoil']['construction']['show'])
        self.airfoil_show_wireframe = QCheckBox("Show wireframe")
        self.airfoil_show_wireframe.setChecked(self.DAEDALUS.preferences['airfoil_designer']['airfoil']['wireframe']['show'])

        color_layout.addWidget(color_text)
        color_layout.addWidget(self.a_color_combo_box)

        layout.addWidget(viewport_text)
        layout.addLayout(color_layout)
        layout.addWidget(self.a_viewport_show_grid)
        layout.addWidget(self.a_viewport_show_ruller)

        layout.addWidget(airfoil_text)
        layout.addWidget(self.airfoil_show_control_points)
        layout.addWidget(self.airfoil_show_construction)
        layout.addWidget(self.airfoil_show_wireframe)

        layout.addStretch()
        self.airfoil_tab.setLayout(layout)

    def init_wing_tab(self):
        layout = QVBoxLayout()

        viewport_text = QLabel("Viewport:")
        viewport_text.setToolTip("")

        self.w_viewport_show_grid = QCheckBox("Show grid")
        self.w_viewport_show_grid.setChecked(self.DAEDALUS.preferences['wing_designer']['viewport']['grid']['show'])

        #self.viewport_show_ruller = QCheckBox("Show ruller")
        #self.viewport_show_ruller.setChecked(DAEDALUS.preferences['wing_designer']['viewport']['ruller']['show'])

        wing_text = QLabel("Wing:")
        wing_text.setToolTip("")

        self.wing_show_grid = QCheckBox("Show control points")
        self.wing_show_grid.setChecked(self.DAEDALUS.preferences['wing_designer']['wing']['grid']['show'])
        self.wing_show_wireframe = QCheckBox("Show construction")
        self.wing_show_wireframe.setChecked(self.DAEDALUS.preferences['wing_designer']['wing']['wireframe']['show'])
        self.wing_show_solid = QCheckBox("Show wireframe")
        self.wing_show_solid.setChecked(self.DAEDALUS.preferences['wing_designer']['wing']['solid']['show'])

        layout.addWidget(viewport_text)
        layout.addWidget(self.w_viewport_show_grid)
        #layout.addWidget(self.w_viewport_show_ruller)

        layout.addWidget(wing_text)
        layout.addWidget(self.wing_show_grid)
        layout.addWidget(self.wing_show_wireframe)
        layout.addWidget(self.wing_show_solid)

        layout.addStretch()
        self.wing_tab.setLayout(layout)

    def save_preferences(self):

        # --- GENERAL TAB --- #
        if self.length_combo_box.currentText() == 'meters':
            self.DAEDALUS.preferences['general']["units"]["length"] = 'm'
        if self.angle_combo_box.currentText() == 'radians':
            self.DAEDALUS.preferences['general']["units"]["angle"] = 'rad'

        self.DAEDALUS.preferences['general']["performance"] = self.general_performance_slider.value()
        self.DAEDALUS.preferences['general']["color_scheme"] = self.color_combo_box.currentText()
        self.DAEDALUS.preferences['general']["beta_features"] = self.general_beta_features.isChecked()

        # --- AIRFOIL DESIGNER TAB --- #
        self.DAEDALUS.preferences['airfoil_designer']["viewport"]["color_scheme"] = self.a_color_combo_box.currentText()
        self.DAEDALUS.preferences['airfoil_designer']["viewport"]["grid"]['show'] = self.a_viewport_show_grid.isChecked()
        self.DAEDALUS.preferences['airfoil_designer']["viewport"]["ruler"]['show'] = self.a_viewport_show_ruller.isChecked()

        self.DAEDALUS.preferences['airfoil_designer']["airfoil"]["control_points"]['show'] = self.airfoil_show_control_points.isChecked()
        self.DAEDALUS.preferences['airfoil_designer']["airfoil"]["construction"]['show'] = self.airfoil_show_construction.isChecked()
        self.DAEDALUS.preferences['airfoil_designer']["airfoil"]["wireframe"]['show'] = self.airfoil_show_wireframe.isChecked()

        # --- WING DESIGNER TAB --- #
        self.DAEDALUS.preferences['wing_designer']["viewport"]["grid"]['show'] = self.w_viewport_show_grid.isChecked()
        #DAEDALUS.preferences['wing_designer']["viewport"]["ruler"]['show'] = self.w_viewport_show_ruller.isChecked()

        self.DAEDALUS.preferences['wing_designer']["wing"]["grid"]['show'] = self.wing_show_grid.isChecked()
        self.DAEDALUS.preferences['wing_designer']["wing"]["wireframe"]['show'] = self.wing_show_wireframe.isChecked()
        self.DAEDALUS.preferences['wing_designer']["wing"]["solid"]['show'] = self.wing_show_solid.isChecked()

        self.accept()
        
        preferences = {}

        preferences['general'] = {
            "units":{
                "length": self.DAEDALUS.preferences['general']['units'].get("length", "m"),
                "angle": self.DAEDALUS.preferences['general']['units'].get("angle", "rad"),
            },
            "performance": self.general_performance_slider.value(),
            "color_scheme": self.DAEDALUS.preferences['general'].get('color_scheme', "Deadlus-light"),
            "beta_features": self.DAEDALUS.preferences['general'].get("beta_features", False),
        }

        preferences['airfoil_designer'] = {
            "viewport": {
                "color_scheme": self.DAEDALUS.preferences['airfoil_designer']['viewport'].get("color_scheme", "Bright"),
                "grid": {
                    "show": self.DAEDALUS.preferences['airfoil_designer']['viewport']['grid'].get("show", True)
                    },
                "ruler": {
                    "show": self.DAEDALUS.preferences['airfoil_designer']['viewport']['ruler'].get("show", True)
                    },
            },
            "airfoil": {
                "control_points": {
                    "show": self.DAEDALUS.preferences['airfoil_designer']['airfoil']['control_points'].get("show", True),
                    "color": self.DAEDALUS.preferences['airfoil_designer']['airfoil']['control_points'].get("color", True)
                    },
                "construction": {
                    "show": self.DAEDALUS.preferences['airfoil_designer']['airfoil']['construction'].get("show", True),
                    "color": self.DAEDALUS.preferences['airfoil_designer']['airfoil']['construction'].get("color", True)
                    },
                "wireframe": {
                    "show": self.DAEDALUS.preferences['airfoil_designer']['airfoil']['wireframe'].get("show", True),
                    "color": self.DAEDALUS.preferences['airfoil_designer']['airfoil']['wireframe'].get("color", True)
                    }
            }
        }
        preferences['wing_designer'] = {
            "viewport": {
                "grid": {
                    "show": self.DAEDALUS.preferences['wing_designer']['viewport']['grid'].get("show", True)
                    },
                #"ruler": DAEDALUS.preferences['airfoil_designer']['viewport']['ruler'].get("show", True),
            },
            "wing": {
                "grid":{
                    "show": self.DAEDALUS.preferences['wing_designer']['wing']['grid'].get("show", True)
                },
                "wireframe": {
                    "show": self.DAEDALUS.preferences['wing_designer']['wing']['wireframe'].get("show", True),
                    "color": self.DAEDALUS.preferences['wing_designer']['wing']['wireframe'].get("color", True)
                },
                "solid": {
                    "show": self.DAEDALUS.preferences['wing_designer']['wing']['solid'].get("show", True)
                }
            }
        }
 
        json_object = json.dumps(preferences, indent=1)

        with open(f"src/settings", "w") as outfile:
            outfile.write(json_object)
            self.logger.info(f"Saved file: settings")
        
        self.DAEDALUS.APP.setStyleSheet(self.DAEDALUS.buildStyleSheet())

# For testing the dialog independently
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = PreferencesWindow()
    if dlg.exec_():
        print("Preferences saved.")
    else:
        print("Cancelled.")