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
import logging
import json

import os
import datetime

# In-Program imports
# import src.obj.objects3D as objects3D
from src.modules.arfdes.tools_airfoils import load_airfoil_from_json, Reference_load
from src.utils.tools_program import convert_ndarray_to_list, convert_list_to_ndarray, parse_from_params, parse_from_attrs

class Project:
    def __init__(self, program=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.name = None
        self.creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.description = "Project description"
        self.path = None  # Path to the project directory

        self.unit = None
        
        self.airfoils = []
        self.nominal_airfoils = []
        self.reference_airfoils = []

        self.components = []
        self.nominal_components = []

    def new(self):
        """Create a new project."""
        self.logger.info("Creating new project...")
        
        self.name = None
        self.creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.description = "New project created"
        self.path = None  # Set the path to the project directory

        self.components.clear()
        self.airfoils.clear()

    def save(self):
        if self.name != None and self.path is None:
            raise ValueError("Cannot save: 'name' and/or 'path' must be defined!")

        self.modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        txt = self._prep_json_data()
        self.logger.debug(txt)

        self.logger.info(f"Saved file: {self.path}")

    def save_as(self, filePath):
        
        if filePath:
            self.name = os.path.basename(filePath).split('.')[0]
            self.path = filePath

            self.modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            txt = self._prep_json_data()
            self.logger.debug(txt)

            self.logger.info(f"Saved file as: {self.name} to location: {self.path}")

    def open(self, fileName):
        from src.obj.class_airfoil import Airfoil
        from src.obj.surfaces import Component, Wing, Segment  # Import the templates
        
        if fileName:
            warning_count = 0

            self.logger.info(f"Open archive project: {fileName}")
            # Open the JSON file directly (as saved by saveProject)
            with open(fileName, "r") as f:
                data = json.load(f)

            # Convert lists back to numpy arrays if needed
            data = convert_list_to_ndarray(data)

            if "Program" in data:
                if data["Program"].get("program version", self.DAEDALUS.version):
                    file_version = data["Program"].get("program version", self.DAEDALUS.version)
                    file_version = file_version.split("-")[0].split(".")
                    program_version = self.DAEDALUS.version
                    program_version = program_version.split("-")[0].split(".")
                    if program_version[1] != file_version[1] or program_version[0] != file_version[0]:
                        self.logger.warning("Current program version is different from the saved version. Some features may not work as expected. \nMissing parameters will take default values.")
                        warning_count += 1

            # Restore PROJECT info
            if "Project" in data:
                self.logger.debug("Loading data")
                proj = data["Project"]
                self.name = proj.get("project name", self.name)
                self.creation_date = proj.get("creation date", self.creation_date)
                self.description = proj.get("project description", self.description)
                self.path = proj.get("project path", self.path)
                self.project_components.clear()
                self.project_airfoils.clear()

                # Load airfoils from in-memory JSON (not from files)
                self.logger.debug("Loading airfoil entires...")
                airfoil_entries = proj.get("project airfoils", [])
                for airfoil_entry in airfoil_entries:
                    airfoil_data = airfoil_entry["data"]
                    arf_obj = load_airfoil_from_json(airfoil_data)
                    self._ensure_unique_name(arf_obj)  # Ensure unique name in case of conflicts
                    self.project_airfoils.append(arf_obj)
                    self.logger.debug(f"Found airfoil: {arf_obj.name}")

                # Load components using templates
                self.logger.debug("Loading components entires...")
                for comp_data in proj.get("project components", []):
                    component = Component()
                    # Merge infos and params with defaults
                    component.infos = {**Component().infos, **comp_data.get("infos", {})}
                    component.params = {**Component().params, **comp_data.get("params", {})}
                    component.wings = []
                    for wing_data in comp_data.get("wings", []):
                        wing = Wing()
                        wing.infos = {**Wing().infos, **wing_data.get("infos", {})}
                        wing.params = {**Wing().params, **wing_data.get("params", {})}
                        wing.segments = []
                        for seg_data in wing_data.get("segments", []):
                            segment = Segment()
                            segment.infos = {**Segment().infos, **seg_data.get("infos", {})}
                            segment.anchor = seg_data.get("anchor", Segment().anchor)
                            segment.params = {**Segment().params, **seg_data.get("params", {})}

                            # Set airfoil based on airfoil name
                            airfoil_ref = seg_data.get("airfoil", "")
                            segment.airfoil = next((a for a in self.project_airfoils if a.name == airfoil_ref), self.project_airfoils[0] if self.project_airfoils else None)
                            wing.segments.append(segment)
                        component.wings.append(wing)
                    self.project_components.append(component)

            airf_no = 0
            comp_no = 0
            wing_no = 0
            segm_no = 0
            objects_updated = 0

            for airfoil in self.project_airfoils:
                airf_no += 1
            for component in self.project_components:
                for wing in component.wings:
                    for segment in wing.segments:
                        segm_no += 1
                    wing_no += 1
                comp_no += 1

            objects_to_update = comp_no + wing_no + segm_no + airf_no
            report = [
            ("Objects found inside saved file:\n"),
            (f"----------------------"),
            (f"|   LOADED OBJECTS   |"),
            (f"----------------------"),
            (f"|   Components:   {comp_no}  |"),
            (f"|   Wings:        {wing_no}  |"),
            (f"|   Segments:     {segm_no}  |"),
            (f"|   Airfoils:     {airf_no}  |"),
            (f"----------------------"),
            (f"|  ALL OBJECTS:   {objects_to_update}  |"),
            (f"----------------------")]

            self.logger.info(f"Rebuilidng geometries...")

            for airfoil in self.project_airfoils:
                airfoil.update()
                objects_updated += 1
                self.logger.debug(f"{objects_updated} / {objects_to_update}")
            for c in range(len(self.project_components)):
                component = self.project_components[c]
                for w in range(len(component.wings)):
                    wing = component.wings[w]
                    for s in range(len(wing.segments)):
                        segment = wing.segments[s]
                        segment.airfoil.update()
                        segment.update(c, w, s)
                        objects_updated += 1
                        self.logger.debug(f"{objects_updated} / {objects_to_update}")
                    wing.update(c, w, s)
                    objects_updated += 1
                    self.logger.debug(f"{objects_updated} / {objects_to_update}")
                component.update(c, w, s)
                objects_updated += 1
                self.logger.debug(f"{objects_updated} / {objects_to_update}")
            self.logger.debug("Update finished!")

            if warning_count == 0:
                report.insert(0, (f"Project archive '{self.name}' successfully loaded")) 
            else: 
                report.insert(0, (f"Project archive '{self.name}' loaded with ({warning_count}) warnings, check might be necessary!"))
                
            self.logger.info("\n".join(report))

            return True
        
    def set_description(self, new_text):
        """Update the description of the project."""
        self.logger.info("Updating description of the project...")
        self.description = new_text
        # This is also the perfect place to set an "unsaved changes" flag if you have one!
        # self.is_modified = True

    def _ensure_unique_airfoil_name(self, airfoil):
        """Ensure the airfoil has a unique name by appending a number if necessary."""
        base_name = airfoil.name
        counter = 1
        existing_names = [a.name for a in self.airfoils if a is not airfoil]
        while airfoil.name in existing_names:
            airfoil.name = f"{base_name}.{str(counter).zfill(3)}"
            counter += 1
    
    def _ensure_unique_object_name(self, object):
        """Ensure the airfoil has a unique name by appending a number if necessary."""
        base_name = object.name
        counter = 1
        existing_names = []

        for component in self.components:
            existing_names.append(component.name)
            for wing in component.wings:
                existing_names.append(wing.name)
                for segment in wing.segments:
                    existing_names.append(segment.name)
                    
        while object.name in existing_names:
            object.name = f"{base_name}.{str(counter).zfill(3)}"
            counter += 1
    
    def _prep_json_data(self):

        designed_components = []

        # Collect all airfoils in one list with names
        airfoil_entries = []
        for arf_obj in self.airfoils:

            airfoil_data = self._serialize_airfoil_to_json(self.path, arf_obj)  # serialized JSON string
            airfoil_entries.append(airfoil_data)

        component_entries = self._serialize_components_to_json()

        Daedalus = {
            "program name": self.DAEDALUS.name,
            "program version": self.DAEDALUS.version,
        }

        Project = {
            "name": self.name,
            "path": self.path,
            "creation date": self.creation_date,
            "modification date": self.modification_date,
            "description": self.description,
            "components": component_entries,
            "airfoils": airfoil_entries
        }

        data = {
            "Program": Daedalus,
            "Project": Project
        }

        # Convert numpy arrays to lists before saving
        data = convert_ndarray_to_list(data)

        # Save into one .ddls file
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

        return 'Project archive successfully saved'

    def _serialize_airfoil_to_json(self, path=None, current_airfoil=None):
        """Save the airfoil data to a JSON format file."""
        
        # Get main airfoil params (origin_X, stretch etc.)
        airfoil_params = parse_from_params(current_airfoil.params)
        airfoil_attrs = parse_from_attrs(current_airfoil.attrs)
        airfoil_stats = parse_from_params(current_airfoil.stats)

        # Dynamically check childs of an airfoil (LE, TE, PS, SS)
        for section_name in ["LE", "TE", "PS", "SS"]:
            section = getattr(current_airfoil, section_name, None)
            if section and hasattr(section, "params"):
                airfoil_params[section_name] = parse_from_params(section.params)
            elif section and hasattr(section, "attrs"):
                airfoil_attrs[section_name] = parse_from_params(section.attrs)

        # Build main structure

        airfoil = {
            "name": str(current_airfoil.name),
            "path": str(path if path else self.path),
            "format": str(current_airfoil.format),
            "info": {key: str(val) for key, val in current_airfoil.info.items()},
            "attrs": airfoil_attrs,
            "params": airfoil_params,
            "stats": airfoil_stats
        }
    
        # json_object = json.dumps(airfoils, indent=1)

        return airfoil
    
    def _serialize_components_to_json(self):
        """Save the airfoil data to a JSON format file."""
        # Build components → wings → segments
        designed_components = []
        for component in self.components:
            designed_wings = []
            for wing in component.wings:
                designed_segments = []
                for segment in wing.segments:

                    # Get main airfoil params (origin_X, stretch etc.)
                    segment_attrs = parse_from_attrs(segment.attrs)
                    segment_params = parse_from_params(segment.params)
                    segment_stats = parse_from_params(segment.stats)

                    # Dynamically check childs of an airfoil (LE, TE, PS, SS)
                    for section_name in ["LE", "TE", "PS", "SS"]:
                        section = getattr(segment, section_name, None)
                        if section and hasattr(section, "params"):
                            segment_params[section_name] = parse_from_params(section.params)
                        elif section and hasattr(section, "attrs"):
                            segment_attrs[section_name] = parse_from_params(section.attrs)
                        elif section and hasattr(section, "stats"):
                            segment_stats[section_name] = parse_from_params(section.attrs)
                    
                    segment_data = {
                        "name": str(segment.name),
                        "info": {key: str(val) for key, val in segment.info.items()},
                        "attrs": segment_attrs,
                        "params": segment_params,
                        "stats": segment_stats
                    }

                    designed_segments.append(segment_data)

                wing_attrs = parse_from_attrs(wing.attrs)
                wing_params = parse_from_params(wing.params)
                wing_stats = parse_from_params(wing.stats)

                wing_data = {
                    "name": str(wing.name),
                    "info": {key: str(val) for key, val in wing.info.items()},
                    "attrs": wing_attrs,
                    "params": wing_params,
                    "stats": wing_stats,
                    "segments": designed_segments
                }
                designed_wings.append(wing_data)

            component_attrs = parse_from_attrs(component.attrs)
            component_params = parse_from_params(component.params)
            component_stats = parse_from_params(component.stats)

            component_data = {
                "name": str(component.name),
                "info": {key: str(val) for key, val in component.info.items()},
                "attrs": component_attrs,
                "params": component_params,
                "stats": component_stats,
                "wings": designed_wings
            }
            designed_components.append(component_data)
        
        # json_object = json.dumps(airfoils, indent=1)

        return designed_components