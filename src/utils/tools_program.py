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
import math
import numpy as np
import logging
import json

logger = logging.getLogger(__name__)

def normalize(vector):
    length = sum(x ** 2 for x in vector) ** 0.5
    if length == 0:
        return vector
    return [x / length for x in vector]

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def lerp(start, end, t):
    return start + (end - start) * t

def deg2rad(degrees):
    return degrees * (math.pi / 180)

def rad2deg(radians):
    return radians * (180 / math.pi)

def convert_ndarray_to_list(obj):
    """Recursively convert numpy arrays in dict/list to lists."""
    if isinstance(obj, dict):
        return {k: convert_ndarray_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_ndarray_to_list(i) for i in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj
    
def convert_list_to_ndarray(obj):
    """Recursively convert lists in the object to numpy arrays where appropriate."""
    if isinstance(obj, list):
        # Only convert to ndarray if all elements are numbers or all are lists (for arrays of arrays)
        if all(isinstance(x, (int, float, complex)) for x in obj):
            return np.array(obj)
        elif all(isinstance(x, list) for x in obj):
            return np.array([convert_list_to_ndarray(x) for x in obj])
        else:
            return [convert_list_to_ndarray(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: convert_list_to_ndarray(v) for k, v in obj.items()}
    else:
        return obj

def safe_date(val):
    import datetime
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    return val

def vec_translate(points, magnitude, angle):

    angle_radians = deg2rad(angle)
    dx = magnitude * math.cos(angle_radians)
    dy = magnitude * math.sin(angle_radians)

    translated_points = [points[0] + dx, points[1] + dy]

    return translated_points

def decode_json(filePath):
    logger.info(f"Open archive airfoil: {filePath}")
    # Open the JSON file directly (as saved by saveProject)
    try:
        with open(f"{filePath}", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.error("File not found!")
        return
    except json.JSONDecodeError:
        logger.error("During decoding JSON!")
        return

    logger.debug("JSON decoded and data loaded to variable")
    # Convert lists back to numpy arrays if needed
    return convert_list_to_ndarray(data)

def get_archive_version(data):
    try:
        file_version = data["Program"].get("version", "0.0.0")
    except KeyError as e:
        try:
            file_version = data["program version"]
        except KeyError as e:
            logger.error(f"Missing key in ARF data - {e}")
            logger.warning("File may not load properly or is not compatible with DAEDALUS")
            return

    return file_version.split("-")[0].split(".")

def parse_from_params(params_dict):
    """Helper to dynamically parse Param objects"""
    return {
        key: {"value": param.value, "unit": param.unit.name}
        for key, param in params_dict.items()
    }
    
def parse_from_attrs(attrs_dict):
    """Helper to dynamically parse Attr objects"""
    parsed = {}
    
    for key, attr in attrs_dict.items():
        val = attr.value
        
        if hasattr(val, 'name'):
            final_value = val.name
            
        elif hasattr(val, 'airfoil') and hasattr(val.airfoil, 'name'):
            final_value = val.airfoil.name
            
        else:
            final_value = val

        parsed[key] = {"value": final_value} 
        
    return parsed

def update_params_dict(target_params, json_params_data, units_map):
    """
    target_params: np. {'Test': Param('test', 0, M)}
    json_params_data: np. {'Test': {'value': 0.004, 'unit': 'm'}}
    """
    if not json_params_data:
        return

    for key, param_data in json_params_data.items():
        if key in target_params:
            target_params[key].update_from_dict(param_data, units_map)

def update_attrs_dict(target_attrs, json_attrs_data, airfoils_list=None):
    """
    target_attrs: np. {'Test': Param('test', "G1", ["G1","G2"])}
    json_attrs_data: np. {'Test': {'value': "G1"}}
    """
    if not json_attrs_data:
        return

    for key, attr_data in json_attrs_data.items():
        if key in target_attrs:
            # Aktualizujemy istniejący obiekt Param
            target_attrs[key].update_from_dict(attr_data, airfoils_list=airfoils_list)