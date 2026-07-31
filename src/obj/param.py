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
class Unit:
    def __init__(self, name, to_si):
        self.name = name
        self.to_si = to_si  # multiply to convert → SI

    def to_si_value(self, value):
        return value * self.to_si

    def from_si_value(self, value):
        return value / self.to_si


# base units
M = Unit("m", 1.0)
MM = Unit("mm", 0.001)
IN = Unit("in", 0.0254)
FT = Unit("ft", 0.3048)

DEG = Unit("deg", 1.0)  # keep angles separate logically
RAD = Unit("rad", 180.0 / 3.141592653589793)

class Param:
    def __init__(self, name, value, unit: Unit):
        self.name = name
        # Always store internally in SI units
        self.value = value
        self.nominal = value
        self.unit = unit

    def get(self):
        """Get value in current unit"""
        return self.unit.from_si_value(self.value)

    def set(self, value):
        """Set value in current unit (converts to SI internally)"""
        self.value = self.unit.to_si_value(value)

    def set_unit(self, new_unit: Unit):
        # only changes how value is interpreted/displayed
        self.unit = new_unit

    def get_si(self):
        """Get value in SI units"""
        return self.value

    def update_from_dict(self, data, units_map):
        """Update state of param based on data in JSON-ddls"""
        if not isinstance(data, dict):
            return

        # Set value and nominal from dictionary
        if "value" in data:
            new_val = data["value"]
            self.value = new_val
            self.nominal = new_val

        # Set unit based on string
        if "unit" in data:
            unit_str = data["unit"]
            if unit_str in units_map:
                self.unit = units_map[unit_str]

class Attr:
    def __init__(self, name, value, allowed_values):
        self.name = name
        self.value = value
        self.nominal = value
        self.allowed_values = allowed_values
    
    def update_from_dict(self, data, airfoils_list=None):
        """Update state of attr based on data in JSON-ddls"""
        if not isinstance(data, dict):
            return

        raw_val = data["value"]

        # Set value and nominal from dictionary
        if self.name.lower() == "airfoil" and airfoils_list:
            # Search airfoil by name
            matched_airfoil = next(
                (a for a in airfoils_list if a.name == raw_val),
                airfoils_list[0] if airfoils_list else None
            )
            self.value = matched_airfoil
            self.nominal = matched_airfoil
        else:
            self.value = raw_val
            self.nominal = raw_val
        