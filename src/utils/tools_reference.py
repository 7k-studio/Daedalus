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
import logging
import numpy as np
from scipy.interpolate import interp1d
import json
from src.obj.class_airfoil import Airfoil, SeligAirfoil, Airfoil_030ddls
# from src.program import DAEDALUS  # Import from globals.py

logger = logging.getLogger(__name__)

def load_xy_points_as_reference(file):
    """Load airfoil coordinates from a file and return upper and lower points."""
    AirfoilCoord = []
    logger.info("Loading airfoil from database...")
    try:
        is_name_set = False
        with open(file) as file:
            for line in file:
                try:
                    x, y = map(float, line.split()) # split X and Y values into 
                    AirfoilCoord.append([x,y])
                except ValueError: # skip lines that dont contain numeric data
                    if is_name_set == False:
                        if isinstance(line, str):
                            airfoil_name = line.replace("\n", '', 1)
                            airfoil_name = " ".join(line.split())
                            is_name_set = True
                    continue
    except FileNotFoundError:
        logger.error("No file found!")
        pass
            
    np.array(AirfoilCoord)
    logger.info("Chosen airfoils data read sucessfully!")
    
    airfoil = SeligAirfoil()
    #airfoil.full_curve = np.vstack([UP_points, DW_points])
    airfoil.curve = AirfoilCoord
    airfoil.name = airfoil_name
    logger.info(f"Finished loading {airfoil.name} in selig format")
    
    return airfoil

def interpolate_reference(reference, spline_points):
    """Interpolate reference points to match the number of spline points"""
    ref_length = len(reference[0])
    ref_spline_length = len(spline_points[0])
    interpolator_x = interp1d(np.linspace(0, 1, ref_length), reference[0], kind='linear')
    interpolator_y = interp1d(np.linspace(0, 1, ref_length), reference[1], kind='linear')
    new_x = interpolator_x(np.linspace(0, 1, ref_spline_length))
    new_y = interpolator_y(np.linspace(0, 1, ref_spline_length))
    return np.array([new_x, new_y])

def load_ddls_as_reference(data, Program, filePath=""):
    """load the airfoil data from a JSON format file."""
    from  src.obj.class_airfoil import Airfoil
    
    airfoil = Airfoil(Program)
    logger.info("Loading airfoil using 0.4.X version importer...")

    # # Build main structure
    # airfoil = {
    #     "name": str(current_airfoil.name),
    #     "path": str(path if path else self.path),
    #     "format": str(current_airfoil.format),
    #     "info": {key: str(val) for key, val in current_airfoil.info.items()},
    #     "attrs": parse_from_attrs(getattr(current_airfoil, "attrs", {})),
    #     "params": parse_from_params(getattr(current_airfoil, "params", {})),
    #     "stats": parse_from_params(getattr(current_airfoil, "stats", {})),
    # }

    # for section_name in ["LE", "TE", "PS", "SS"]:
    #     section = getattr(current_airfoil, section_name, None)

    #     if section:
    #         sec_attrs  = parse_from_attrs(getattr(section, "attrs", {}))
    #         sec_params = parse_from_params(getattr(section, "params", {}))
    #         sec_stats  = parse_from_params(getattr(section, "stats", {}))
    #     else:
    #         sec_attrs, sec_params, sec_stats = {}, {}, {}

    #     airfoil[section_name] = {
    #         "attrs":  sec_attrs,
    #         "params": sec_params,
    #         "stats":  sec_stats
    #     }
    

    if data:
        try:
            airfoil_params = data["params"]
            airfoil_params_le = data["LE"]["params"]
            airfoil_params_te = data["TE"]["params"]
            airfoil_params_ps = data["PS"]["params"]
            airfoil_params_ss = data["SS"]["params"]
            airfoil_attrs = data["attrs"]
            airfoil_attrs_le = data["LE"]["attrs"]
            airfoil_attrs_te = data["TE"]["attrs"]
            airfoil_attrs_ps = data["PS"]["attrs"]
            airfoil_attrs_ss = data["SS"]["attrs"]
            
            
        except KeyError as e:
            logger.error(f"Missing key in ARF data - {e}")
            logger.warning("File may not load properly or is not compatible with DAEDALUS")
            return None

        # try:
        airfoil.name = data['name']
        airfoil.path = filePath

        airfoil.info = {
            "creation_date":     data["info"].get("creation_date"),
            "modification_date": data["info"].get("modification_date"),
            "description":       data["info"].get("description", "")
        }

        # Set parameters in Airfoil.attrs dictionary
        for key in []:
            airfoil.params[key].value = float(airfoil_attrs[key].get('value', None))

        for key in ["type"]:
            print(airfoil_attrs)
            print(airfoil_attrs_le)
            airfoil.LE.attrs[key].value = airfoil_attrs_le[key].get('value', None)
            airfoil.TE.attrs[key].value = airfoil_attrs_te[key].get('value', None)
            airfoil.PS.attrs[key].value = airfoil_attrs_ps[key].get('value', None)
            airfoil.SS.attrs[key].value = airfoil_attrs_ss[key].get('value', None)

        # Set parameters in Airfoil.params dictionary
        for key in ["origin_X", "origin_Y", "stretch", "incline", "LE_thickness", "LE_angle", "TE_thickness", "TE_angle"]:
            airfoil.params[key].value = float(airfoil_params[key].get('value', 0.0))

        for key in ["ps_tan", "ps_slope", "ps_curv", "ss_tan", "ss_slope", "ss_curv"]:
            airfoil.LE.params[key].value = float(airfoil_params_le[key].get('value', 0.0))
            airfoil.TE.params[key].value = float(airfoil_params_te[key].get('value', 0.0))

        for key in ["fwd_wedge", "fwd_tan", "fwd_slope", "fwd_curv", "rwd_wedge", "rwd_tan", "rwd_slope", "rwd_curv"]:
            airfoil.PS.params[key].value = float(airfoil_params_ps[key].get('value', 0.0))
            airfoil.SS.params[key].value = float(airfoil_params_ss[key].get('value', 0.0))
            
        # except KeyError as e:
        #     logger.error(f"Missing key in ARF data - {e}")
        #     return None
        
        logger.info(f"Airfoil '{airfoil.name}' loaded successfully!")

        airfoil.update()

        return airfoil

