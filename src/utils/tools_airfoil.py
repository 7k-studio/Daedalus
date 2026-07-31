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
import math
from scipy.interpolate import splev, interp1d
from scipy.optimize import root_scalar
import json
import src.obj

from src.obj.class_airfoil import Airfoil

logger = logging.getLogger(__name__)

def SeligReference(file):
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

    #logger.debug(UP_points)
    #logger.debug(DW_points)
    
    airfoil = src.obj.objects2D.Airfoil_selig_format()
    #airfoil.full_curve = np.vstack([UP_points, DW_points])
    airfoil.top_curve = UP_points
    airfoil.dwn_curve = DW_points
    airfoil.info['name'] = airfoil_name
    logger.info(f"Finished loading {airfoil.info['name']} in selig format")
    
    return airfoil

def Reference_load(file):
    """Load airfoil coordinates from a file and return upper and lower points."""
    format = file.split('.')[1]
    airfoil = None
    
    if format =="arf":
        airfoil, _ = load_airfoil_from_json(file)
    else:
        airfoil = SeligReference(file)
    
    return airfoil

def CreateBSpline(const_points, force_resolution=None):

    l=len(const_points[0])

    t=np.linspace(0,1,l-2,endpoint=True)
    t=np.append([0,0,0],t)
    t=np.append(t,[1,1,1])

    tck=[t,[const_points[0],const_points[1]],3]
    
    f = int(DAEDALUS.preferences['general']['performance'])
    if force_resolution:
        f = force_resolution

    u3=np.linspace(0,1,(max(l*f/100,f)),endpoint=True)

    spline = splev(u3, tck)

    return spline

def interpolate_reference(reference, spline_points):
    """Interpolate reference points to match the number of spline points"""
    ref_length = len(reference[0])
    ref_spline_length = len(spline_points[0])
    interpolator_x = interp1d(np.linspace(0, 1, ref_length), reference[0], kind='linear')
    interpolator_y = interp1d(np.linspace(0, 1, ref_length), reference[1], kind='linear')
    new_x = interpolator_x(np.linspace(0, 1, ref_spline_length))
    new_y = interpolator_y(np.linspace(0, 1, ref_spline_length))
    return np.array([new_x, new_y])

def calculate_error(params, top_ref, dwn_ref):
    """Define the function to calculate error"""
    # Extract parameters
    chord, origin_X, origin_Y, le_thickness, le_depth, le_offset, le_angle, te_thickness, te_depth, te_offset, te_angle, \
        ps_fwd_angle, ps_rwd_angle, ps_fwd_accel, ps_rwd_accel, ss_fwd_angle, ss_rwd_angle, ss_fwd_accel, ss_rwd_accel = params

    le_angle = math.radians(le_angle)
    te_angle = math.radians(te_angle)
    ps_fwd_angle = math.radians(ps_fwd_angle)
    ps_rwd_angle = math.radians(ps_rwd_angle)
    ss_fwd_angle = math.radians(ss_fwd_angle)
    ss_rwd_angle = math.radians(ss_rwd_angle)

    # Leading edge control points
    p_le_start = [origin_X, origin_Y]
    a0 = math.tan(le_angle)
    a1 = math.tan(ps_fwd_angle)
    a2 = math.tan(ss_fwd_angle)
    b0 = p_le_start[1] - a0 * p_le_start[0]
    b1 = p_le_start[1] + le_thickness / 2 - a1 * (p_le_start[0] + le_depth)
    b2 = p_le_start[1] - le_thickness / 2 - a2 * (p_le_start[0] + le_depth)
    p_le_t = [(b1 - b0) / (a0 - a1), a0 * ((b1 - b0) / (a0 - a1)) + b0]
    p_le_d = [(b2 - b0) / (a0 - a2), a0 * ((b2 - b0) / (a0 - a2)) + b0]
    le_constr = np.vstack([p_le_d, p_le_start, p_le_t]).T

    # Trailing edge control points
    p_te_start = [origin_X + chord, origin_Y]
    a3 = math.tan(te_angle)
    a4 = math.tan(ps_rwd_angle)
    a5 = math.tan(ss_rwd_angle)
    b3 = p_te_start[1] - a3 * p_te_start[0]
    b4 = p_te_start[1] + te_thickness / 2 - a4 * (p_te_start[0] - te_depth)
    b5 = p_te_start[1] - te_thickness / 2 - a5 * (p_te_start[0] - te_depth)
    p_te_t = [(b4 - b3) / (a3 - a4), a3 * ((b4 - b3) / (a3 - a4)) + b3]
    p_te_d = [(b5 - b3) / (a3 - a5), a3 * ((b5 - b3) / (a3 - a5)) + b3]
    te_constr = np.vstack([p_te_d, p_te_start, p_te_t]).T

    # Create splines
    le_spline = CreateBSpline(le_constr)
    te_spline = CreateBSpline(te_constr)

    # Interpolate reference points to match spline length
    top_ref_interp = interpolate_reference(top_ref, le_spline)
    dwn_ref_interp = interpolate_reference(dwn_ref, te_spline)

    # Calculate error between splines and reference
    top_error = np.sum((le_spline[1] - top_ref_interp[1])**2 + (le_spline[0] - top_ref_interp[0])**2)
    bottom_error = np.sum((te_spline[1] - dwn_ref_interp[1])**2 + (te_spline[0] - dwn_ref_interp[0])**2)

    return top_error + bottom_error

