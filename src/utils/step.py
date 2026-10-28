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
import datetime
import numpy as np

logger = logging.getLogger(__name__)


def process_knot_vector(knot_list, degree, num_pts):
    """
    Computes distinct knot values and corresponding knot multiplicities for STEP AP203.
    Generates a clamped uniform knot vector if knot_list is None or a simplified range.
    """
    if knot_list is None or len(knot_list) < 2:
        num_middle = num_pts - degree - 1
        if num_middle <= 0:
            full_knots = [0.0] * (degree + 1) + [1.0] * (degree + 1)
        else:
            middle_knots = np.linspace(0.0, 1.0, num_middle + 2)[1:-1].tolist()
            full_knots = [0.0] * (degree + 1) + middle_knots + [1.0] * (degree + 1)
    elif len(knot_list) == 2 and knot_list[0] != knot_list[1]:
        k_min, k_max = float(knot_list[0]), float(knot_list[1])
        num_middle = num_pts - degree - 1
        if num_middle <= 0:
            full_knots = [k_min] * (degree + 1) + [k_max] * (degree + 1)
        else:
            middle_knots = np.linspace(k_min, k_max, num_middle + 2)[1:-1].tolist()
            full_knots = [k_min] * (degree + 1) + middle_knots + [k_max] * (degree + 1)
    else:
        full_knots = [float(k) for k in knot_list]

    unique_knots = []
    mults = []
    for k in full_knots:
        k_round = round(k, 10)
        if not unique_knots or abs(unique_knots[-1] - k_round) > 1e-8:
            unique_knots.append(k_round)
            mults.append(1)
        else:
            mults[-1] += 1

    return mults, unique_knots


def normalized_coords(x, y, z):
    return (
        float(round(x, 10)),
        float(round(y, 10)),
        float(round(z, 10))
    )


