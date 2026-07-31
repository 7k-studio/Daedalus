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
from src.utils.tools_airfoil import load_ddls_airfoil, load_ddls_airfoil_030, Reference_load
from src.utils.tools_program import convert_ndarray_to_list, convert_list_to_ndarray, parse_from_params, parse_from_attrs, decode_json, get_archive_version, update_attrs_dict, update_params_dict

class Project:
    def __init__(self, program=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.PROGRAM = program
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

    def open(self, filePath):
        
        if not filePath:
            self.logger.error("File path not specified or incorrect!")
            return

        data = decode_json(filePath)
        file_version = get_archive_version(data)

        try:
            project_data = data["Project"]
        except KeyError as e:
            self.logger.error(f"Missing key in ARF data - {e}")
            self.logger.warning("File may not load properly or is not compatible with DAEDALUS")
            return

        # Check compatibility
        self.logger.debug("Checking compatibility...")
        print(int(file_version[0]), int(file_version[1]))
        print(int(file_version[0]) == 0, int(file_version[1]) < 4)
        if int(file_version[0]) == 0 and int(file_version[1]) < 4:
            self.logger.warning("There were critical changes to airfoil definition. Program will try to recreate saved airfoil to latest format. Checing the appending results is advised!")
            # Load airfoils from in-memory JSON
            self.logger.info("Loading airfoil using legacy approach...")
            self._030_project_reader(data, self.PROGRAM, filePath)
        else:
            project_data = data["Project"]
            self._project_reader(project_data)
            
        self.logger.debug("Processing the data...")

    def _project_reader(self, project_data):
        from src.widgets.widget_progress import ProgressDialog
        from src.obj.param import Param, Attr, M, MM, IN, FT, DEG, RAD
        from src.obj.class_airfoil import Airfoil
        from src.obj.class_component import Component
        from src.obj.class_wing import Wing
        from src.obj.class_segment import Segment  # Import the templates

        # Słownik dostępnych jednostek w Twoim programie
        UNITS_MAP = {
            "m": M,
            "mm": MM,
            "in": IN,
            "ft": FT,
            "deg": DEG,
            "rad": RAD
        }

        airf_no = len(project_data.get("airfoils",[]))
        comp_no = 0
        wing_no = 0
        segm_no = 0
        objects_no = 0
        
        components_vec = project_data.get("components",[])
        for c in components_vec:
            wings_vec = c.get("wings",[])
            for w in wings_vec:
                segment_vec = w.get("segments",[])
                segm_no += len(segment_vec)
            wing_no += len(wings_vec)
        comp_no = len(components_vec)

        objects_no = comp_no + wing_no + segm_no

        self.progressWidget = ProgressDialog(title="Opening Project...")
        self.progressWidget.show()
        self.progressWidget.max_value = 2*objects_no+10
        self.progressWidget.set_progress(0, "Restoring project attributes...")

        # Restore PROJECT info
        self.name = project_data.get("name", self.name)
        self.path = project_data.get("path", self.path)
        self.creation_date = project_data.get("creation date", self.creation_date)
        self.description = project_data.get("description", self.description)
        self.components.clear()
        self.airfoils.clear()
     
        # Load airfoils from in-memory JSON
        self.progressWidget.set_progress(5, "Loading airfoil entires...")
        self.logger.debug("Loading airfoil entires...")
        try:
            airfoil_entries = project_data.get("airfoils", [])
            print(airfoil_entries)
            for airfoil_entry in airfoil_entries:
                arf_obj = load_ddls_airfoil(Airfoil(self.PROGRAM), airfoil_entry)
                if arf_obj:
                    self.logger.debug(f"Found airfoil: {arf_obj.name}")
                    # self.PROJECT._ensure_unique_airfoil_name(arf_obj)  # Ensure unique name
                    self.airfoils.append(arf_obj)
                    arf_obj.update()
                    self.progressWidget.increase_progress(1)

        except KeyError as e:
            self.logger.error(f"Missing key in ARF data - {e}")
            self.logger.warning("File may not load properly or is not compatible with DAEDALUS")
            self.progressWidget.close()
            return
        
        self.progressWidget.set_progress(30, "Loading components entires...")
        # Load components using templates
        self.logger.debug("Loading components entires...")
        for comp_data in project_data.get("components", []):
            component = Component(self.PROGRAM, self)
            component.name = comp_data.get("name","Component")
            component.info = {**component.info, **comp_data.get("info", {})}
            update_attrs_dict(component.attrs, comp_data.get("attrs", {}))
            update_params_dict(component.params, comp_data.get("params", {}), UNITS_MAP)
            component.wings = []
            for wing_data in comp_data.get("wings", []):
                wing = Wing(self.PROGRAM, self, component)
                wing.name = wing_data.get("name","Wing")
                wing.info = {**wing.info, **wing_data.get("info", {})}
                update_attrs_dict(wing.attrs, wing_data.get("attrs", {}))
                update_params_dict(wing.params, wing_data.get("params", {}), UNITS_MAP)
                wing.segments = []
                for seg_data in wing_data.get("segments", []):
                    segment = Segment(self.PROGRAM, self, wing)
                    segment.name = seg_data.get("name","Segment")
                    segment.info = {**segment.info, **seg_data.get("info", {})}
                    update_attrs_dict(segment.attrs, seg_data.get("attrs", {}), self.airfoils)
                    update_params_dict(segment.params, seg_data.get("params", {}), UNITS_MAP)

                    wing.segments.append(segment)
                    self.progressWidget.increase_progress(1, "Loaded segment...")
                component.wings.append(wing)
                self.progressWidget.increase_progress(1, "Loaded wing...")
            self.components.append(component)
            self.progressWidget.increase_progress(1, "Loaded component...")

        self.logger.info(f"Objects found inside saved file: ALL OBJECTS: {objects_no} | Components: {comp_no}, Wings: {wing_no}, Segments: {segm_no}, Airfoils: {airf_no}"),

        self.progressWidget.increase_progress(5, "Rebuilding geometries...")
        self.logger.info(f"Rebuilidng geometries...")

        for airfoil in self.airfoils:
            airfoil.update()
            self.progressWidget.increase_progress(1)
        for c in range(len(self.components)):
            component = self.components[c]
            for w in range(len(component.wings)):
                wing = component.wings[w]
                for s in range(len(wing.segments)):
                    segment = wing.segments[s]
                    segment.update()
                    self.progressWidget.increase_progress(1, "Updating segment...")
                wing.update()
                self.progressWidget.increase_progress(1, "Updating wing...")
            component.update()
            self.progressWidget.increase_progress(1, "Updating component...")

        self.progressWidget.set_progress(100, "Update finished!")
        self.logger.debug("Update finished!")

        self.logger.info(f"Project archive '{self.name}' successfully loaded")

        self.progressWidget.close()

    def _030_project_reader(self, program, project_data):
        # Restore PROJECT info
        self.name = project_data.get("project name", self.name)
        self.path = project_data.get("project path", self.path)
        self.creation_date = project_data.get("creation date", self.creation_date)
        self.description = project_data.get("project description", self.description)
        self.components.clear()
        self.airfoils.clear()

        # Load airfoils from in-memory JSON
        self.logger.debug("Loading airfoil entires...")
        airfoil_entries = project_data.get("project airfoils", [])
        for airfoil_entry in airfoil_entries:
            print(airfoil_entry)
            airfoil_data = airfoil_entry["data"]
            arf_obj = load_ddls_airfoil_040(airfoil_data)
            # self._ensure_unique_name(arf_obj)  # Ensure unique name in case of conflicts
            self.airfoils.append(arf_obj)
            self.logger.debug(f"Found airfoil: {arf_obj.name}")

        # Load components using templates
        self.logger.debug("Loading components entires...")
        for comp_data in project_data.get("project components", []):
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
                    segment.airfoil = next((a for a in self.airfoils if a.name == airfoil_ref), self.airfoils[0] if self.airfoils else None)
                    wing.segments.append(segment)
                component.wings.append(wing)
            self.components.append(component)

        airf_no = 0
        comp_no = 0
        wing_no = 0
        segm_no = 0
        objects_updated = 0

        for airfoil in self.airfoils:
            airf_no += 1
        for component in self.components:
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

        for airfoil in self.airfoils:
            airfoil.update()
            objects_updated += 1
            self.logger.debug(f"{objects_updated} / {objects_to_update}")
        for c in range(len(self.components)):
            component = self.components[c]
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

        report.insert(0, (f"Project archive '{self.name}' successfully loaded")) 
            
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
            "name": self.PROGRAM.name,
            "version": self.PROGRAM.version,
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

        # Build main structure
        airfoil = {
            "name": str(current_airfoil.name),
            "path": str(path if path else self.path),
            "format": str(current_airfoil.format),
            "info": {key: str(val) for key, val in current_airfoil.info.items()},
            "attrs": parse_from_attrs(getattr(current_airfoil, "attrs", {})),
            "params": parse_from_params(getattr(current_airfoil, "params", {})),
            "stats": parse_from_params(getattr(current_airfoil, "stats", {})),
        }

        for section_name in ["LE", "TE", "PS", "SS"]:
            section = getattr(current_airfoil, section_name, None)

            if section:
                sec_attrs  = parse_from_attrs(getattr(section, "attrs", {}))
                sec_params = parse_from_params(getattr(section, "params", {}))
                sec_stats  = parse_from_params(getattr(section, "stats", {}))
            else:
                sec_attrs, sec_params, sec_stats = {}, {}, {}

            airfoil[section_name] = {
                "attrs":  sec_attrs,
                "params": sec_params,
                "stats":  sec_stats
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