def find_t_for_x(desired_x, tck):
    def equation(t):
        return splev(t, tck)[0] - desired_x  # x(t) - desired_x = 0

    result = root_scalar(equation, bracket=[0, 1], method='brentq')  # Solve for t
    if not result.converged:
        raise ValueError(f"Could not find t for X = {desired_x}")
    return result.root
   
def load_ddls_airfoil_030(data, program, filePath="Unknown"):
    """load the airfoil data from a JSON format file."""
    
    from  src.obj.class_airfoil import Airfoil

    airfoil = Airfoil(program)

    logger.info("Trying to load using 0.3.X version")

    try:
        airfoil_data = data["airfoil"]
        airfoil_params = airfoil_data["params"]
        airfoil_info   = airfoil_data["infos"]
    except KeyError as e:
        logger.error(f"Missing key in ARF data - {e}")
        logger.warning("File may not load properly or is not compatible with DAEDALUS")
        return None

    try:
        airfoil.name = airfoil_info['name']
        airfoil.path = filePath

        airfoil.info = {
            "creation_date":     airfoil_info["creation_date"],
            "modification_date": airfoil_info["modification_date"],
            "description":       airfoil_info["description"]
        }

        # Set parameters in Airfoil.params dictionary
        airfoil.params["origin_X"].value = float(airfoil_params["origin_X"])+float(airfoil_params["le_depth"])-float(airfoil_params["te_depth"])
        airfoil.params["origin_Y"].value = float(airfoil_params["origin_Y"])
        airfoil.params["stretch"].value = float(airfoil_params["chord"])-float(airfoil_params["le_offset"])-float(airfoil_params["te_offset"])-float(airfoil_params["le_depth"])-float(airfoil_params["te_depth"])
        airfoil.params["incline"].value = 0.0
        airfoil.params["LE_thickness"].value = float(airfoil_params["le_thickness"])
        airfoil.params["LE_angle"].value = float(airfoil_params["le_angle"])
        airfoil.params["TE_thickness"].value = float(airfoil_params["te_thickness"])
        airfoil.params["TE_angle"].value = float(airfoil_params["te_angle"])

        airfoil.LE.attrs["type"].value = "G1"

        airfoil.LE.params["ps_tan"].value = float(airfoil_params["le_depth"])
        airfoil.LE.params["ps_slope"].value = -30.0
        airfoil.LE.params["ps_curv"].value = float(airfoil_params["le_depth"])/2
        airfoil.LE.params["ss_tan"].value = float(airfoil_params["le_depth"])
        airfoil.LE.params["ss_slope"].value = 30.0
        airfoil.LE.params["ss_curv"].value = float(airfoil_params["le_depth"])/2

        airfoil.TE.attrs["type"].value = "G1"

        airfoil.TE.params["ps_tan"].value = float(airfoil_params["te_depth"])
        airfoil.TE.params["ps_slope"].value = -30.0
        airfoil.TE.params["ps_curv"].value = float(airfoil_params["te_depth"])/2
        airfoil.TE.params["ss_tan"].value = float(airfoil_params["te_depth"])
        airfoil.TE.params["ss_slope"].value = 30.0
        airfoil.TE.params["ss_curv"].value = float(airfoil_params["te_depth"])/2

        airfoil.PS.attrs["type"].value = "G1"

        airfoil.PS.params["fwd_wedge"].value = float(airfoil_params["ps_fwd_angle"])
        airfoil.PS.params["fwd_tan"].value = float(airfoil_params["ps_fwd_accel"])
        airfoil.PS.params["fwd_slope"].value = 0.0
        airfoil.PS.params["fwd_curv"].value = 0.10
        airfoil.PS.params["rwd_wedge"].value = -float(airfoil_params["ps_rwd_angle"])
        airfoil.PS.params["rwd_tan"].value = float(airfoil_params["ps_rwd_accel"])
        airfoil.PS.params["rwd_slope"].value = 0.0
        airfoil.PS.params["rwd_curv"].value = 0.10

        airfoil.SS.attrs["type"].value = "G1"
        
        airfoil.SS.params["fwd_wedge"].value = -float(airfoil_params["ss_fwd_angle"])
        airfoil.SS.params["fwd_tan"].value = float(airfoil_params["ss_fwd_accel"])
        airfoil.SS.params["fwd_slope"].value = 0.0
        airfoil.SS.params["fwd_curv"].value = 0.10
        airfoil.SS.params["rwd_wedge"].value = float(airfoil_params["ss_rwd_angle"])
        airfoil.SS.params["rwd_tan"].value = float(airfoil_params["ss_rwd_accel"])
        airfoil.SS.params["rwd_slope"].value = 0.0
        airfoil.SS.params["rwd_curv"].value = 0.10
        
    except KeyError as e:
        logger.error(f"Missing key in ARF data - {e}")
        return None

    return airfoil