class Daedalus2Step:
    def __init__(self, program=None, project=None, base_name="Unknown"):
        self.name = "Deadalus2Step203"
        self.description = "Deadalus Python STEP AP203 Export"
        self.version = "0.2.0-beta"

        self.PROGRAM = program
        self.PROJECT = project

        self.measurement_store = []
        self.all_elements_store = {}
        self.base_name = base_name

    def HEADER(self, file, base_name):
        file.write("ISO-10303-21;\n")
        file.write("HEADER;\n")
        file.write(f"FILE_DESCRIPTION(('{self.description}'), '1');\n")
        file.write(f"FILE_NAME('{self.base_name}','{datetime.datetime.now()}',(''),(''),'{self.description}','{self.name}','{self.version}');\n")
        file.write("FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));\n")

    def ENDSEC_OPEN(self, file):
        file.write("ENDSEC;\n\nDATA;\n")

    def FOOTER(self, file):
        file.write("ENDSEC;\nEND-ISO-10303-21;")

    def export_surfaces(self, filePath):
        self.build_step()
        self.write_step_file(filePath)

    def build_step(self):
        mech_context, design_context = self.build_application_context()
        manifold_shape_surf_rep = self.build_manifold_shape_surf_rep()

        product = Product(self.base_name.replace(".step", ""), mech_context)
        self.all_elements_store["product"] = product

        pdfwss = ProductDefinitionFormationWithSpecifiedSource(product)
        self.all_elements_store["product_definition_form_w_spec_source"] = pdfwss

        prod_def = ProductDefinition(prod_def_form_w_spec_source=pdfwss, design_context=design_context)
        self.all_elements_store["product_definition"] = prod_def

        prod_def_shape = ProductDefinitionShape(prod_def)
        self.all_elements_store["product_definition_shape"] = prod_def_shape

        shape_def_rep = ShapeDefinitionRepresentation(prod_def_shape, manifold_shape_surf_rep)
        self.all_elements_store["shape_definition_representation"] = shape_def_rep

    def build_application_context(self):
        app_context = ApplicationContext()
        self.all_elements_store["application_context"] = app_context

        design_context = DesignContext(app_context)
        self.all_elements_store["design_context"] = design_context

        mech_context = MechanicalContext(application_context_obj=app_context)
        self.all_elements_store["mechanical_context"] = mech_context

        return design_context, mech_context

    def build_geometric_representation_context(self):
        UNIT = self.PROGRAM.preferences["general"]["units"] if self.PROGRAM else {"angle": "rad", "length": "m"}

        solid_angle_unit = SolidAngleUnit(UNIT["angle"])
        self.all_elements_store["solid angle unit"] = solid_angle_unit

        plane_angle_unit = PlaneAngleUnit(UNIT["angle"])
        self.all_elements_store["plane angle unit"] = plane_angle_unit

        length_unit = LengthUnit(UNIT["length"])
        self.all_elements_store["length unit"] = length_unit

        uncertainty_measure = UncertaintyMeasure(length_unit)
        self.all_elements_store["uncertainty measure"] = uncertainty_measure

        geometric_representation_context = GeometricRepresentationContext(uncertainty_measure, length_unit, solid_angle_unit, plane_angle_unit)
        self.all_elements_store["geometric representation context"] = geometric_representation_context

        return geometric_representation_context

    def build_manifold_shape_surf_rep(self):
        geometric_representation_context = self.build_geometric_representation_context()
        last_axis_placement = None
        all_open_shells = []

        self.all_elements_store["patches"] = []
        cartesian_point_cache = {}
        vertex_point_cache = {}
        edge_curve_cache = {}

        if not self.PROJECT:
            return None

        for component in self.PROJECT.components:
            for wing in component.wings:
                skin_obj = getattr(wing, "skin", None)
                if not skin_obj:
                    continue

                tmp_surface_store = []
                patch_boundary_map = {
                    'LE': ('v_fwd', 'u_fwd', 'v_rwd', 'u_rwd'),
                    'TE': ('v_fwd', 'u_fwd', 'v_rwd', 'u_rwd'),
                    'PS': ('v_fwd', 'u_fwd', 'v_rwd', 'u_rwd'),
                    'SS': ('v_fwd', 'u_fwd', 'v_rwd', 'u_rwd')
                }

                for key in ["LE", "TE", "PS", "SS"]:
                    patch = getattr(skin_obj, key, None)
                    if patch is None:
                        continue

                    cp_grid_data, u_deg, v_deg, knots_u, knots_v = _extract_patch_data(patch)
                    if not cp_grid_data:
                        continue

                    cp_store, cp_grid_objs = _write_control_points(
                        cp_grid_data, key, cartesian_point_cache
                    )
                    vp_store, vp_grid_objs = _write_vertex_point(
                        cp_grid_objs, key, vertex_point_cache
                    )

                    bound_attrs = patch_boundary_map[key]
                    parent_splines = [getattr(patch, attr, None) for attr in bound_attrs]
                    o_edges, e_curves, b_splines = _write_oriented_edge_from_uv_grid(
                        key,
                        cp_grid_objs,
                        vp_grid_objs,
                        parent_splines,
                        cartesian_point_cache,
                        vertex_point_cache,
                        edge_curve_cache,
                        (id(wing), key),
                    )

                    b_spline_surf, edge_loop, face_bound, advanced_face = _write_advanced_face_from_patch(
                        key, u_deg, v_deg, cp_grid_objs, knots_u, knots_v, o_edges
                    )

                    patch_store = [
                        cp_store, vp_store, b_splines, e_curves,
                        o_edges, b_spline_surf, edge_loop, face_bound, advanced_face
                    ]
                    self.all_elements_store["patches"].append(patch_store)
                    tmp_surface_store.append(advanced_face)

                if getattr(wing, "segments", None):
                    dir_nor, dir_tan = _write_direction(wing.segments[0])
                    origin_cp = cp_grid_objs[0][0] if 'cp_grid_objs' in locals() else None
                    last_axis_placement = Axis2Placement3D(f"{wing.name} Axis Placement", origin_cp, dir_nor, dir_tan)
                    self.all_elements_store[f"{wing.name}_axis"] = [dir_nor, dir_tan, last_axis_placement]

                if tmp_surface_store:
                    open_shell = OpenShell(f'{wing.name} Shell', tmp_surface_store)
                    all_open_shells.append(open_shell)
                    self.all_elements_store[f"{wing.name}_shell"] = open_shell

        shell_based_surface_model = ShellBasedSurfaceModel("Wing Surface Model", all_open_shells)
        self.all_elements_store["shell_based_surface_model"] = shell_based_surface_model

        manifold_shape_surf_rep = ManifoldSurfaceShapeRepresentation(
            f'{self.base_name.replace(".step", "")}', shell_based_surface_model, last_axis_placement, geometric_representation_context
        )
        self.all_elements_store["manifold_shape_surf_repersentation"] = manifold_shape_surf_rep

        return manifold_shape_surf_rep

    def write_step_file(self, filepath):
        all_entities = []

        def collect(value):
            if isinstance(value, (list, tuple, np.ndarray)):
                for item in value:
                    collect(item)
            elif isinstance(value, dict):
                for v in value.values():
                    collect(v)
            elif hasattr(value, "export") and callable(value.export):
                if value not in all_entities:
                    all_entities.append(value)
                    for attr in vars(value).values():
                        collect(attr)

        collect(self.measurement_store)
        collect(self.all_elements_store)

        for idx, entity in enumerate(all_entities, start=1):
            entity.idx = idx

        with open(filepath, "w") as file:
            self.HEADER(file, self.base_name)
            self.ENDSEC_OPEN(file)
            for entity in all_entities:
                file.write(entity.export() + '\n')
            self.FOOTER(file)


