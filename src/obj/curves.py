'''

Copyright (C) 2025-2026 Jakub Kamyk

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

from scipy.interpolate import splprep, splev, BSpline, interp1d
from scipy import interpolate

class Line:
    def __init__(self):
        self.start_point = []
        self.end_point = []
        self.geom = []
    
    def create(self):
        self.geom = self.start_point
        self.geom.append(self.end_point)

class BSpline:
    def __init__(self, program, parent=None):
        self.DAEDALUS = program
        self.parent = parent
        self.control_points = []
        self.geom = []
        self.mode = 'approximated'  # 'approximated' or 'interpolated'
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create(self, degree=None, resolution=None, mode='approximated', min_intermediate_points=3):
        """
        Create a B-spline curve.
        
        Args:
            degree: B-spline degree. If None, computed from control points
            resolution: Sampling resolution. If None, uses performance setting
            mode: 'approximated' - use control points as is, 'interpolated' - spline passes through points
            min_intermediate_points: Minimum number of intermediate control points to create for G0 continuity
        """
        self.mode = mode
        
        # Check if control_points is empty - handle both list and numpy array
        try:
            is_empty = len(self.control_points) == 0
        except (TypeError, ValueError):
            is_empty = True
        
        if is_empty:
            self.logger.warning("No control points defined for B-spline")
            self.geom = []
            return
        
        coords = [np.array(c) for c in self.control_points] # format: [X_array, Y_array, Z_array]
        print('Control points', self.control_points)
        print('Coords:', coords)
        print('Mode:', mode)
        l = len(coords[0])  # number of control points
        
        # If we only have 2 points and in approximated mode, create intermediate control points
        if l <= 2 and mode == 'approximated':
            print(f"Warning: Only {l} control points. Creating intermediate points for better curve.")
            coords = self._create_intermediate_control_points(coords, min_intermediate_points)
            l = len(coords[0])
        
        if degree is None:
            degree = min(3, l - 1)
        degree = min(degree, l - 1)
        self.degree = degree
        
        if mode == 'interpolated':
            # Interpolated mode: create spline that passes through all points
            self.geom = self._create_interpolated_spline(coords, resolution)
        else:
            # Approximated mode: use control points directly
            self.geom = self._create_approximated_spline(coords, degree, resolution)
    
    def _create_intermediate_control_points(self, coords, min_count=3):
        """Create intermediate control points between two endpoints for better curve."""
        if len(coords[0]) < 2:
            return coords
        
        new_coords = []
        for axis_array in coords:
            start = axis_array[0]
            end = axis_array[-1]
        
            # Create intermediate points along the line
            intermediate = [start]
        
            for i in range(1, min_count):
                t = i / min_count
                val = start + t * (end - start)
                intermediate.append(val)
            intermediate.append(end)

            new_coords.append(np.array(intermediate))

        return new_coords
    
    def _create_approximated_spline(self, coords, degree, resolution):
        """Create a B-spline using control points (approximated)."""
        l = len(coords[0])
        
        # Knot vector for clamped B-spline
        t = np.concatenate((
            np.zeros(degree),                   # start knots
            np.linspace(0, 1, l - degree + 1),  # interior knots
            np.ones(degree)                     # end knots
        ))
        
        tck = [t, coords, degree]
        
        # Sampling resolution
        if resolution is None:
            f = int(self.DAEDALUS.preferences['general']['performance'])
        else:
            f = resolution

        u3 = np.linspace(0, 1, (max(l * f / 100, f)), endpoint=True)
        
        return splev(u3, tck)
    
    def _create_interpolated_spline(self, coords, resolution):
        """Create a spline that passes through all given points (interpolated)."""
        # Use scipy's interpolate to create a spline through the points
        l = len(coords[0])
        k = min(3, l-1)
        
        # Obliczanie spline'u interpolacyjnego przez SciPy
        tck, u = interpolate.splprep(coords, s=0, k=k)
        
        # --- SZYBKIE OBEJŚCIE PUŁAPKI ---
        # tck[1] zawiera listę [X_arrays, Y_arrays, Z_arrays] nowych punktów kontrolnych.
        # Nadpisujemy nimi self.control_points, żeby Patch zobaczył właściwą powłokę!
        self.control_points = [tck[1][0].tolist(), tck[1][1].tolist(), tck[1][2].tolist()]
        self.degree = tck[2]  # Nadpisujemy stopień tym z interpolacji (zwykle k=3)
        # --------------------------------
        
        if resolution is None:
            f = int(self.DAEDALUS.preferences['general']['performance'])
        else:
            f = resolution

        u_new = np.linspace(0, 1, int(max(l * f / 100, f)), endpoint=True)
        return interpolate.splev(u_new, tck)