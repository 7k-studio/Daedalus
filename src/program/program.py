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

# Library imports
import re
import logging
from datetime import date
import json
import os

import webbrowser

from src.widgets.about import About


class Program:
    def __init__(self):
        
        # basic program info
        self.name = "Daedalus"
        self.version = "0.4.0-beta"
        self.copyright = "Copyright (C) 2026 Jakub Kamyk"

        # logger
        self.logger = logging.getLogger(self.__class__.__name__)

        # Program components
        self.APP = None
        self.MAIN_WINDOW = None
        self.PROJECT = None
        self.SPLASHSCREEN = None
        self.AIRFOILDESIGNER = None
        self.WINGDESIGNER = None

        # Settings
        self.color_scheme = {}
        self.AD_viewport_color = {
            'Bright': {
                'background': [250, 250, 250],
                'grid': [215,215,215],
                'minor_grid': [235,235,235],
                'ruler': [5,5,5],
                'text': [0,0,0]
            },
            'Dark': {
                'background': [25, 25, 25],
                'grid': [65,65,65],
                'minor_grid': [65,65,65],
                'ruler': [250,250,250],
                'text': [255,255,255]
            },
            'Blueprint': {
                'background': [0, 42, 100],
                'grid': [90,125,150],
                'minor_grid': [75,105,150],
                'ruler': [225,225,225],
                'text': [255,255,255]
            },
            'Greenprint': {
                'background': [0, 123, 139],
                'grid': [200,200,200],
                'minor_grid': [180,180,180],
                'ruler': [225,225,225],
                'text': [255,255,255]
            }
        }
        self.preferences = {
            'general': {
                "units": {
                    "length": "m",
                    "angle":  "rad"
                }, # Options: "meters / radians", (future: "milimeters / degrees", "feet / degrees")
                "performance": 50,  # Options: 10 - 100
                "color_scheme": "Daedalus-light",
                "beta_features": False,  # Enable beta features
            },
            'airfoil_designer': {
                "viewport":{
                    "color_scheme": "Bright",
                    "grid":{
                        "show": True
                    },
                    "ruler": {
                        "show": True
                    },
                },
                "airfoil": {
                    "control_points": {
                        "show": True,
                        "color": {
                            'le': [0.0, 0.0, 1.0],
                            'te': [1.0, 0.8, 0.2],
                            'ps': [0.0, 1.0, 0.0],
                            'ss': [1.0, 0.0, 0.0]
                        }
                    },
                    "construction": {
                        "show": True,
                        "color": {
                            'le': [0.0, 0.0, 1.0],
                            'te': [1.0, 0.8, 0.2],
                            'ps': [0.0, 1.0, 0.0],
                            'ss': [1.0, 0.0, 0.0]
                        }
                    },
                    "wireframe": {
                        "show": True,
                        "color": {
                            'le': [0.0, 0.0, 1.0],
                            'te': [1.0, 0.8, 0.2],
                            'ps': [0.0, 1.0, 0.0],
                            'ss': [1.0, 0.0, 0.0]
                        }
                    }
                }
            },
            'wing_designer': {
                "viewport": {
                    "grid": {
                        "show": True,
                    },
                    "ruller": {
                        "show": True,
                    }
                },
                "wing": {
                    "grid": {
                        "show": True
                    },
                    "wireframe": {
                        "show": True,
                        "color": {
                            'le': [0.0, 0.0, 1.0], 
                            'te': [1.0, 1.0, 0.0], 
                            'ps': [0.0, 1.0, 0.0], 
                            'ss': [1.0, 0.0, 0.0], 
                            'le_ps': [0.0, 1.0, 0.0], 
                            'le_ss': [1.0, 0.0, 0.0], 
                            'te_ps': [0.0, 1.0, 0.0], 
                            'te_ss': [1.0, 0.0, 0.0]},
                    },
                    "solid":{         
                        "show": True},
                }
            }
        }
        
        self.readPreferences()  # Load preferences from file
    
    def readPreferences(self):
        """Read preferences from a JSON file."""
        try:
            with open("src/settings", "r") as infile:
                loaded = json.load(infile)
                # Only update keys that exist in the default preferences
                for section in self.preferences:
                    if section in loaded and isinstance(loaded[section], dict):
                        self.preferences[section].update(loaded[section])
                self.logger.info("Preferences loaded successfully.")
        except FileNotFoundError:
            self.logger.warning("Preferences file not found. Using default settings.")
        except json.JSONDecodeError:
            self.logger.error("Decoding preferences file. Using default settings.")

    def parse_css_with_daedalus_style(self, css_file):
        """
        Parse CSS content and extract DaedalusStyle object.
        
        Returns:
            tuple: (daedalus_dict, clean_css)
        """
        # Look for the DaedalusStyle block
        pattern = r'DaedalusStyle\s*\{([^}]+)\}'
        match = re.search(pattern, css_file) # Find the DaedalusStyle block
        
        daedalus_dict = {}
        clean_css = css_file

        if match:
            # Extract the content inside the braces
            style_content = match.group(1)

            # Parse key-value pairs
            for line in style_content.strip().split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.rstrip(';').split(':', 1)
                    key = key.strip()
                    # Clean up the value: strip whitespace and remove surrounding quotes
                    val = value.strip().strip('"').strip("'")
                    daedalus_dict[key] = val
            #Remove the DaedalusStyle block from CSS
            clean_css = re.sub(pattern, '', css_file).strip()

        return daedalus_dict, clean_css
            
    def buildStyleSheet(self):
        path_to_style = f"src/assets/styles/{self.preferences['general']['color_scheme']}.css"
        css_path = os.path.abspath(path_to_style)
        with open(css_path, 'r', encoding="utf-8") as f:
            StyleDaedalus, StylePyQt = self.parse_css_with_daedalus_style(f.read())
            self.color_scheme = StyleDaedalus
            self.logger.debug(self.color_scheme)
        
        return StylePyQt

    def showAboutDialog(self):
        About(self.version, self.copyright)
        
    def showUserManual(self):
        file_path = os.path.abspath("src/assets/user_manual/user_manual.html")
        webbrowser.open(f"file://{file_path}")
    
    def showRealiseNotes(self):
        webbrowser.open(f"https://github.com/7k-studio/Daedalus/releases")

    def showDedicatedWebpage(self):
        webbrowser.open(f"https://7k-studio.github.io/")

    # def showPreferences(self):
    #     """Open the preferences dialog."""
    #     self.logger.info("Open preferences window")
    #     from src.program.preferences import PreferencesWindow

    #     self.preferences_dialog = PreferencesWindow(self)
    #     self.preferences_dialog.show()