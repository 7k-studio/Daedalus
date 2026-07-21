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

        param_data = {"value": final_value} 
        parsed[key] = param_data
        
    return parsed