def load_ddls_airfoil(airfoil_obj, airfoil_data, filePath=""):
    """load the airfoil data from a JSON format file."""
    from src.utils.tools_program import update_params_dict, update_attrs_dict
    from src.obj.param import M, MM, IN, FT, DEG, RAD

    # Słownik dostępnych jednostek w Twoim programie
    UNITS_MAP = {
        "m": M,
        "mm": MM,
        "in": IN,
        "ft": FT,
        "deg": DEG,
        "rad": RAD
    }
    
    if airfoil_data:

        try:
            airfoil_obj.name = airfoil_data['name']
            airfoil_obj.path = filePath
            airfoil_obj.info = {**airfoil_obj.info, **airfoil_data.get("info", {})}

            # Set parameters in Airfoil.attrs dictionary
            update_attrs_dict(airfoil_obj.attrs, airfoil_data.get("attrs", {}))
            update_params_dict(airfoil_obj.params, airfoil_data.get("params", {}), UNITS_MAP)

            for key in ['le', 'te', 'ps', 'ss']:
                segment = getattr(airfoil_obj, key.upper())
                update_attrs_dict(segment.attrs, airfoil_data[key.upper()].get("attrs", {}))
                update_params_dict(segment.params, airfoil_data[key.upper()].get("params", {}), UNITS_MAP)
            
        except KeyError as e:
            logger.error(f"Missing key in ARF data - {e}")
            return None

        airfoil_obj.update()

        return airfoil_obj

def flip_airfoil_horizontally(airfoil):
    """Flip the airfoil horizontally.
    Looks for the specific params makes them negative and updates an airfoil geometry.
    
    Note: Since 0.4 version no new airfoil is created.

    Args:
        airfoil (class Airfoil): pass the airfoil object

    Returns:
        class Airfoil: the same airfoil with params flipped and geometry updated
    """ 
    if airfoil._is_pressure_side_up:
        airfoil._is_pressure_side_up = False # Flip also the PS with SS
    else:
        airfoil._is_pressure_side_up = True # Flip back the PS and SS

    airfoil_keys = [p for p in  airfoil.params]
    logger.debug(f"Found keys: {airfoil_keys}")

    for key in airfoil_keys:
        old_value = airfoil.params[key].value
        if key in []: # "incline","LE_angle","TE_angle"
            airfoil.params[key].value = -old_value
    
    le_keys = [p for p in  airfoil.LE.params]
    logger.debug(f"Found LE keys: {le_keys}")

    for key in le_keys:
        old_value = airfoil.LE.params[key].value
        if key in []:
            airfoil.LE.params[key].value = -old_value
    
    te_keys = [p for p in  airfoil.TE.params]
    logger.debug(f"Found TE keys: {te_keys}")

    for key in te_keys:
        old_value = airfoil.TE.params[key].value
        if key in []:
            airfoil.TE.params[key].value = -old_value
    
    ps_keys = [p for p in  airfoil.PS.params]
    logger.debug(f"Found PS keys: {ps_keys}")

    for key in ps_keys:
        old_value = airfoil.PS.params[key].value
        if key in []: # "incline","LE_angle","TE_angle"
            airfoil.PS.params[key].value = -old_value

    ss_keys = [p for p in  airfoil.SS.params]
    logger.debug(f"Found SS keys: {ss_keys}")

    for key in ss_keys:
        old_value = airfoil.SS.params[key].value
        if key in []: # "incline","LE_angle","TE_angle"
            airfoil.SS.params[key].value = -old_value

    airfoil.update()
    
    return airfoil