def _extract_patch_data(patch):
    if patch.surface is not None and hasattr(patch.surface, 'ctrlpts2d'):
        cp_grid = patch.surface.ctrlpts2d
        u_deg = patch.surface.degree_u
        v_deg = patch.surface.degree_v
        knots_u = patch.surface.knotvector_u if hasattr(patch.surface, 'knotvector_u') else None
        knots_v = patch.surface.knotvector_v if hasattr(patch.surface, 'knotvector_v') else None
        return cp_grid, u_deg, v_deg, knots_u, knots_v
    elif patch.control_grid is not None:
        grid = patch.control_grid.tolist()
        u_deg = patch.u_fwd.degree if patch.u_fwd else 3
        v_deg = patch.v_fwd.degree if patch.v_fwd else 3
        return grid, u_deg, v_deg, None, None

    return None, 3, 3, None, None


def _write_control_points(uv_grid=None, key=None, point_cache=None):
    cp_store = []
    rows = len(uv_grid)
    cols = len(uv_grid[0])
    tmp_control_points_grid = [[None for _ in range(cols)] for _ in range(rows)]
    point_cache = {} if point_cache is None else point_cache

    for j in range(rows):
        for i in range(cols):
            coords = normalized_coords(uv_grid[j][i][0], uv_grid[j][i][1], uv_grid[j][i][2])
            cp = point_cache.get(coords)
            if cp is None:
                cp = CartesianPoint(
                    desc='Control Point', X=coords[0], Y=coords[1], Z=coords[2]
                )
                point_cache[coords] = cp
            tmp_control_points_grid[j][i] = cp
            cp_store.append(cp)

    return cp_store, tmp_control_points_grid


