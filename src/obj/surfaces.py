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
from geomdl import BSpline, utilities, fitting

class Patch:
    """
    Represents a B-spline surface bounded by 4 curves (Coons patch interpolation).
    
    The surface is created from 4 boundary splines:
    - u_fwd, u_rwd: curves in the u-direction (forward and reverse)
    - v_fwd, v_rwd: curves in the v-direction (forward and reverse)
    
    Public API:
    - build(): Orchestrates surface creation from boundary curves
    """
    
    def __init__(self, program, parent=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.parent = parent
        
        # Boundary curves
        self.u_fwd = None  # Forward u-direction boundary
        self.u_rwd = None  # Reverse u-direction boundary
        self.v_fwd = None  # Forward v-direction boundary
        self.v_rwd = None  # Reverse v-direction boundary

        self.vertices_flat = None
        
        # Computed results (internal)
        self.control_grid = None  # Control points grid from Coons patch
        self.surface = None       # Evaluated BSpline surface
        self.geom = []             # Mesh faces (quads)

    def build_fill(self, edge_north, edge_south, edge_east, edge_west):
        """
        Public API: Build the surface from the 4 boundary curves.
        Orchestrates all internal steps: grid creation, surface evaluation, mesh generation.
        """
        if not self._validate_boundaries():
            logging.error("Surface: Invalid boundary curves provided")
            return False
        
        self.control_grid = self._create_control_grid_from_boundaries()
        self.surface = self._create_bspline_surface(self.control_grid)
        self.geom = self._generate_surface_mesh(self.surface)
        
        u_count = len(self.control_grid)
        v_count = len(self.control_grid[0]) if u_count > 0 else 0
        logging.info(f"Surface created: control grid {u_count}x{v_count}x3, "
                    f"mesh with {len(self.geom)} quads")
        return True

    # --- METODY BUDUJĄCE (BUILDERS) ---

    def build_loft(self, curves, degree_u=3, degree_v=3):
        """
        Tworzy geometrię powierzchni metodą interpolacji (Loft) z przekrojów 3D.
        """
        self.logger.info("Building loft...")
        if not curves or len(curves) < 2:
            self.logger.warning("Loft wymaga co najmniej 2 profilów.")
            return False

        # 1. Filtrowanie profilów (odrzucamy nakładające się)
        filtered_curves = [curves[0]]
        for i in range(1, len(curves)):
            p_prev = np.array([curves[i-1][0][0], curves[i-1][1][0], curves[i-1][2][0]])
            p_curr = np.array([curves[i][0][0], curves[i][1][0], curves[i][2][0]])
            if np.linalg.norm(p_curr - p_prev) > 1e-6:
                filtered_curves.append(curves[i])

        if len(filtered_curves) < 2:
            return False

        # 2. Przygotowanie siatki punktów
        num_profiles = len(filtered_curves)
        points_per_profile = len(filtered_curves[0][0])
        grid_pts = []

        for curve in filtered_curves:
            for i in range(points_per_profile):
                grid_pts.append([float(curve[0][i]), float(curve[1][i]), float(curve[2][i])])

        deg_u = min(degree_u, num_profiles - 1)
        deg_v = min(degree_v, points_per_profile - 1)

        try:
            # Interpolacja
            surf = fitting.interpolate_surface(grid_pts, num_profiles, points_per_profile, deg_u, deg_v)
            surf.delta = (0.05, 0.05)
            surf.evaluate()

            if not surf.evalpts or np.isnan(surf.evalpts).any():
                self.logger.error("Loft generated incorrect points (NaN/None)!")
                return False

            self.surface = surf
            self._update_opengl_mesh()
            return True
        except Exception as e:
            self.logger.error(f"Błąd generowania Loft: {e}")
            return False

    def _validate_boundaries(self):
        """Check that all 4 boundary curves are set."""
        return all([self.u_fwd, self.u_rwd, self.v_fwd, self.v_rwd])

    def _create_control_grid_from_boundaries(self):
        """
        Build control grid using Coons patch interpolation.
        Smoothly interpolates between the 4 boundary curves.
        Returns: numpy array of shape (n_u, n_v, 3)
        """
        u_count = len(self.u_fwd.control_points[0])
        v_count = len(self.v_fwd.control_points[0])
        
        grid = np.zeros((u_count, v_count, 3))
        
        for u in range(u_count):
            for v in range(v_count):
                tu = u / (u_count - 1) if u_count > 1 else 0
                tv = v / (v_count - 1) if v_count > 1 else 0
                
                # Interpolate along u-direction curves
                cu = (1 - tu) * self._get_control_point(self.v_fwd, v) + \
                     tu * self._get_control_point(self.v_rwd, v)
                
                # Interpolate along v-direction curves
                cv = (1 - tv) * self._get_control_point(self.u_fwd, u) + \
                     tv * self._get_control_point(self.u_rwd, u)
                
                # Bilinear blend of corners
                p00 = self._get_control_point(self.u_fwd, 0)
                p10 = self._get_control_point(self.u_fwd, u_count - 1)
                p01 = self._get_control_point(self.u_rwd, 0)
                p11 = self._get_control_point(self.u_rwd, u_count - 1)
                bilinear = (1 - tu) * (1 - tv) * p00 + tu * (1 - tv) * p10 + \
                          (1 - tu) * tv * p01 + tu * tv * p11
                
                grid[u, v, :] = cu + cv - bilinear
        
        return grid

    def _get_control_point(self, curve, index):
        """Extract a single control point from a curve as a numpy array."""
        return np.array([curve.control_points[0][index],
                        curve.control_points[1][index],
                        curve.control_points[2][index]])

    def _create_bspline_surface(self, control_grid):
        """
        Create and evaluate a B-spline surface from control grid.
        Returns: geomdl.BSpline.Surface object with evaluated points
        """
        n_u = len(control_grid)
        n_v = len(control_grid[0]) if n_u > 0 else 0
        
        if n_u < 2 or n_v < 2:
            logging.error(f"Surface: Invalid control grid size {n_u}x{n_v}")
            return None
        
        # Flatten control points
        ctrlpts_flat = [[float(p[0]), float(p[1]), float(p[2])]
                       for row in control_grid for p in row]
        
        # Create surface
        surf = BSpline.Surface()
        surf.degree_u = min(self.u_fwd.degree, n_u - 1)
        surf.degree_v = min(self.v_fwd.degree, n_v - 1)
        surf.set_ctrlpts(ctrlpts_flat, n_u, n_v)
        surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, n_u)
        surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, n_v)
        
        # Set resolution based on performance settings
        perf = int(self.DAEDALUS.preferences["general"]["performance"])
        resolution = -0.00056 * perf + 0.1
        surf.delta = (resolution, resolution)
        
        surf.evaluate()
        return surf

    def _generate_surface_mesh(self, surf):
        """
        Convert evaluated surface to quad faces.
        Returns: list of quads [(p0,p1,p2,p3), ...]
        """
        if surf is None:
            return []
        
        res_u, res_v = surf.sample_size
        grid = [[surf.evalpts[i * res_v + j] for j in range(res_v)] 
               for i in range(res_u)]
        
        faces = []
        for i in range(res_u - 1):
            for j in range(res_v - 1):
                p0 = grid[i][j]
                p1 = grid[i][j + 1]
                p2 = grid[i + 1][j + 1]
                p3 = grid[i + 1][j]
                faces.append((p0, p1, p2, p3))
        
        return faces
    
    # --- METODY POMOCNICZE ---

    def _update_opengl_mesh(self):
        """Przelicza punkty z surface na siatkę quadów dla renderera."""
        if not self.surface:
            return
        res_u, res_v = self.surface.sample_size
        grid = [[self.surface.evalpts[i * res_v + j] for j in range(res_v)] for i in range(res_u)]
        
        new_faces = []
        for i in range(res_u - 1):
            for j in range(res_v - 1):
                new_faces.append((grid[i][j], grid[i][j+1], grid[i+1][j+1], grid[i+1][j]))
                
        self.geom = new_faces

        # Tworzymy płaską tablicę float32 raz
        self.vertices_flat = np.array(new_faces, dtype=np.float32).reshape(-1, 3)