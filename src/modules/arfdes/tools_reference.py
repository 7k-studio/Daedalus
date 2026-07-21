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
from src.obj.class_airfoil import SeligAirfoil
# from src.program import DAEDALUS  # Import from globals.py

logger = logging.getLogger(__name__)

def load_selig_reference(file):
    """Load airfoil coordinates from a file and return upper and lower points."""
    AirfoilCoord = []
    UP_points = []
    DW_points = []
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
    
    i=0
    while AirfoilCoord[i][1] >= 0:
        UP_points.append(AirfoilCoord[i])
        i=i+1

    i=len(UP_points)-1
    while i < len(AirfoilCoord):
        DW_points.append(AirfoilCoord[i])
        i=i+1
    
    UP_points = np.array(UP_points)
    UP_points = UP_points[::-1, :]
    UP_points = UP_points.T
    
    DW_points = np.array(DW_points).T

    logger.debug(UP_points)
    logger.debug(DW_points)
    
    airfoil = SeligAirfoil()
    #airfoil.full_curve = np.vstack([UP_points, DW_points])
    airfoil.top_curve = UP_points
    airfoil.dwn_curve = DW_points
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

def load_json_reference(fileName):
    """load the airfoil data from a JSON format file."""
    error_count = 0

    if fileName:
        try:
            with open(f"{fileName}", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            logger.error("File not found!")
        except json.JSONDecodeError:
            logger.error("During decoding JSON!")

    if data:
        logger.debug("JSON decoded and data loaded to variable")
        try:
            airfoil_version = data["program version"]
        except KeyError as e:
            logger.error(f"Missing key in ARF data - {e}")
            logger.warning("File may not load properly or is not compatible with DAEDALUS")
            return None
        
        if airfoil_version:
            airfoil_version = airfoil_version.split("-")[0].split(".")
            program_version = DAEDALUS.program_version
            program_version = program_version.split("-")[0].split(".")

            if program_version[1] != airfoil_version[1] or program_version[0] != airfoil_version[0]:
                logger.warning("Current program version is different from the saved airfoil version. Import may not be compatible.")
                if airfoil_version[1] == 1:
                    logger.info("Trying to load using 0.1.X version")
                    airfoil, error_count = load_from_ddls_010(data)
            else:
                logger.info("Trying to load using 0.3.X version")
                airfoil, error_count = load_from_ddls_030(data)

        logger.debug(airfoil)

        self.PROJECT.reference_airfoils.append(airfoil)

def load_from_ddls_010(data):
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
    
def load_from_ddls_030(data):
    """load the airfoil data from a JSON format file."""
    is_version_different =  False
    error_count = 0

    Airfoil = objects2D.Airfoil()

    if data:
        try:
            airfoil_version = data["program version"]
            airfoil_data = data["airfoil"]
            airfoil_params = airfoil_data["params"]
            airfoil_infos   = airfoil_data["infos"]
        except KeyError as e:
            logger.error(f"Missing key in ARF data - {e}")
            logger.warning("File may not load properly or is not compatible with DAEDALUS")
            return None
        
        if airfoil_version:
            airfoil_version = airfoil_version.split("-")[0].split(".")
            program_version = DAEDALUS.program_version
            program_version = program_version.split("-")[0].split(".")

            if program_version[1] != airfoil_version[1] or program_version[0] != airfoil_version[0]:
                logger.warning("Current program version is different from the saved airfoil version. Import may not be compatible.")
                is_version_different = True

        try:
            # Set parameters in Airfoil.params dictionary
            Airfoil.params = {
                "chord":        airfoil_params["chord"],
                "origin_X":     airfoil_params["origin_X"],
                "origin_Y":     airfoil_params["origin_Y"],
                "le_thickness": airfoil_params["le_thickness"],
                "le_depth":     airfoil_params["le_depth"],
                "le_offset":    airfoil_params["le_offset"],
                "le_angle":     airfoil_params["le_angle"],
                "te_thickness": airfoil_params["te_thickness"],
                "te_depth":     airfoil_params["te_depth"],
                "te_offset":    airfoil_params["te_offset"],
                "te_angle":     airfoil_params["te_angle"],
                "ps_fwd_angle": airfoil_params["ps_fwd_angle"],
                "ps_rwd_angle": airfoil_params["ps_rwd_angle"],
                "ps_fwd_accel": airfoil_params["ps_fwd_accel"],
                "ps_rwd_accel": airfoil_params["ps_rwd_accel"],
                "ss_fwd_angle": airfoil_params["ss_fwd_angle"],
                "ss_rwd_angle": airfoil_params["ss_rwd_angle"],
                "ss_fwd_accel": airfoil_params["ss_fwd_accel"],
                "ss_rwd_accel": airfoil_params["ss_rwd_accel"]
            }
            Airfoil.info = {
                "name":              airfoil_infos["name"],
                "creation_date":     airfoil_infos["creation_date"],
                "modification_date": airfoil_infos["modification_date"],
                "description":       airfoil_infos["description"]
            }
        except KeyError as e:
            logger.error(f"Missing key in ARF data - {e}")
            return None
        
        if is_version_different == True:
            logger.info(f"Airfoil '{Airfoil.info['name']}' loaded but should be checked!")
            error_count += 1
        else:
            logger.info(f"Airfoil '{Airfoil.info['name']}' loaded successfully!")

        Airfoil.update()

        return Airfoil, error_count

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