def _write_vertex_point(
    uv_grid_of_objects: list, key: str, vertex_point_cache=None
):
    vp_store = []
    rows = len(uv_grid_of_objects)
    cols = len(uv_grid_of_objects[0])

    max_u = rows - 1
    max_v = cols - 1
    tmp_vertex_points_grid = [[None for _ in range(cols)] for _ in range(rows)]
    vertex_point_cache = (
        {} if vertex_point_cache is None else vertex_point_cache
    )

    def add_vp(r, c, label):
        point = uv_grid_of_objects[r][c]
        vp = vertex_point_cache.get(id(point))
        if vp is None:
            vp = VertexPoint(
                f"End point {key} {label}", cartesian_point=point
            )
            vertex_point_cache[id(point)] = vp
        tmp_vertex_points_grid[r][c] = vp
        vp_store.append(vp)

    add_vp(0, 0, "(0,0)")
    add_vp(0, max_v, "(0,v)")
    add_vp(max_u, 0, "(u,0)")
    add_vp(max_u, max_v, "(u,v)")

    return vp_store, tmp_vertex_points_grid


def _write_oriented_edge_from_uv_grid(
    key,
    cp_uv_grid,
    vp_uv_grid,
    parent_splines=None,
    point_cache=None,
    vertex_point_cache=None,
    edge_curve_cache=None,
    face_key=None,
):
    spline_store = []
    ec_store = []
    oe_store = []
    point_cache = {} if point_cache is None else point_cache
    vertex_point_cache = (
        {} if vertex_point_cache is None else vertex_point_cache
    )
    edge_curve_cache = {} if edge_curve_cache is None else edge_curve_cache

    key_lower = key.lower()
    txt = [f'{key_lower}_v_fwd', f'{key_lower}_u_rwd', f'{key_lower}_v_rwd', f'{key_lower}_u_fwd']

    rows = len(cp_uv_grid)
    cols = len(cp_uv_grid[0])

    boundary_defs = [
        ('row', 0,  'T', txt[0], 0),
        ('col', -1, 'T', txt[1], 3),
        ('row', -1, 'F', txt[2], 2),
        ('col', 0,  'F', txt[3], 1),
    ]

    for slice_type, idx_val, orientation, label, p_idx in boundary_defs:
        spline_cp = []

        if slice_type == 'row':
            for c in range(cols):
                spline_cp.append(cp_uv_grid[idx_val][c])
            grid_start_vertex = vp_uv_grid[idx_val][0]
            grid_end_vertex = vp_uv_grid[idx_val][-1]
        else:
            for r in range(rows):
                spline_cp.append(cp_uv_grid[r][idx_val])
            grid_start_vertex = vp_uv_grid[0][idx_val]
            grid_end_vertex = vp_uv_grid[-1][idx_val]

        parent_spline = parent_splines[p_idx] if parent_splines and len(parent_splines) > p_idx else None
        spline_coordinates = None
        if parent_spline is not None:
            try:
                coordinates = np.asarray(
                    parent_spline.control_points, dtype=float
                )
                if coordinates.ndim == 2 and coordinates.shape[0] in (2, 3):
                    spline_coordinates = coordinates.T
            except (TypeError, ValueError):
                spline_coordinates = None

        if spline_coordinates is not None and len(spline_coordinates) >= 2:
            spline_cp = []
            for point in spline_coordinates:
                coords = normalized_coords(
                    point[0], point[1], point[2] if len(point) > 2 else 0.0
                )
                cartesian_point = point_cache.get(coords)
                if cartesian_point is None:
                    cartesian_point = CartesianPoint(
                        desc='Shared boundary control point',
                        X=coords[0],
                        Y=coords[1],
                        Z=coords[2],
                    )
                    point_cache[coords] = cartesian_point
                spline_cp.append(cartesian_point)

        bspline = BSplineWithKnots(label, cartesian_points=spline_cp, spline_obj=parent_spline)
        point_coordinates = tuple(
            (point.X, point.Y, point.Z) for point in spline_cp
        )
        reversed_coordinates = tuple(reversed(point_coordinates))
        canonical_coordinates = min(point_coordinates, reversed_coordinates)
        edge_key = (
            id(parent_spline) if parent_spline is not None else None,
            canonical_coordinates,
            bspline.degree,
            tuple(bspline.mults),
            tuple(bspline.knots),
        )
        face_identity = face_key if face_key is not None else (key, id(cp_uv_grid))
        matching_edge = next(
            (
                entry for entry in edge_curve_cache.get(edge_key, ())
                if face_identity not in entry["faces"]
                and len(entry["faces"]) < 2
            ),
            None,
        )
        if matching_edge is not None:
            edge_curve = matching_edge["edge_curve"]
            # Adjacent faces must traverse their shared edge in opposite directions.
            orientation = (
                'F' if matching_edge["orientation"] == 'T' else 'T'
            )
            matching_edge["faces"].add(face_identity)
        else:
            start_point = spline_cp[0]
            end_point = spline_cp[-1]
            start_vertex = vertex_point_cache.get(id(start_point))
            if start_vertex is None and getattr(
                grid_start_vertex, "cartesian_point", None
            ) is start_point:
                start_vertex = grid_start_vertex
            if start_vertex is None:
                start_vertex = VertexPoint(
                    f"End point {key} {label} start",
                    cartesian_point=start_point,
                )
            vertex_point_cache[id(start_point)] = start_vertex

            end_vertex = vertex_point_cache.get(id(end_point))
            if end_vertex is None and getattr(
                grid_end_vertex, "cartesian_point", None
            ) is end_point:
                end_vertex = grid_end_vertex
            if end_vertex is None:
                end_vertex = VertexPoint(
                    f"End point {key} {label} end",
                    cartesian_point=end_point,
                )
            vertex_point_cache[id(end_point)] = end_vertex
            edge_curve = EdgeCurve(
                f'spline {label}',
                vp1=start_vertex,
                vp2=end_vertex,
                Curv=bspline,
            )
            edge_curve_cache.setdefault(edge_key, []).append({
                "edge_curve": edge_curve,
                "orientation": orientation,
                "faces": {face_identity},
            })

        spline_store.append(edge_curve.curve)
        ec_store.append(edge_curve)

        oriented_edge = OrientedEdge(
            f'spline {label}',
            ec_obj=edge_curve,
            orientation=orientation,
        )
        oe_store.append(oriented_edge)

    return oe_store, ec_store, spline_store


