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
    """
    
    def __init__(self, program, parent=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.parent = parent
        
        # Boundary curves
        self.u_fwd = None
        self.u_rwd = None
        self.v_fwd = None
        self.v_rwd = None

        self.vertices_flat = None
        
        # Computed results
        self.control_grid = None
        self.surface = None
        self.geom = []

    def build_fill(self, edge_north, edge_south, edge_east, edge_west):
        if not self._validate_boundaries():
            logging.error("Surface: Invalid boundary curves provided")
            return False

        self.u_fwd = edge_north
        self.u_rwd = edge_south
        self.v_fwd = edge_east
        self.v_rwd = edge_west
        
        self.control_grid = self._create_control_grid_from_boundaries()
        self.surface = self._create_bspline_surface(self.control_grid)
        self.geom = self._generate_surface_mesh(self.surface)
        
        u_count = len(self.control_grid)
        v_count = len(self.control_grid[0]) if u_count > 0 else 0
        logging.info(f"Surface created: control grid {u_count}x{v_count}x3, "
                    f"mesh with {len(self.geom)} quads")
        return True

    def _normalize_profile_grid(self, spline_objects, target_degree_v):
        raw_profiles = []
        max_pts = 0
        max_deg = target_degree_v

        for s in spline_objects:
            cps = np.array(s.control_points, dtype=np.float64)
            if cps.shape[0] == 3 and cps.shape[1] != 3:
                cps = cps.T
            
            raw_profiles.append(cps)
            max_pts = max(max_pts, len(cps))
            
            s_deg = getattr(s, 'degree', 3)
            max_deg = max(max_deg, s_deg)

        deg_v = min(max_deg, max_pts - 1)
        normalized_grid = []

        for cps in raw_profiles:
            curr_pts = len(cps)
            if curr_pts != max_pts:
                t_old = np.linspace(0.0, 1.0, curr_pts)
                t_new = np.linspace(0.0, 1.0, max_pts)
                resampled = np.column_stack([
                    np.interp(t_new, t_old, cps[:, 0]),
                    np.interp(t_new, t_old, cps[:, 1]),
                    np.interp(t_new, t_old, cps[:, 2])
                ])
                normalized_grid.append(resampled)
            else:
                normalized_grid.append(cps)

        return np.array(normalized_grid, dtype=np.float64), deg_v, max_pts

    def build_loft(self, spline_objects, u_fwd=None, u_rwd=None, degree_u=3, degree_v=3, mode_u='approximated', mode_v='interpolated'):
        """
        Builds surface geometry via Lofting:
        - mode_v: 'interpolated' (spanwise interpolation through profiles) or 'approximated'
        - mode_u: 'approximated' (preserves airfoil profile control points) or 'interpolated'
        """
        self.logger.info(f"Building loft (mode_u: {mode_u}, mode_v: {mode_v})...")
        if not spline_objects or len(spline_objects) < 2:
            self.logger.error("Loft requires at least 2 profiles")
            return False

        self.v_fwd = spline_objects[0]
        self.v_rwd = spline_objects[-1]
        self.u_fwd = u_fwd
        self.u_rwd = u_rwd

        num_profiles = len(spline_objects)
        deg_u = min(degree_u, num_profiles - 1)

        try:
            # Step 1: Normalize profile control points across all profiles
            grid_array, deg_v, points_per_profile = self._normalize_profile_grid(spline_objects, degree_v)

            # Step 2: V Direction (Interpolates spanwise between segments/profiles)
            if mode_v == 'interpolated' and num_profiles >= 2:
                v_fitted_grid = np.zeros_like(grid_array)
                for col in range(points_per_profile):
                    pts_to_interpolate = grid_array[:, col, :].tolist()
                    curve_fitted = fitting.interpolate_curve(pts_to_interpolate, deg_u)
                    v_fitted_grid[:, col, :] = np.array(curve_fitted.ctrlpts, dtype=np.float64)
                
                self.control_grid = v_fitted_grid
            else:
                self.control_grid = grid_array

            # Step 3: U Direction (Keep airfoil profiles approximated as defined)
            if mode_u == 'interpolated':
                u_fitted_grid = np.zeros_like(self.control_grid)
                for row in range(num_profiles):
                    pts_to_interpolate = self.control_grid[row, :, :].tolist()
                    curve_fitted = fitting.interpolate_curve(pts_to_interpolate, deg_v)
                    u_fitted_grid[row, :, :] = np.array(curve_fitted.ctrlpts, dtype=np.float64)
                
                self.control_grid = u_fitted_grid

            # Step 4: Evaluate Surface
            control_grid_pts = self.control_grid.reshape(-1, 3).tolist()

            surf = BSpline.Surface()
            surf.degree_u = deg_u
            surf.degree_v = deg_v
            surf.set_ctrlpts(control_grid_pts, num_profiles, points_per_profile)
            surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, num_profiles)
            surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, points_per_profile)

            perf = int(self.DAEDALUS.preferences["general"]["performance"])
            resolution = -0.00056 * perf + 0.1
            surf.delta = (resolution, resolution)
            surf.evaluate()

            if not surf.evalpts or np.isnan(surf.evalpts).any():
                self.logger.error("Loft generated invalid points (NaN/None)!")
                return False

            self.surface = surf
            self._sync_boundary_splines()
            self._update_opengl_mesh()
            return True

        except Exception as e:
            self.logger.error(f"Error generating Loft: {e}")
            return False

    def _validate_boundaries(self):
        return all([self.u_fwd, self.u_rwd, self.v_fwd, self.v_rwd])

    def _create_control_grid_from_boundaries(self):
        u_count = len(self.u_fwd.control_points[0])
        v_count = len(self.v_fwd.control_points[0])
        
        grid = np.zeros((u_count, v_count, 3))
        
        for u in range(u_count):
            for v in range(v_count):
                tu = u / (u_count - 1) if u_count > 1 else 0
                tv = v / (v_count - 1) if v_count > 1 else 0
                
                cu = (1 - tu) * self._get_control_point(self.v_fwd, v) + \
                     tu * self._get_control_point(self.v_rwd, v)
                
                cv = (1 - tv) * self._get_control_point(self.u_fwd, u) + \
                     tv * self._get_control_point(self.u_rwd, u)
                
                p00 = self._get_control_point(self.u_fwd, 0)
                p10 = self._get_control_point(self.u_fwd, u_count - 1)
                p01 = self._get_control_point(self.u_rwd, 0)
                p11 = self._get_control_point(self.u_rwd, u_count - 1)
                bilinear = (1 - tu) * (1 - tv) * p00 + tu * (1 - tv) * p10 + \
                          (1 - tu) * tv * p01 + tu * tv * p11
                
                grid[u, v, :] = cu + cv - bilinear
        
        return grid

    def _get_control_point(self, curve, index):
        return np.array([curve.control_points[0][index],
                        curve.control_points[1][index],
                        curve.control_points[2][index]])

    def _create_bspline_surface(self, control_grid):
        n_u = len(control_grid)
        n_v = len(control_grid[0]) if n_u > 0 else 0
        
        if n_u < 2 or n_v < 2:
            logging.error(f"Surface: Invalid control grid size {n_u}x{n_v}")
            return None
        
        ctrlpts_flat = [[float(p[0]), float(p[1]), float(p[2])]
                       for row in control_grid for p in row]
        
        surf = BSpline.Surface()
        surf.degree_u = min(self.u_fwd.degree, n_u - 1)
        surf.degree_v = min(self.v_fwd.degree, n_v - 1)
        surf.set_ctrlpts(ctrlpts_flat, n_u, n_v)
        surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, n_u)
        surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, n_v)
        
        perf = int(self.DAEDALUS.preferences["general"]["performance"])
        resolution = -0.00056 * perf + 0.1
        surf.delta = (resolution, resolution)
        
        surf.evaluate()
        return surf

    def _generate_surface_mesh(self, surf):
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

    def _sync_boundary_splines(self):
        if self.control_grid is None or self.surface is None:
            return

        if self.u_fwd is not None:
            north_cps = self.control_grid[:, 0, :]
            self.u_fwd.control_points = north_cps.T.tolist()
            if hasattr(self.surface, 'evalpts') and self.surface.evalpts:
                res_v = self.surface.sample_size[1]
                north_geom = [self.surface.evalpts[i * res_v] for i in range(self.surface.sample_size[0])]
                self.u_fwd.geom = np.array(north_geom).T.tolist()

        if self.u_rwd is not None:
            south_cps = self.control_grid[:, -1, :]
            self.u_rwd.control_points = south_cps.T.tolist()
            if hasattr(self.surface, 'evalpts') and self.surface.evalpts:
                res_v = self.surface.sample_size[1]
                south_geom = [self.surface.evalpts[i * res_v + (res_v - 1)] for i in range(self.surface.sample_size[0])]
                self.u_rwd.geom = np.array(south_geom).T.tolist()

    def _update_opengl_mesh(self):
        if not self.surface:
            return
        res_u, res_v = self.surface.sample_size
        grid = [[self.surface.evalpts[i * res_v + j] for j in range(res_v)] for i in range(res_u)]
        
        new_faces = []
        for i in range(res_u - 1):
            for j in range(res_v - 1):
                new_faces.append((grid[i][j], grid[i][j+1], grid[i+1][j+1], grid[i+1][j]))
                
        self.geom = new_faces
        self.vertices_flat = np.array(new_faces, dtype=np.float32).reshape(-1, 3)