def load_from_ddls_010(data, filePath=""):
    """load the airfoil data from a JSON format file."""
    is_version_different =  False
    error_count = 0

    Airfoil = objects2D.Airfoil()

    if data:

        try:
            # Set parameters in Airfoil.params dictionary
            Airfoil.params = {
                "chord": objects2D["chord"],
                "origin_X": objects2D["origin_X"],
                "origin_Y": objects2D["origin_Y"],
                "le_thickness": objects2D["le_thickness"],
                "le_depth": objects2D["le_depth"],
                "le_offset": objects2D["le_offset"],
                "le_angle": objects2D["le_angle"],
                "te_thickness": objects2D["te_thickness"],
                "te_depth": objects2D["te_depth"],
                "te_offset": objects2D["te_offset"],
                "te_angle": objects2D["te_angle"],
                "ps_fwd_angle": objects2D["ps_fwd_angle"],
                "ps_rwd_angle": objects2D["ps_rwd_angle"],
                "ps_fwd_accel": objects2D["ps_fwd_accel"],
                "ps_rwd_accel": objects2D["ps_rwd_accel"],
                "ss_fwd_angle": objects2D["ss_fwd_angle"],
                "ss_rwd_angle": objects2D["ss_rwd_angle"],
                "ss_fwd_accel": objects2D["ss_fwd_accel"],
                "ss_rwd_accel": objects2D["ss_rwd_accel"]
            }
            Airfoil.infos = {
                "name": objects2D["infos"]["name"],
                "creation_date": objects2D["infos"]["creation_date"],
                "modification_date": objects2D["infos"]["modification_date"],
                "description": objects2D["infos"]["description"]
            }
        except KeyError as e:
            logger.error(f"ERROR: Missing key in ARF data - {e}")
            return None

        Airfoil.update()

        logger.debug(Airfoil)
        logger.info(f"Airfoil '{Airfoil.infos['name']}' loaded successfully!")

        return Airfoil, error_count
    