def _write_advanced_face_from_patch(key, u_deg, v_deg, cp_uv_grid, knots_u, knots_v, oriented_edge_store):
    b_spline_surface = BSplineSurfaceWithKnots(
        f'{key} b-spline surface', u_deg, v_deg, cp_uv_grid, knots_u, knots_v
    )

    surface_edge_loop = EdgeLoop(f'{key} surface', oriented_edge_store)
    face_outer_bound = FaceOuterBound(f'{key} surface', surface_edge_loop)
    advanced_face = AdvancedFace(f'{key} surface', face_outer_bound=face_outer_bound, plane_object=b_spline_surface)

    return b_spline_surface, surface_edge_loop, face_outer_bound, advanced_face


def _write_direction(segment):
    P1, P2, P3 = [0, 0, 0], [1, 0, 0], [0, 1, 0]
    V1 = np.array(P2) - np.array(P1)
    V2 = np.array(P3) - np.array(P1)
    Vn = np.cross(V1, V2)

    V1_norm = V1 / np.linalg.norm(V1)
    Vn_norm = Vn / np.linalg.norm(Vn)

    return Direction('normal', Vn_norm), Direction('tangential', V1_norm)


# --- STEP AP203 Entity Classes ---

class CartesianPoint:
    def __init__(self, desc=None, X=0.0, Y=0.0, Z=0.0):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.X = X
        self.Y = Y
        self.Z = Z

    def export(self):
        return f"#{self.idx} = CARTESIAN_POINT ( '{self.desc}', ( {self.X}, {self.Y}, {self.Z} ) ) ;"


class VertexPoint:
    def __init__(self, desc=None, cartesian_point=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.cartesian_point = cartesian_point

    def export(self):
        return f"#{self.idx} = VERTEX_POINT ( '{self.desc}', #{getattr(self.cartesian_point, 'idx', None)} ) ;"


class BSplineWithKnots:
    def __init__(self, desc=None, cartesian_points=None, spline_obj=None, knotvector=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.points = cartesian_points if cartesian_points is not None else []
        self.degree = max(1, min(3, len(self.points) - 1))

        if spline_obj and hasattr(spline_obj, 'degree'):
            self.degree = min(spline_obj.degree, max(1, len(self.points) - 1))

        kv = getattr(spline_obj, 'knotvector', knotvector)
        self.mults, self.knots = process_knot_vector(kv, self.degree, len(self.points))

    def export(self):
        cp_ids = ', '.join([f'#{obj.idx}' for obj in self.points])
        mults_str = ', '.join([str(m) for m in self.mults])
        knots_str = ', '.join([f'{k:.16g}' for k in self.knots])
        return (
            f"#{self.idx} = B_SPLINE_CURVE_WITH_KNOTS ( '{self.desc}', {self.degree}, "
            f"( {cp_ids} ), .UNSPECIFIED., .F., .F., "
            f"( {mults_str} ), ( {knots_str} ), .UNSPECIFIED. ) ;"
        )


class BSplineSurfaceWithKnots:
    def __init__(self, desc, u_degree, v_degree, cp_uv_grid, knots_u=None, knots_v=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.u_degree = u_degree
        self.v_degree = v_degree
        self.uv_grid = cp_uv_grid

        n_u = len(cp_uv_grid)
        n_v = len(cp_uv_grid[0]) if n_u > 0 else 0

        self.mults_u, self.knots_u = process_knot_vector(knots_u, u_degree, n_u)
        self.mults_v, self.knots_v = process_knot_vector(knots_v, v_degree, n_v)

    def export(self):
        u_dir_cp = []
        for row in self.uv_grid:
            u_group = ', '.join([f'#{pt.idx}' for pt in row])
            u_dir_cp.append(f"( {u_group} )")

        spline_group = ', '.join(u_dir_cp)
        mults_u_str = ', '.join([str(m) for m in self.mults_u])
        mults_v_str = ', '.join([str(m) for m in self.mults_v])
        knots_u_str = ', '.join([f'{k:.16g}' for k in self.knots_u])
        knots_v_str = ', '.join([f'{k:.16g}' for k in self.knots_v])

        return (
            f"#{self.idx} = B_SPLINE_SURFACE_WITH_KNOTS ( '{self.desc}', {self.u_degree}, {self.v_degree}, "
            f"( {spline_group} ), .UNSPECIFIED., .F., .F., .F., "
            f"( {mults_u_str} ), ( {mults_v_str} ), "
            f"( {knots_u_str} ), ( {knots_v_str} ), .UNSPECIFIED. ) ;"
        )


class EdgeCurve:
    def __init__(self, desc=None, vp1=None, vp2=None, Curv=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.vertex_point_1 = vp1
        self.vertex_point_2 = vp2
        self.curve = Curv

    def export(self):
        return f"#{self.idx} = EDGE_CURVE ( '{self.desc}', #{self.vertex_point_1.idx}, #{self.vertex_point_2.idx}, #{self.curve.idx}, .T. ) ;"


class OrientedEdge:
    def __init__(self, desc=None, ec_obj=None, orientation='T'):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.edge_curve = ec_obj
        self.orientation = orientation

    def export(self):
        return f"#{self.idx} = ORIENTED_EDGE ( '{self.desc}', *, *, #{self.edge_curve.idx}, .{self.orientation}. ) ;"


class EdgeLoop:
    def __init__(self, desc=None, OrientedEdge_list=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.OrientedEdge_list = OrientedEdge_list if OrientedEdge_list else []

    def export(self):
        oriented_edges = ', '.join([f'#{obj.idx}' for obj in self.OrientedEdge_list])
        return f"#{self.idx} = EDGE_LOOP ( '{self.desc}', ( {oriented_edges} ) ) ;"


class FaceOuterBound:
    def __init__(self, desc=None, edge_loop=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.edge_loop = edge_loop

    def export(self):
        return f"#{self.idx} = FACE_OUTER_BOUND ( '{self.desc}', #{self.edge_loop.idx}, .T. ) ;"


class AdvancedFace:
    def __init__(self, desc=None, face_outer_bound=None, plane_object=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.face_outer_bound = face_outer_bound
        self.plane = plane_object

    def export(self):
        return f"#{self.idx} = ADVANCED_FACE ( '{self.desc}', ( #{self.face_outer_bound.idx} ), #{self.plane.idx}, .T. ) ;"


class OpenShell:
    def __init__(self, desc=None, af_obj=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.advanced_face_list = af_obj if af_obj else []

    def export(self):
        advanced_faces = ', '.join([f'#{obj.idx}' for obj in self.advanced_face_list])
        return f"#{self.idx} = OPEN_SHELL ( '{self.desc}', ( {advanced_faces} ) ) ;"


class ShellBasedSurfaceModel:
    def __init__(self, desc=None, open_shell=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.open_shell_list = open_shell if open_shell else []

    def export(self):
        open_shells = ', '.join([f"#{getattr(s, 'idx', None)}" for s in self.open_shell_list])
        return f"#{self.idx} = SHELL_BASED_SURFACE_MODEL ( '{self.desc}', ( {open_shells} ) ) ;"


class Direction:
    def __init__(self, desc=None, vec=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.vec = vec if vec is not None else [0.0, 0.0, 1.0]

    def export(self):
        return f"#{self.idx} = DIRECTION ( '{self.desc}', ( {self.vec[0]}, {self.vec[1]}, {self.vec[2]} ) );"


class Axis2Placement3D:
    def __init__(self, desc=None, cp=None, dir1=None, dir2=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.cp = cp
        self.dir1 = dir1
        self.dir2 = dir2

    def export(self):
        cp_id = f"#{self.cp.idx}" if self.cp else "#*"
        return f"#{self.idx} = AXIS2_PLACEMENT_3D ( '{self.desc}', {cp_id}, #{self.dir1.idx}, #{self.dir2.idx} ) ;"


class ApplicationContext:
    def __init__(self, context='parametrical 3d design of wings'):
        self.idx = None
        self.context = context

    def export(self):
        return f"#{self.idx} = APPLICATION_CONTEXT ( '{self.context}' ) ;"


class DesignContext:
    def __init__(self, application_context_obj):
        self.idx = None
        self.desc = "detailed design"
        self.application_context = application_context_obj

    def export(self):
        return f"#{self.idx} = DESIGN_CONTEXT ( '{self.desc}', #{self.application_context.idx}, 'design' ) ;"


class MechanicalContext:
    def __init__(self, desc='NONE', application_context_obj=None, context='mechanical'):
        self.idx = None
        self.desc = desc
        self.app_context = application_context_obj
        self.context = context

    def export(self):
        return f"#{self.idx} = MECHANICAL_CONTEXT ( '{self.desc}', #{self.app_context.idx}, '{self.context}' ) ;"


class SolidAngleUnit:
    def __init__(self, angle_unit):
        self.idx = None
        self.angle_unit = '.STERADIAN.' if angle_unit == 'rad' else '.STERADIAN.'

    def export(self):
        return f"#{self.idx} = ( NAMED_UNIT ( * ) SI_UNIT ( $, {self.angle_unit} ) SOLID_ANGLE_UNIT ( ) );"


class PlaneAngleUnit:
    def __init__(self, angle_unit):
        self.idx = None
        self.angle_unit = '.RADIAN.' if angle_unit == 'rad' else '.RADIAN.'

    def export(self):
        return f"#{self.idx} = ( NAMED_UNIT ( * ) PLANE_ANGLE_UNIT ( ) SI_UNIT ( $, {self.angle_unit} ) );"


class LengthUnit:
    def __init__(self, length_unit):
        self.idx = None
        self.unit = ['.MILLI.', '.METRE.'] if length_unit == 'mm' else ['$', '.METRE.']

    def export(self):
        return f"#{self.idx} = ( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( {self.unit[0]}, {self.unit[1]} ) );"


class UncertaintyMeasure:
    def __init__(self, length_unit):
        self.idx = None
        self.length_unit = length_unit

    def export(self):
        return f"#{self.idx} = UNCERTAINTY_MEASURE_WITH_UNIT (LENGTH_MEASURE( 1.000000000000000082E-05 ), #{self.length_unit.idx}, 'distance_accuracy_value', 'NONE');"


class GeometricRepresentationContext:
    def __init__(self, uncertainty, length_unit, solid_angle, plane_angle):
        self.idx = None
        self.uncertainty = uncertainty
        self.length_unit = length_unit
        self.solid_angle = solid_angle
        self.plane_angle = plane_angle

    def export(self):
        return f"#{self.idx} = ( GEOMETRIC_REPRESENTATION_CONTEXT ( 3 ) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT ( ( #{self.uncertainty.idx} ) ) GLOBAL_UNIT_ASSIGNED_CONTEXT ( ( #{self.length_unit.idx}, #{self.plane_angle.idx}, #{self.solid_angle.idx} ) ) REPRESENTATION_CONTEXT ( 'NONE', 'WORKSPACE' ) );"


class Product:
    def __init__(self, name, mechanical_context_obj):
        self.idx = None
        self.name = name
        self.mechanical_context = mechanical_context_obj

    def export(self):
        return f"#{self.idx} = PRODUCT ( '{self.name}', '{self.name}', '', ( #{self.mechanical_context.idx} ) );"


class ProductDefinitionFormationWithSpecifiedSource:
    def __init__(self, product):
        self.idx = None
        self.product = product

    def export(self):
        return f"#{self.idx} = PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE ( 'ANY', '', #{self.product.idx}, .NOT_KNOWN. ) ;"


class ProductDefinition:
    def __init__(self, desc='UNKNOWN', prod_def_form_w_spec_source=None, design_context=None):
        self.idx = None
        self.description = desc
        self.pdfwss = prod_def_form_w_spec_source
        self.des_con = design_context

    def export(self):
        return f"#{self.idx} = PRODUCT_DEFINITION ( '{self.description}', '', #{self.pdfwss.idx}, #{self.des_con.idx} ) ;"


class ProductDefinitionShape:
    def __init__(self, product_definition):
        self.idx = None
        self.product_definition = product_definition

    def export(self):
        return f"#{self.idx} = PRODUCT_DEFINITION_SHAPE ( 'NONE', 'NONE', #{self.product_definition.idx} );"


class ManifoldSurfaceShapeRepresentation:
    def __init__(self, desc=None, sbsm=None, a2p3d=None, gp=None):
        self.idx = None
        self.desc = desc if desc is not None else 'NONE'
        self.shell_based_surf_model = sbsm
        self.axis2_placement_3d = a2p3d
        self.geom_representation = gp

    def export(self):
        a2p_ref = f"#{self.axis2_placement_3d.idx}" if self.axis2_placement_3d else "#*"
        return f"#{self.idx} = MANIFOLD_SURFACE_SHAPE_REPRESENTATION ( '{self.desc}', ( #{self.shell_based_surf_model.idx}, {a2p_ref} ), #{self.geom_representation.idx} ) ;"


class ShapeDefinitionRepresentation:
    def __init__(self, product_definition_shape, manifold_surf_shape_rep):
        self.idx = None
        self.product_def_shape = product_definition_shape
        self.manifold_surf_shape_rep = manifold_surf_shape_rep

    def export(self):
        return f"#{self.idx} = SHAPE_DEFINITION_REPRESENTATION ( #{self.product_def_shape.idx}, #{self.manifold_surf_shape_rep.idx} ) ;"