def load_ddls_030_as_reference(data, Program, filePath=""):
    """load the airfoil data from a JSON format file."""

    Airfoil = Airfoil_030ddls(Program)

    if not data:
        return

    try:
        airfoil_data = data["airfoil"]
        airfoil_params = airfoil_data["params"]
        airfoil_infos   = airfoil_data["infos"]
    except KeyError as e:
        logger.error(f"Missing key in ARF data - {e}")
        logger.warning("File may not load properly or is not compatible with DAEDALUS")
        return None

    try:
        # Set parameters in Airfoil.params dictionary
        Airfoil.params = {
            "chord":        float(airfoil_params["chord"]),
            "origin_X":     float(airfoil_params["origin_X"]),
            "origin_Y":     float(airfoil_params["origin_Y"]),
            "le_thickness": float(airfoil_params["le_thickness"]),
            "le_depth":     float(airfoil_params["le_depth"]),
            "le_offset":    float(airfoil_params["le_offset"]),
            "le_angle":     float(airfoil_params["le_angle"]),
            "te_thickness": float(airfoil_params["te_thickness"]),
            "te_depth":     float(airfoil_params["te_depth"]),
            "te_offset":    float(airfoil_params["te_offset"]),
            "te_angle":     float(airfoil_params["te_angle"]),
            "ps_fwd_angle": float(airfoil_params["ps_fwd_angle"]),
            "ps_rwd_angle": float(airfoil_params["ps_rwd_angle"]),
            "ps_fwd_accel": float(airfoil_params["ps_fwd_accel"]),
            "ps_rwd_accel": float(airfoil_params["ps_rwd_accel"]),
            "ss_fwd_angle": float(airfoil_params["ss_fwd_angle"]),
            "ss_rwd_angle": float(airfoil_params["ss_rwd_angle"]),
            "ss_fwd_accel": float(airfoil_params["ss_fwd_accel"]),
            "ss_rwd_accel": float(airfoil_params["ss_rwd_accel"])
        }
        Airfoil.info = {    
            "creation_date":     airfoil_infos["creation_date"],
            "modification_date": airfoil_infos["modification_date"],
            "description":       airfoil_infos["description"]
        }
        Airfoil.name = airfoil_infos["name"]
    except KeyError as e:
        logger.error(f"Missing key in ARF data - {e}")
        return None

    Airfoil.update()

    return Airfoil

def flip_airfoil_horizontally(airfoil):
    """Flip the airfoil horizontally."""
    flipped_airfoil = objects2D.Airfoil()
    flipped_airfoil.info = airfoil.info.copy()
    flipped_airfoil.params = airfoil.params.copy()

    flipped_airfoil.params['chord'] = airfoil.params['chord']
    flipped_airfoil.params['origin_X'] = airfoil.params['origin_X']
    flipped_airfoil.params['origin_Y'] = airfoil.params['origin_Y']
    flipped_airfoil.params['le_thickness'] = airfoil.params['le_thickness']
    flipped_airfoil.params['le_depth'] = airfoil.params['le_depth']
    flipped_airfoil.params['le_offset'] = -airfoil.params['le_offset']
    flipped_airfoil.params['le_angle'] = -airfoil.params['le_angle']
    flipped_airfoil.params['te_thickness'] = airfoil.params['te_thickness']
    flipped_airfoil.params['te_depth'] = airfoil.params['te_depth']
    flipped_airfoil.params['te_offset'] = -airfoil.params['te_offset']
    flipped_airfoil.params['te_angle'] = -airfoil.params['te_angle']
    flipped_airfoil.params['ps_fwd_angle'] = -airfoil.params['ss_fwd_angle']
    flipped_airfoil.params['ps_rwd_angle'] = -airfoil.params['ss_rwd_angle']
    flipped_airfoil.params['ps_fwd_accel'] = airfoil.params['ss_fwd_accel']
    flipped_airfoil.params['ps_rwd_accel'] = airfoil.params['ss_rwd_accel']
    flipped_airfoil.params['ss_fwd_angle'] = -airfoil.params['ps_fwd_angle']
    flipped_airfoil.params['ss_rwd_angle'] = -airfoil.params['ps_rwd_angle']
    flipped_airfoil.params['ss_fwd_accel'] = airfoil.params['ps_fwd_accel']
    flipped_airfoil.params['ss_rwd_accel'] = airfoil.params['ps_rwd_accel']

    return flipped_airfoil