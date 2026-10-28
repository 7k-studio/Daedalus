"""Fit an airfoil's four divided spline regions to a selected reference."""

import json
import logging
import math
from copy import copy
from types import SimpleNamespace

import numpy as np
from PyQt6.QtCore import QSettings, QThread, Qt, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy.optimize import least_squares
from scipy.interpolate import PchipInterpolator

from src.opengl.viewport2D.viewport2d import ViewportOpenGL

logger = logging.getLogger(__name__)

REGION_NAMES = ("PS", "SS", "LE", "TE")
RESIDUAL_REGION_NAMES = ("LE", "SS", "PS", "TE")
RESIDUAL_STATISTICS = ("minimum", "maximum", "average")
POSITIVE_LENGTH_SUFFIXES = ("_tan", "_curv")
SLOPE_LIMIT_DEGREES = 60.0
MINIMUM_POSITIVE_LENGTH_CHORD = 1e-4
REGION_RESIDUAL_WEIGHTS = {
    "LE": 1.0,
    "SS": 1.0,
    "PS": 1.0,
    "TE": 0.35,
}
TE_ANCHOR_RESIDUAL_WEIGHT = 8.0
ROBUST_LOSS_SCALE = 0.002
REGION_COLORS = {
    "PS": "#1769aa",
    "SS": "#e07a1f",
    "LE": "#b23a48",
    "TE": "#665191",
}
SAMPLE_COUNT = 200
SURFACE_SAMPLE_COUNT = 400
BOUNDARY_KEYS = tuple(f"boundary.{index}" for index in range(4))
FIT_SETTINGS_KEY = "airfoil_fitting/preferences"


class _FitEvaluationLimit(Exception):
    pass


def _airfoil_chord(airfoil):
    points = _points_from_geometry(getattr(airfoil, "curve", None))
    if len(points) >= 2:
        chord = float(np.ptp(points[:, 0]))
        if chord > 1e-12:
            return chord

    curves = _component_curves(airfoil)
    if curves:
        chord = float(np.ptp(np.vstack(list(curves.values()))[:, 0]))
        if chord > 1e-12:
            return chord

    stats = getattr(airfoil, "stats", {})
    chord_parameter = stats.get("Chord") if isinstance(stats, dict) else None
    if chord_parameter is not None:
        chord = float(chord_parameter.get())
        if math.isfinite(chord) and chord > 1e-12:
            return chord
    return None


def _parameter_search_scale(path, parameter, chord):
    """Return conservative optimizer step scales informed by manual examples."""
    unit_name = getattr(parameter.unit, "name", "")
    if unit_name == "deg":
        if path.endswith("_slope"):
            return 5.0 if path.startswith("TE.") else 10.0
        return 10.0 if path.startswith(("PS.", "SS.")) else 5.0

    if path.startswith("TE.") and path.endswith(POSITIVE_LENGTH_SUFFIXES):
        chord_fraction = 0.004
    elif path.startswith("LE.") and path.endswith(POSITIVE_LENGTH_SUFFIXES):
        chord_fraction = 0.015
    elif path.startswith(("PS.", "SS.")) and path.endswith(
        POSITIVE_LENGTH_SUFFIXES
    ):
        chord_fraction = 0.05
    elif path in ("LE_thickness", "TE_thickness"):
        chord_fraction = 0.01
    else:
        chord_fraction = 0.02
    return max(chord * chord_fraction, 1e-8)


def _automatic_parameter_bounds(path, parameter, chord):
    if path.endswith("_slope"):
        return -SLOPE_LIMIT_DEGREES, SLOPE_LIMIT_DEGREES
    if path.endswith(POSITIVE_LENGTH_SUFFIXES):
        minimum_si = max(chord * MINIMUM_POSITIVE_LENGTH_CHORD, 1e-9)
        return parameter.unit.from_si_value(minimum_si), None
    return None, None


def _robust_least_squares_cost(residuals):
    scaled_squared = (residuals / ROBUST_LOSS_SCALE) ** 2
    return float(
        ROBUST_LOSS_SCALE**2
        * np.sum(np.sqrt(1.0 + scaled_squared) - 1.0)
    )


def _points_from_geometry(geometry):
    if geometry is None:
        return np.empty((0, 2), dtype=float)

    try:
        array = np.asarray(geometry, dtype=float)
    except (TypeError, ValueError):
        return np.empty((0, 2), dtype=float)

    if array.ndim != 2:
        return np.empty((0, 2), dtype=float)
    if array.shape[1] == 2:
        points = array
    elif array.shape[0] >= 2:
        points = array[:2].T
    else:
        return np.empty((0, 2), dtype=float)
    return points[np.isfinite(points).all(axis=1)]


def _resample_curve(points, count=SAMPLE_COUNT):
    """Resample an ordered curve at equal arc-length intervals."""
    points = _points_from_geometry(points)
    if len(points) < 2:
        raise ValueError("Each spline needs at least two finite XY points.")

    keep = np.concatenate(
        ([True], np.linalg.norm(np.diff(points, axis=0), axis=1) > 1e-12)
    )
    points = points[keep]
    if len(points) < 2:
        raise ValueError("A spline cannot consist of duplicate points only.")

    distances = np.concatenate(
        ([0.0], np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1)))
    )
    if distances[-1] <= 1e-12:
        raise ValueError("A spline must have non-zero length.")

    sample_distances = np.linspace(0.0, distances[-1], count)
    return np.column_stack((
        np.interp(sample_distances, distances, points[:, 0]),
        np.interp(sample_distances, distances, points[:, 1]),
    ))


def _parametric_spline(points):
    points = _points_from_geometry(points)
    if len(points) < 2:
        raise ValueError("Each spline needs at least two finite XY points.")

    keep = np.concatenate(
        ([True], np.linalg.norm(np.diff(points, axis=0), axis=1) > 1e-12)
    )
    points = points[keep]
    if len(points) < 2:
        raise ValueError("A spline cannot consist of duplicate points only.")

    parameter = np.concatenate((
        [0.0],
        np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1)),
    ))
    return PchipInterpolator(parameter, points, axis=0)


def _nearest_points_on_spline(query_points, spline, sample_count):
    """Project points onto a continuous spline, refining a sampled nearest segment."""
    parameters = np.linspace(spline.x[0], spline.x[-1], sample_count)
    samples = spline(parameters)
    segments = np.diff(samples, axis=0)
    offsets = query_points[:, None, :] - samples[None, :-1, :]
    fractions = np.sum(offsets * segments[None, :, :], axis=2)
    fractions /= np.maximum(
        np.sum(segments * segments, axis=1)[None, :], 1e-24
    )
    fractions = np.clip(fractions, 0.0, 1.0)
    projections = samples[None, :-1, :] + fractions[:, :, None] * segments[None, :, :]
    distances_squared = np.sum(
        (query_points[:, None, :] - projections) ** 2, axis=2
    )
    segment_indices = np.argmin(distances_squared, axis=1)
    rows = np.arange(len(query_points))

    lower = parameters[segment_indices]
    upper = parameters[segment_indices + 1]
    parameter = lower + fractions[rows, segment_indices] * (upper - lower)
    first_derivative = spline.derivative()
    second_derivative = first_derivative.derivative()
    for _ in range(8):
        curve_points = spline(parameter)
        first = first_derivative(parameter)
        second = second_derivative(parameter)
        delta = curve_points - query_points
        gradient = np.sum(delta * first, axis=1)
        curvature = np.sum(first * first + delta * second, axis=1)
        valid = np.abs(curvature) > 1e-12
        step = np.zeros_like(parameter)
        step[valid] = gradient[valid] / curvature[valid]
        parameter_next = np.clip(parameter - step, lower, upper)
        if np.max(np.abs(parameter_next - parameter)) <= 1e-12:
            parameter = parameter_next
            break
        parameter = parameter_next

    candidate_parameters = np.column_stack((
        parameter,
        lower,
        upper,
        parameters[segment_indices],
    ))
    candidate_points = spline(candidate_parameters)
    candidate_distances_squared = np.sum(
        (candidate_points - query_points[:, None, :]) ** 2,
        axis=2,
    )
    best_candidates = np.argmin(candidate_distances_squared, axis=1)
    nearest_points = candidate_points[rows, best_candidates]
    distances = np.linalg.norm(query_points - nearest_points, axis=1)
    return nearest_points, distances


def _component_curves(airfoil):
    curves = {}
    for name in REGION_NAMES:
        component = getattr(airfoil, name, None)
        spline = getattr(component, "spline", None)
        if spline is None:
            spline = getattr(airfoil, f"{name.lower()}_spline", None)
        points = _points_from_geometry(getattr(spline, "geom", None))
        if len(points) < 2:
            return None
        curves[name] = points
    return curves


def _contour_surfaces(reference, pressure_side_up):
    points = _points_from_geometry(getattr(reference, "curve", None))
    if len(points) < 4:
        raise ValueError(
            "The selected reference must contain spline geometry or an XY contour."
        )

    leading_edge_index = int(np.argmin(points[:, 0]))
    split_index = (
        int(np.argmax(points[:, 0]))
        if leading_edge_index in (0, len(points) - 1)
        else leading_edge_index
    )
    first_side = points[:split_index + 1]
    second_side = points[split_index:]
    if min(len(first_side), len(second_side)) < 2:
        raise ValueError("The reference contour does not form two usable surfaces.")

    if np.mean(first_side[:, 1]) >= np.mean(second_side[:, 1]):
        upper, lower = first_side, second_side
    else:
        upper, lower = second_side, first_side
    if upper[0, 0] > upper[-1, 0]:
        upper = upper[::-1]
    if lower[0, 0] > lower[-1, 0]:
        lower = lower[::-1]
    return (upper, lower) if pressure_side_up else (lower, upper)


def _surface_range(points, low_x, high_x):
    """Sample a continuous, shape-preserving cubic surface over an X interval."""
    ordered = points[np.argsort(points[:, 0])]
    x_values, indices = np.unique(ordered[:, 0], return_index=True)
    if len(x_values) < 2:
        raise ValueError("Each airfoil surface must span multiple X positions.")
    low_x = max(float(low_x), float(x_values[0]))
    high_x = min(float(high_x), float(x_values[-1]))
    if high_x <= low_x:
        raise ValueError("The LE and TE positions leave an empty surface region.")

    unique_points = ordered[indices]
    surface = PchipInterpolator(x_values, unique_points[:, 1])
    sample_x = np.linspace(low_x, high_x, SURFACE_SAMPLE_COUNT)
    return np.column_stack((sample_x, surface(sample_x)))


def _orient_cap(cap, start, end):
    cap = _points_from_geometry(cap)
    if len(cap) < 2:
        raise ValueError("The reference LE and TE splines must contain two points.")
    forward_error = (
        np.linalg.norm(cap[0] - start) + np.linalg.norm(cap[-1] - end)
    )
    reverse_error = (
        np.linalg.norm(cap[-1] - start) + np.linalg.norm(cap[0] - end)
    )
    return cap if forward_error <= reverse_error else cap[::-1]


def _divide_curves(airfoil, boundaries, pressure_side_up):
    raw_curves = _component_curves(airfoil)
    if raw_curves is None:
        pressure_side, suction_side = _contour_surfaces(
            airfoil, pressure_side_up
        )
        le_cap = None
        te_cap = None
    else:
        pressure_side = raw_curves["PS"]
        suction_side = raw_curves["SS"]
        if pressure_side[0, 0] > pressure_side[-1, 0]:
            pressure_side = pressure_side[::-1]
        if suction_side[0, 0] > suction_side[-1, 0]:
            suction_side = suction_side[::-1]
        le_cap = raw_curves["LE"]
        te_cap = raw_curves["TE"]

    x_min = min(float(np.min(pressure_side[:, 0])), float(np.min(suction_side[:, 0])))
    x_max = max(float(np.max(pressure_side[:, 0])), float(np.max(suction_side[:, 0])))
    chord = x_max - x_min
    if chord <= 1e-12:
        raise ValueError("The airfoil contour has zero chord length.")

    le_pressure, le_suction, te_pressure, te_suction = boundaries
    le_pressure_x = x_min + le_pressure * chord
    le_suction_x = x_min + le_suction * chord
    te_pressure_x = x_min + te_pressure * chord
    te_suction_x = x_min + te_suction * chord

    ps_le = _surface_range(pressure_side, x_min, le_pressure_x)
    ss_le = _surface_range(suction_side, x_min, le_suction_x)
    ps_te = _surface_range(pressure_side, te_pressure_x, x_max)
    ss_te = _surface_range(suction_side, te_suction_x, x_max)
    ps_mid = _surface_range(pressure_side, le_pressure_x, te_pressure_x)
    ss_mid = _surface_range(suction_side, le_suction_x, te_suction_x)

    if le_cap is not None:
        le_cap = _orient_cap(le_cap, ps_le[0], ss_le[0])
        te_cap = _orient_cap(te_cap, ps_te[-1], ss_te[-1])

    le_region = np.vstack((
        ps_le[::-1],
        le_cap[1:] if le_cap is not None else np.empty((0, 2)),
        ss_le[1:],
    ))
    te_region = np.vstack((
        ps_te,
        te_cap[1:] if te_cap is not None else np.empty((0, 2)),
        ss_te[::-1][1:],
    ))
    return {
        "PS": ps_mid,
        "SS": ss_mid,
        "LE": le_region,
        "TE": te_region,
    }, chord


def _airfoil_parameters(airfoil):
    parameters = {}
    for component_name in ("", "LE", "TE", "PS", "SS"):
        component = airfoil if not component_name else getattr(airfoil, component_name)
        for key, parameter in component.params.items():
            if component_name in ("LE", "TE") and key in ("ps_wedge", "ss_wedge"):
                continue
            path = f"{component_name}.{key}" if component_name else key
            parameters[path] = parameter
    return parameters


def _get_parameter(airfoil, path):
    component_name, separator, key = path.partition(".")
    if not separator:
        key = component_name
        component = airfoil
    else:
        component = getattr(airfoil, component_name)
    return component.params[key]


def _parse_parameter_bounds(path, minimum_text, maximum_text):
    bounds = []
    for label, text in (("Minimum", minimum_text), ("Maximum", maximum_text)):
        text = text.strip()
        if not text:
            bounds.append(None)
            continue
        try:
            value = float(text)
        except ValueError as error:
            raise ValueError(f"{label} bound for {path} must be numeric.") from error
        if not math.isfinite(value):
            raise ValueError(f"{label} bound for {path} must be finite.")
        bounds.append(value)

    minimum, maximum = bounds
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ValueError(f"Minimum bound for {path} cannot exceed its maximum.")
    return minimum, maximum


def _distance_statistics(comparison):
    statistics = {}
    for name in RESIDUAL_REGION_NAMES:
        distances = comparison[name][2]
        statistics[name] = (
            float(np.min(distances)),
            float(np.max(distances)),
            float(np.mean(distances)),
        )
    return statistics


def _normalized_color(color):
    return tuple(int(color[index:index + 2], 16) / 255 for index in (1, 3, 5))


class AirfoilFit:
    """Joint least-squares fit of selected parameters across four spline regions."""

    def __init__(
        self,
        airfoil,
        reference,
        boundaries,
        variable_paths,
        parameter_bounds,
        iteration_limit,
    ):
        self.airfoil = airfoil
        self.reference = reference
        self.boundaries = boundaries
        self.pressure_side_up = getattr(airfoil, "_is_pressure_side_up", True)
        self.variable_paths = tuple(variable_paths)

        self.parameters = {
            path: _get_parameter(airfoil, path) for path in self.variable_paths
        }
        initial_values = {
            path: parameter.get() for path, parameter in self.parameters.items()
        }
        self.parameter_bounds = {}
        for path in self.variable_paths:
            minimum, maximum = parameter_bounds.get(path, (None, None))
            if (
                (minimum is not None and not math.isfinite(minimum))
                or (maximum is not None and not math.isfinite(maximum))
            ):
                raise ValueError(f"Bounds for {path} must be finite.")
            if minimum is not None and maximum is not None and minimum > maximum:
                raise ValueError(
                    f"Minimum bound for {path} cannot exceed its maximum."
                )
            self.parameter_bounds[path] = (minimum, maximum)
        self.values = dict(initial_values)
        self.boundary_limits = tuple(boundaries)
        self.boundary_ranges = tuple(
            (0.0001, limit) if index < 2 else (limit, 0.9999)
            for index, limit in enumerate(self.boundary_limits)
        )
        self.values.update(dict(zip(BOUNDARY_KEYS, boundaries)))
        self.reference_groups = _divide_curves(
            self.reference, self.boundaries, self.pressure_side_up
        )[0]
        self.reference_chord = float(np.ptp(np.vstack(
            list(self.reference_groups.values())
        )[:, 0]))
        if self.reference_chord <= 1e-12:
            raise ValueError("The reference has zero chord length.")
        for path, parameter in self.parameters.items():
            minimum, maximum = self.parameter_bounds[path]
            automatic_minimum, automatic_maximum = _automatic_parameter_bounds(
                path, parameter, self.reference_chord
            )
            if automatic_minimum is not None:
                minimum = max(
                    automatic_minimum,
                    -math.inf if minimum is None else minimum,
                )
            if automatic_maximum is not None:
                maximum = min(
                    automatic_maximum,
                    math.inf if maximum is None else maximum,
                )
            if minimum is not None and maximum is not None and minimum > maximum:
                raise ValueError(
                    f"Bounds for {path} do not overlap its safe fitting range."
                )
            self.parameter_bounds[path] = minimum, maximum
            if minimum is not None:
                self.values[path] = max(self.values[path], minimum)
            if maximum is not None:
                self.values[path] = min(self.values[path], maximum)
        self.initial_values = dict(self.values)
        self.iteration_limit = max(1, int(iteration_limit))
        self.iterations = 0
        self.evaluations = 0
        self.finished = False
        self.anchor_error = math.inf
        self.comparison = None
        self.best_score = None
        self._update_geometry()
        self.comparison = self._measure()
        self.anchor_error = self._anchor_error()
        self.best_score = None
        self.residual_history = []
        self._record_residuals()

    def _update_geometry(self):
        for path, value in self.values.items():
            parameter = self.parameters.get(path)
            if parameter is not None:
                parameter.set(value)
        self.airfoil.update()

    def _active_boundaries(self):
        return tuple(self.values[key] for key in BOUNDARY_KEYS)

    def _measure(self):
        reference_groups, _ = _divide_curves(
            self.reference, self._active_boundaries(), self.pressure_side_up
        )
        current_groups, _ = _divide_curves(
            self.airfoil, self._active_boundaries(), self.pressure_side_up
        )
        comparison = {}
        for name in REGION_NAMES:
            reference_points = _resample_curve(
                reference_groups[name], SURFACE_SAMPLE_COUNT
            )
            current_points = _resample_curve(current_groups[name])
            reference_spline = _parametric_spline(reference_groups[name])
            current_spline = _parametric_spline(current_groups[name])
            current_projection, current_distances = _nearest_points_on_spline(
                current_points, reference_spline, SURFACE_SAMPLE_COUNT
            )
            reference_projection, reference_distances = _nearest_points_on_spline(
                reference_points, current_spline, SAMPLE_COUNT
            )
            connector_segments = np.concatenate((
                np.stack((current_points, current_projection), axis=1),
                np.stack((reference_points, reference_projection), axis=1),
            ))
            distances = np.concatenate((current_distances, reference_distances))
            comparison[name] = (
                reference_points,
                current_points,
                distances,
                connector_segments,
            )
        return comparison

    def _anchor_error(self):
        squared_distances = []
        for reference_points, current_points, *_ in self.comparison.values():
            squared_distances.extend((
                float(np.sum((reference_points[0] - current_points[0]) ** 2)),
                float(np.sum((reference_points[-1] - current_points[-1]) ** 2)),
            ))
        return math.sqrt(float(np.mean(squared_distances)))

    def _residual_vector(self, comparison):
        residuals = []
        for name in RESIDUAL_REGION_NAMES:
            distances = comparison[name][2] / self.reference_chord
            residuals.append(
                distances
                * math.sqrt(REGION_RESIDUAL_WEIGHTS[name])
            )

        reference_te, current_te = comparison["TE"][:2]
        anchor_residuals = np.concatenate((
            current_te[0] - reference_te[0],
            current_te[-1] - reference_te[-1],
        )) / self.reference_chord
        residuals.append(anchor_residuals * TE_ANCHOR_RESIDUAL_WEIGHT)
        return np.concatenate(residuals)

    def _record_residuals(self):
        all_distances = np.concatenate([
            values[2] for values in self.comparison.values()
        ])
        mean_distance = float(np.mean(all_distances))
        statistics = _distance_statistics(self.comparison)
        mean_spread = float(np.mean([
            values[1] - values[0] for values in statistics.values()
        ]))
        residuals = [
            self.iterations,
            mean_distance / self.reference_chord,
            mean_spread / self.reference_chord,
            self.anchor_error / self.reference_chord,
        ]
        for name in RESIDUAL_REGION_NAMES:
            residuals.extend(
                value / self.reference_chord
                for value in statistics[name]
            )
        self.residual_history.append(tuple(residuals))

    def optimize(self, is_cancelled=None):
        """Fit all selected parameters together against all four spline regions."""
        paths = self.variable_paths + BOUNDARY_KEYS
        initial_values = dict(self.values)
        for key in BOUNDARY_KEYS:
            initial_values.setdefault(key, self.boundaries[BOUNDARY_KEYS.index(key)])

        variable_paths = []
        lower_bounds = []
        upper_bounds = []
        fixed_values = {}
        for path in paths:
            if path in BOUNDARY_KEYS:
                lower, upper = self.boundary_ranges[BOUNDARY_KEYS.index(path)]
            else:
                lower, upper = self.parameter_bounds[path]
                lower = -math.inf if lower is None else lower
                upper = math.inf if upper is None else upper
            if lower == upper:
                fixed_values[path] = lower
                initial_values[path] = lower
                self.values[path] = lower
                continue
            variable_paths.append(path)
            lower_bounds.append(lower)
            upper_bounds.append(upper)

        lower_bounds = np.asarray(lower_bounds, dtype=float)
        upper_bounds = np.asarray(upper_bounds, dtype=float)
        initial = np.asarray(
            [initial_values[path] for path in variable_paths], dtype=float
        )
        initial = np.minimum(np.maximum(initial, lower_bounds), upper_bounds)
        finite_lower = np.isfinite(lower_bounds)
        finite_upper = np.isfinite(upper_bounds)
        initial[finite_lower] = np.maximum(
            initial[finite_lower],
            np.nextafter(
                lower_bounds[finite_lower], upper_bounds[finite_lower]
            ),
        )
        initial[finite_upper] = np.minimum(
            initial[finite_upper],
            np.nextafter(
                upper_bounds[finite_upper], lower_bounds[finite_upper]
            ),
        )
        scales = np.asarray([
            0.01 if path in BOUNDARY_KEYS else _parameter_search_scale(
                path,
                self.parameters[path],
                self.reference_chord,
            )
            for path in variable_paths
        ])
        residual_count = len(self._residual_vector(self.comparison))
        last_feasible_values = initial.copy()
        best_values = initial.copy()
        best_comparison = self.comparison
        best_cost = math.inf

        def apply_values(vector):
            for path, value in fixed_values.items():
                self.values[path] = value
            for path, value in zip(variable_paths, vector):
                self.values[path] = float(value)
            self._update_geometry()

        def calculate_residuals(vector):
            nonlocal last_feasible_values, best_values, best_comparison, best_cost
            if is_cancelled is not None and is_cancelled():
                raise InterruptedError("Airfoil fitting was cancelled.")
            if self.evaluations >= self.iteration_limit:
                raise _FitEvaluationLimit
            self.evaluations += 1
            self.iterations = self.evaluations

            try:
                apply_values(vector)
                if getattr(self.airfoil, "has_self_intersection", False):
                    raise ValueError("The trial airfoil contour self-intersects.")
                comparison = self._measure()
            except (ValueError, FloatingPointError, OverflowError):
                apply_values(last_feasible_values)
                distance_from_feasible = float(np.linalg.norm(
                    (vector - last_feasible_values) / scales
                ))
                return np.full(
                    residual_count,
                    0.1 + distance_from_feasible,
                    dtype=float,
                )

            last_feasible_values = vector.copy()
            self.comparison = comparison
            self.anchor_error = self._anchor_error()
            residuals = self._residual_vector(comparison)
            cost = _robust_least_squares_cost(residuals)
            if cost < best_cost:
                best_cost = cost
                best_values = vector.copy()
                best_comparison = comparison
            self.best_score = cost
            self._record_residuals()
            return residuals

        if variable_paths:
            try:
                least_squares(
                    calculate_residuals,
                    initial,
                    bounds=(lower_bounds, upper_bounds),
                    x_scale=scales,
                    max_nfev=self.iteration_limit,
                    loss="soft_l1",
                    f_scale=ROBUST_LOSS_SCALE,
                    ftol=1e-9,
                    xtol=1e-9,
                    gtol=1e-9,
                )
            except _FitEvaluationLimit:
                pass
            if is_cancelled is not None and is_cancelled():
                raise InterruptedError("Airfoil fitting was cancelled.")
        else:
            calculate_residuals(initial)

        if not math.isfinite(best_cost):
            raise RuntimeError("The optimizer could not find a valid airfoil shape.")
        apply_values(best_values)
        self.comparison = best_comparison
        self.anchor_error = self._anchor_error()
        self.best_score = best_cost
        self.finished = True


class _FitWorker(QThread):
    def __init__(self, fit, parent=None):
        super().__init__(parent)
        self.fit = fit
        self.error = None
        self.cancelled = False

    def run(self):
        try:
            self.fit.optimize(self.isInterruptionRequested)
        except InterruptedError:
            self.cancelled = True
        except Exception as error:
            self.error = error
            logger.exception("Airfoil least-squares fitting failed.")


class Fit2RefWindow(QDialog):
    """Anchor and fit the current airfoil against a selected reference."""

    def __init__(
        self,
        parent=None,
        current_airfoil=None,
        reference_airfoil=None,
        airfoil_designer=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Fit Airfoil to Reference")
        self.resize(1400, 950)
        self.current_airfoil = current_airfoil
        self.airfoil_designer = airfoil_designer or parent
        self.project = getattr(self.airfoil_designer, "PROJECT", None)
        self.reference_airfoil = reference_airfoil
        self.fit = None
        self._worker = None
        self._running = False
        self._cancel_pending = False
        self._parameter_paths = []
        self._settings = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            "7kStudio",
            "Daedalus",
        )
        self._fit_preferences = self._load_fit_preferences()

        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._run_fit_batch)

        layout = QVBoxLayout(self)
        columns = QSplitter(Qt.Orientation.Horizontal)
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)

        reference_layout = QHBoxLayout()
        reference_layout.addWidget(QLabel("Reference airfoil:"))
        self.reference_combo = QComboBox()
        reference_layout.addWidget(self.reference_combo, 1)
        self.add_reference_button = QPushButton("Add reference…")
        self.add_reference_button.clicked.connect(self._add_reference)
        reference_layout.addWidget(self.add_reference_button)
        left_layout.addLayout(reference_layout)

        boundary_group = QGroupBox("LE / TE definitions")
        boundary_layout = QGridLayout()
        boundary_group.setLayout(boundary_layout)
        self.boundary_spins = []
        boundary_labels = (
            ("LE pressure-side position (%)", 7.0),
            ("LE suction-side position (%)", 7.0),
            ("TE pressure-side position (%)", 93.0),
            ("TE suction-side position (%)", 93.0),
        )
        for index, (label, value) in enumerate(boundary_labels):
            spin = QDoubleSpinBox()
            spin.setRange(0.01, 99.99)
            spin.setDecimals(2)
            spin.setSingleStep(0.5)
            spin.setValue(value)
            self.boundary_spins.append(spin)
            boundary_layout.addWidget(QLabel(label), index // 2, (index % 2) * 2)
            boundary_layout.addWidget(spin, index // 2, (index % 2) * 2 + 1)
        boundary_layout.addWidget(
            QLabel("Chord percentages: 0% at LE, 100% at TE."),
            2,
            0,
            1,
            4,
        )
        left_layout.addWidget(boundary_group)

        preview_group = QGroupBox(
            "Reference curve division and point-to-curve fit preview"
        )
        preview_layout = QVBoxLayout(preview_group)
        preview_program = getattr(self.airfoil_designer, "PROGRAM", None)
        self.preview_project = SimpleNamespace(reference_airfoils=[])
        self.preview_viewport = None
        self._preview_regions = {}
        self._preview_camera_reference = None
        if preview_program is None:
            preview_layout.addWidget(QLabel(
                "OpenGL preview is unavailable without the Airfoil Designer."
            ))
        else:
            self.preview_viewport = ViewportOpenGL(
                program=preview_program,
                project=self.preview_project,
                parent=preview_group,
            )
            self.preview_viewport.setMinimumSize(320, 300)
            preview_layout.addWidget(self.preview_viewport)
        left_layout.addWidget(preview_group, 1)

        iteration_layout = QHBoxLayout()
        iteration_layout.addWidget(QLabel("Maximum optimizer evaluations:"))
        self.iterations_spin = QSpinBox()
        self.iterations_spin.setRange(1, 100000)
        self.iterations_spin.setValue(1000)
        iteration_layout.addWidget(self.iterations_spin)
        iteration_layout.addStretch()
        right_layout.addLayout(iteration_layout)

        right_splitter = QSplitter(Qt.Orientation.Vertical)
        parameter_group = QGroupBox("Parameter specification")
        parameter_layout = QVBoxLayout(parameter_group)
        self.parameter_table = QTableWidget(0, 6)
        self.parameter_table.setHorizontalHeaderLabels(
            ["Fit", "Parameter", "Unit", "Current value", "Min value", "Max value"]
        )
        self.parameter_table.horizontalHeader().setStretchLastSection(True)
        parameter_layout.addWidget(self.parameter_table)
        parameter_layout.addWidget(QLabel(
            "Automatic guards: spline slopes stay within ±60° and tangent/"
            "curvature lengths stay positive. TE parameters use smaller search "
            "steps; TE endpoints are anchored explicitly."
        ))
        right_splitter.addWidget(parameter_group)

        process_group = QGroupBox("Step checklist")
        process_layout = QVBoxLayout(process_group)
        self.process_checks = []
        for text in (
            "Reference division ready",
            "Joint four-spline fit",
            "All region averages ≤ 0.01 chord",
        ):
            check = QCheckBox(text)
            check.setEnabled(False)
            process_layout.addWidget(check)
            self.process_checks.append(check)
        right_splitter.addWidget(process_group)

        residual_group = QGroupBox("Fit residuals by optimizer evaluation")
        residual_layout = QVBoxLayout(residual_group)
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.residual_axes = self.figure.add_subplot(111)
        self.residual_axes.set_title("Normalized residuals by iteration")
        self.residual_axes.set_xlabel("Objective evaluation")
        self.residual_axes.set_ylabel("Distance / reference chord")
        self.residual_axes.grid(True, alpha=0.3)
        self.residual_lines = {
            "Average distance": self.residual_axes.plot(
                [], [], color="#222222", label="Overall average"
            )[0],
            "Mean max−min spread": self.residual_axes.plot(
                [], [], color="#777777", linestyle="--", label="Mean max−min spread"
            )[0],
            "Anchor RMS": self.residual_axes.plot(
                [], [], color="#aaaaaa", linestyle=":", label="Anchor RMS"
            )[0],
        }
        statistic_styles = {
            "minimum": ":",
            "maximum": "--",
            "average": "-",
        }
        for region in RESIDUAL_REGION_NAMES:
            for statistic in RESIDUAL_STATISTICS:
                label = f"{region} {statistic} distance"
                self.residual_lines[label] = self.residual_axes.plot(
                    [],
                    [],
                    color=REGION_COLORS[region],
                    linestyle=statistic_styles[statistic],
                    label=label,
                )[0]
        self.residual_axes.legend(loc="best", fontsize="x-small", ncol=3)
        self.canvas.setMinimumHeight(180)
        residual_layout.addWidget(self.canvas)
        right_splitter.addWidget(residual_group)

        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(
            ["Spline region", "Min distance", "Max distance", "Average distance"]
        )
        self.results_table.horizontalHeader().setStretchLastSection(True)
        output_layout.addWidget(self.results_table)
        right_splitter.addWidget(output_group)
        right_splitter.setSizes([260, 100, 320, 180])
        right_layout.addWidget(right_splitter, 1)

        columns.addWidget(left_column)
        columns.addWidget(right_column)
        columns.setStretchFactor(0, 1)
        columns.setStretchFactor(1, 1)
        columns.setSizes([600, 700])
        layout.addWidget(columns, 1)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.proceed_button = QPushButton("Proceed")
        self.proceed_button.clicked.connect(self._proceed_clicked)
        button_layout.addWidget(self.proceed_button)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self._close_dialog)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        self.reference_combo.currentIndexChanged.connect(
            self._reference_selection_changed
        )
        for spin in self.boundary_spins:
            spin.valueChanged.connect(self._refresh_reference_preview)
        saved_boundaries = self._fit_preferences.get("boundaries", [])
        if (
            isinstance(saved_boundaries, list)
            and len(saved_boundaries) == len(self.boundary_spins)
            and all(
                isinstance(value, (int, float)) and math.isfinite(value)
                for value in saved_boundaries
            )
        ):
            for spin, value in zip(self.boundary_spins, saved_boundaries):
                spin.setValue(value)
        self._populate_reference_combo()
        self._populate_parameter_table()
        self._show_empty_preview()
        self._refresh_reference_preview()
        QTimer.singleShot(
            0,
            lambda: self._fit_preview_camera(self.reference_combo.currentData()),
        )
        self._update_controls()
        self.finished.connect(self._save_fit_preferences)

    def _load_fit_preferences(self):
        raw_preferences = self._settings.value(FIT_SETTINGS_KEY, "")
        if not raw_preferences:
            return {}
        try:
            preferences = json.loads(str(raw_preferences))
        except (TypeError, ValueError):
            logger.warning("Ignoring invalid saved airfoil-fitting preferences.")
            return {}
        if not isinstance(preferences, dict):
            logger.warning("Ignoring malformed saved airfoil-fitting preferences.")
            return {}
        version = preferences.get("version", 1)
        if not isinstance(version, int):
            version = 1
        if version < 2:
            saved_parameters = preferences.get("parameters", {})
            if isinstance(saved_parameters, dict):
                te_thickness = saved_parameters.get("TE_thickness", {})
                if isinstance(te_thickness, dict):
                    te_thickness["checked"] = True
                else:
                    saved_parameters["TE_thickness"] = {"checked": True}
                preferences["parameters"] = saved_parameters
            version = 2
        if version < 3:
            saved_parameters = preferences.get("parameters", {})
            if isinstance(saved_parameters, dict):
                for path, saved_parameter in saved_parameters.items():
                    if (
                        path.endswith(POSITIVE_LENGTH_SUFFIXES)
                        and isinstance(saved_parameter, dict)
                    ):
                        minimum = saved_parameter.get("minimum")
                        if minimum in (0, 0.0, "0", "0.0", "0.00"):
                            saved_parameter["minimum"] = ""
            preferences["parameters"] = saved_parameters
            version = 3
        preferences["version"] = version
        return preferences

    def _save_fit_preferences(self, *_):
        parameters = {}
        for row, path in enumerate(self._parameter_paths):
            parameters[path] = {
                "checked": (
                    self.parameter_table.item(row, 0).checkState()
                    == Qt.CheckState.Checked
                ),
                "minimum": self.parameter_table.item(row, 4).text(),
                "maximum": self.parameter_table.item(row, 5).text(),
            }
        reference = self.reference_combo.currentData()
        preferences = {
            "version": 3,
            "parameters": parameters,
            "reference": getattr(reference, "name", None),
            "boundaries": [spin.value() for spin in self.boundary_spins],
        }
        self._settings.setValue(FIT_SETTINGS_KEY, json.dumps(preferences))
        self._settings.sync()
        if self._settings.status() != QSettings.Status.NoError:
            logger.error("Could not save airfoil-fitting preferences.")

    def _populate_reference_combo(self):
        selected_reference = self.reference_airfoil
        references = list(getattr(self.project, "reference_airfoils", []))
        if selected_reference is None:
            saved_name = self._fit_preferences.get("reference")
            if isinstance(saved_name, str):
                selected_reference = next(
                    (
                        reference for reference in references
                        if getattr(reference, "name", None) == saved_name
                    ),
                    None,
                )
        if selected_reference is not None and all(
            reference is not selected_reference for reference in references
        ):
            references.insert(0, selected_reference)

        blocked = self.reference_combo.blockSignals(True)
        self.reference_combo.clear()
        self.reference_combo.addItem("Select a reference…", None)
        selected_index = 0
        for index, reference in enumerate(references, start=1):
            self.reference_combo.addItem(
                getattr(reference, "name", f"Reference {index}"), reference
            )
            if reference is selected_reference:
                selected_index = index
        self.reference_combo.setCurrentIndex(selected_index)
        self.reference_combo.blockSignals(blocked)
        self.reference_airfoil = self.reference_combo.currentData()

    def _populate_parameter_table(self):
        if self.current_airfoil is None:
            return
        parameters = _airfoil_parameters(self.current_airfoil)
        saved_parameters = self._fit_preferences.get("parameters", {})
        if not isinstance(saved_parameters, dict):
            logger.warning("Ignoring malformed saved airfoil parameter preferences.")
            saved_parameters = {}
        reference = self.reference_combo.currentData()
        chord = _airfoil_chord(reference) if reference is not None else None
        if chord is None:
            chord = _airfoil_chord(self.current_airfoil) or 1.0
        self._parameter_paths = list(parameters)
        self.parameter_table.setRowCount(len(parameters))
        for row, (path, parameter) in enumerate(parameters.items()):
            saved_parameter = saved_parameters.get(path, {})
            if not isinstance(saved_parameter, dict):
                saved_parameter = {}
            enabled = QTableWidgetItem()
            enabled.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable
            )
            enabled.setCheckState(
                Qt.CheckState.Checked
                if saved_parameter.get(
                    "checked", True
                ) is True
                else Qt.CheckState.Unchecked
            )
            self.parameter_table.setItem(row, 0, enabled)
            self.parameter_table.setItem(row, 1, QTableWidgetItem(path))
            self.parameter_table.setItem(
                row, 2, QTableWidgetItem(getattr(parameter.unit, "name", ""))
            )
            value = parameter.get()
            current_item = QTableWidgetItem(f"{value:.8g}")
            current_item.setFlags(current_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.parameter_table.setItem(row, 3, current_item)
            default_minimum, default_maximum = _automatic_parameter_bounds(
                path, parameter, chord
            )
            minimum = saved_parameter.get("minimum")
            maximum = saved_parameter.get("maximum")
            if minimum in (None, ""):
                minimum = (
                    f"{default_minimum:.8g}"
                    if default_minimum is not None
                    else ""
                )
            if maximum in (None, ""):
                maximum = (
                    f"{default_maximum:.8g}"
                    if default_maximum is not None
                    else ""
                )
            self.parameter_table.setItem(
                row, 4, QTableWidgetItem(str(minimum) if minimum is not None else "")
            )
            self.parameter_table.setItem(
                row, 5, QTableWidgetItem(str(maximum) if maximum is not None else "")
            )
        self.parameter_table.resizeColumnsToContents()

    def _selected_parameters(self):
        selected = []
        parameter_bounds = {}
        for row, path in enumerate(self._parameter_paths):
            if self.parameter_table.item(row, 0).checkState() != Qt.CheckState.Checked:
                continue
            selected.append(path)
            parameter_bounds[path] = _parse_parameter_bounds(
                path,
                self.parameter_table.item(row, 4).text(),
                self.parameter_table.item(row, 5).text(),
            )
        return selected, parameter_bounds

    def _boundaries(self):
        le_pressure, le_suction, te_pressure, te_suction = (
            spin.value() / 100.0 for spin in self.boundary_spins
        )
        if le_pressure >= te_pressure or le_suction >= te_suction:
            raise ValueError("Each LE position must be before its TE position.")
        return le_pressure, le_suction, te_pressure, te_suction

    def _refresh_reference_preview(self, *_):
        reference = self.reference_combo.currentData()
        self._reference_preview_valid = False
        self._preview_regions = {}
        if reference is None:
            if self.preview_viewport is not None:
                self.preview_viewport.setToolTip("Select a reference airfoil.")
        else:
            try:
                curves, _ = _divide_curves(
                    reference,
                    self._boundaries(),
                    getattr(self.current_airfoil, "_is_pressure_side_up", True),
                )
                self._preview_regions = curves
                self._reference_preview_valid = True
                if self.preview_viewport is not None:
                    self.preview_viewport.setToolTip(
                        "Colored curves show the LE, TE, pressure-side, and "
                        "suction-side divisions. Fit connectors appear after "
                        "starting the fit."
                    )
            except (AttributeError, TypeError, ValueError) as error:
                if self.preview_viewport is not None:
                    self.preview_viewport.setToolTip(str(error))
                self.status_label.setText(f"Reference preview unavailable: {error}")
        self._sync_preview_viewport()
        self._update_process_checks()
        self._update_controls()

    def _fit_preview_camera(self, reference):
        viewport = self.preview_viewport
        if viewport is None:
            return

        point_sets = []
        reference_points = _points_from_geometry(
            getattr(reference, "curve", None)
        )
        if len(reference_points):
            point_sets.append(reference_points)
        airfoil_curves = _component_curves(self.current_airfoil)
        if airfoil_curves:
            point_sets.extend(airfoil_curves.values())
        reference_curves = _component_curves(reference)
        if reference_curves:
            point_sets.extend(reference_curves.values())
        if not point_sets:
            return

        points = np.vstack(point_sets)
        x_min, y_min = np.min(points, axis=0)
        x_max, y_max = np.max(points, axis=0)
        aspect = viewport.width() / max(1, viewport.height())
        viewport.camera.center[:] = ((x_min + x_max) / 2, (y_min + y_max) / 2)
        viewport.camera.zoom = max(
            (x_max - x_min) / (2 * max(aspect, 0.1)),
            (y_max - y_min) / 2,
            0.01,
        ) * 1.15

    def _sync_preview_viewport(self, comparison=None):
        viewport = self.preview_viewport
        if viewport is None:
            return

        reference = self.reference_combo.currentData()
        if reference is not self._preview_camera_reference:
            self._fit_preview_camera(reference)
            self._preview_camera_reference = reference

        if reference is None:
            self.preview_project.reference_airfoils = []
        else:
            displayed_reference = copy(reference)
            displayed_reference.visible = True
            self.preview_project.reference_airfoils = [displayed_reference]

        preview_airfoil = (
            self.fit.airfoil
            if self.fit is not None and self._running
            else self.current_airfoil
        )
        viewport.set_airfoil_to_display(preview_airfoil)

        lines = [
            (
                self._preview_regions[name],
                _normalized_color(REGION_COLORS[name]),
                False,
                3.0 if name in ("LE", "TE") else 1.4,
            )
            for name in REGION_NAMES
            if name in self._preview_regions
        ]
        if comparison is not None:
            lines.extend(
                (
                    comparison[name][3][
                        np.linspace(
                            0,
                            len(comparison[name][3]) - 1,
                            min(100, len(comparison[name][3])),
                            dtype=int,
                        )
                    ],
                    _normalized_color(REGION_COLORS[name]),
                    True,
                    0.8,
                )
                for name in REGION_NAMES
            )
        viewport.set_preview_lines(lines)

    def _copy_airfoil_for_fit(self):
        from src.obj.class_airfoil import Airfoil

        source = self.current_airfoil
        clone = Airfoil(source.PROGRAM)
        clone.name = source.name
        clone.info = dict(source.info)
        clone._is_pressure_side_up = source._is_pressure_side_up
        for component_name in ("", "LE", "TE", "PS", "SS"):
            source_component = source if not component_name else getattr(
                source, component_name
            )
            target_component = clone if not component_name else getattr(
                clone, component_name
            )
            for key, parameter in source_component.params.items():
                if key in target_component.params:
                    target_parameter = target_component.params[key]
                    target_parameter.value = parameter.value
                    target_parameter.nominal = parameter.nominal
                    target_parameter.unit = parameter.unit
            for key, attribute in source_component.attrs.items():
                if key in target_component.attrs:
                    target_component.attrs[key].value = attribute.value
        clone.update()
        return clone

    def _proceed_clicked(self):
        if self.proceed_button.text() == "Done":
            self.accept()
            return
        if self._running:
            return

        reference = self.reference_combo.currentData()
        if reference is None:
            self._update_controls()
            return
        if self.current_airfoil is None:
            self.status_label.setText("No current airfoil is available.")
            return

        try:
            self.current_airfoil.update()
            boundaries = self._boundaries()
            paths, parameter_bounds = self._selected_parameters()
            fit_airfoil = self._copy_airfoil_for_fit()
            self.fit = AirfoilFit(
                fit_airfoil,
                reference,
                boundaries,
                paths,
                parameter_bounds,
                self.iterations_spin.value(),
            )
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            QMessageBox.warning(self, "Cannot start fit", str(error))
            self.status_label.setText(str(error))
            return
        except Exception:
            logger.exception("Could not initialize airfoil fitting")
            QMessageBox.critical(
                self,
                "Fit failed",
                "Could not initialize fitting. See the application log.",
            )
            self.status_label.setText("Could not initialize fitting; see the log.")
            return

        self._running = True
        self._cancel_pending = False
        self.proceed_button.setEnabled(False)
        self.close_button.setText("Cancel")
        self._set_fit_controls_enabled(False)
        self._worker = _FitWorker(self.fit, self)
        self._worker.finished.connect(self._fit_worker_finished)
        self._worker.start()
        self._update_process_checks()
        self._timer.start()
        self._show_fit_state()

    def _set_fit_controls_enabled(self, enabled):
        self.reference_combo.setEnabled(enabled)
        self.add_reference_button.setEnabled(enabled)
        self.parameter_table.setEnabled(enabled)
        self.iterations_spin.setEnabled(enabled)
        for spin in self.boundary_spins:
            spin.setEnabled(enabled)

    def _run_fit_batch(self):
        if self.fit is None:
            self._timer.stop()
            return
        self._draw_comparison(self.fit.comparison)
        self._show_results(self.fit.comparison)
        self._draw_residuals()
        self._refresh_parameter_values()
        self._show_fit_state()
        self._update_process_checks()

    def _fit_worker_finished(self):
        worker = self._worker
        if worker is None:
            return
        self._worker = None
        worker.deleteLater()
        self._timer.stop()
        self._running = False

        if self._cancel_pending or worker.cancelled:
            self.fit = None
            super().reject()
            return
        if worker.error is not None:
            self.fit = None
            self._sync_preview_viewport()
            self._set_fit_controls_enabled(True)
            self.close_button.setText("Close")
            self.proceed_button.setEnabled(True)
            self._update_process_checks()
            self.status_label.setText(
                "Fitting failed; see the application log for details."
            )
            QMessageBox.critical(
                self,
                "Fit failed",
                "The airfoil fit failed. See the application log for details.",
            )
            return

        original_values = {
            path: _get_parameter(self.current_airfoil, path).get()
            for path in self.fit.variable_paths
        }
        try:
            for path in self.fit.variable_paths:
                _get_parameter(self.current_airfoil, path).set(
                    self.fit.values[path]
                )
            self.current_airfoil.update()
        except Exception:
            logger.exception("Could not apply the fitted airfoil parameters.")
            for path, value in original_values.items():
                _get_parameter(self.current_airfoil, path).set(value)
            try:
                self.current_airfoil.update()
            except Exception:
                logger.exception("Could not restore the original airfoil after fitting.")
            self.fit = None
            self._set_fit_controls_enabled(True)
            self.close_button.setText("Close")
            self.proceed_button.setEnabled(True)
            self._update_process_checks()
            self.status_label.setText(
                "Could not apply fit results; see the application log."
            )
            QMessageBox.critical(
                self,
                "Fit failed",
                "Could not apply fit results. See the application log.",
            )
            return
        self.fit.airfoil = self.current_airfoil
        self.fit.parameters = {
            path: _get_parameter(self.current_airfoil, path)
            for path in self.fit.variable_paths
        }
        self.fit.comparison = self.fit._measure()
        self.fit.anchor_error = self.fit._anchor_error()
        self.fit.finished = True
        self._draw_comparison(self.fit.comparison)
        self._show_results(self.fit.comparison)
        self._draw_residuals()
        self._refresh_parameter_values()
        self._show_fit_state()
        self._update_process_checks()
        self.proceed_button.setText("Done")
        self.proceed_button.setEnabled(True)
        self.close_button.setText("Close")
        self._refresh_airfoil_views()

    def _update_process_checks(self):
        self.process_checks[0].setChecked(
            getattr(self, "_reference_preview_valid", False)
        )
        if self.fit is None:
            self.process_checks[1].setChecked(False)
            self.process_checks[2].setChecked(False)
            return
        self.process_checks[1].setChecked(self._running or self.fit.finished)
        self.process_checks[2].setChecked(all(
            values[2] / self.fit.reference_chord <= 0.01
            for values in _distance_statistics(self.fit.comparison).values()
        ))

    def _draw_residuals(self):
        if self.fit is None:
            return
        history = np.asarray(self.fit.residual_history, dtype=float)
        if history.ndim != 2 or not len(history):
            return
        series_names = [
            "Average distance",
            "Mean max−min spread",
            "Anchor RMS",
        ]
        series_names.extend(
            f"{region} {statistic} distance"
            for region in RESIDUAL_REGION_NAMES
            for statistic in RESIDUAL_STATISTICS
        )
        for column, name in enumerate(series_names, start=1):
            self.residual_lines[name].set_data(history[:, 0], history[:, column])
        self.residual_axes.relim()
        self.residual_axes.autoscale_view()
        self.canvas.draw_idle()

    def _refresh_parameter_values(self):
        for row, path in enumerate(self._parameter_paths):
            value = (
                self.fit.values.get(path)
                if self.fit is not None and self._running
                else _get_parameter(self.current_airfoil, path).get()
            )
            if value is None:
                continue
            self.parameter_table.item(row, 3).setText(f"{value:.8g}")

    def _show_fit_state(self):
        if self.fit is None:
            return
        if self._running:
            self.status_label.setText(
                "Jointly fitting all four spline regions — "
                f"{self.fit.evaluations}/{self.fit.iteration_limit} "
                "objective evaluations."
            )
        else:
            average = float(np.mean(np.concatenate([
                values[2] for values in self.fit.comparison.values()
            ])))
            spread = float(np.mean([
                np.max(values[2]) - np.min(values[2])
                for values in self.fit.comparison.values()
            ]))
            self.status_label.setText(
                f"Fit complete — average distance {average:.6g}; "
                f"average max−min spread {spread:.6g}; "
                f"anchor RMS {self.fit.anchor_error:.6g}."
            )

    def _show_empty_preview(self):
        for line in self.residual_lines.values():
            line.set_data([], [])
        self.residual_axes.relim()
        self.residual_axes.autoscale_view()
        self.canvas.draw_idle()
        self._sync_preview_viewport()

    def _draw_comparison(self, comparison):
        self._sync_preview_viewport(comparison)

    def _show_results(self, comparison):
        self.results_table.setRowCount(len(REGION_NAMES))
        statistics = _distance_statistics(comparison)
        for row, name in enumerate(RESIDUAL_REGION_NAMES):
            values = (name, *(f"{value:.8g}" for value in statistics[name]))
            for column, value in enumerate(values):
                self.results_table.setItem(row, column, QTableWidgetItem(value))
        self.results_table.resizeColumnsToContents()

    def _reference_selection_changed(self):
        self.reference_airfoil = self.reference_combo.currentData()
        self.fit = None
        self.results_table.setRowCount(0)
        self._show_empty_preview()
        self._refresh_reference_preview()
        self._update_process_checks()
        self._update_controls()

    def _update_controls(self):
        self.proceed_button.setEnabled(
            self.reference_combo.currentData() is not None
            and self.current_airfoil is not None
            and getattr(self, "_reference_preview_valid", False)
        )
        if self.reference_combo.currentData() is None:
            self.status_label.setText("Select or add a reference airfoil.")
        elif self.current_airfoil is None:
            self.status_label.setText("No current airfoil is available.")
        elif self.fit is None:
            self.status_label.setText(
                "Set optional parameter min/max values, then proceed."
            )

    def _add_reference(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Add Reference Airfoil",
            "",
            "Accepted airfoil formats (*.arf.ddls *.arf *.txt *.dat);;All files (*)",
        )
        if not file_path:
            return
        if self.airfoil_designer is None:
            QMessageBox.warning(
                self, "Reference unavailable", "No Airfoil Designer is attached."
            )
            return

        before_count = len(getattr(self.project, "reference_airfoils", []))
        self.airfoil_designer.addReference(file_path)
        references = getattr(self.project, "reference_airfoils", [])
        if len(references) == before_count:
            self.status_label.setText(
                "The reference could not be loaded; check the application log."
            )
            return

        self.reference_airfoil = references[-1]
        self._populate_reference_combo()
        self._reference_selection_changed()

    def _refresh_airfoil_views(self):
        designer = self.airfoil_designer
        if designer is None:
            return
        if getattr(designer, "OPEN_GL", None) is not None:
            designer.OPEN_GL.set_airfoil_to_display(self.current_airfoil)
            designer.OPEN_GL.update()
        if getattr(designer, "TABLE_PARAMETERS", None) is not None:
            designer.TABLE_PARAMETERS.update()
        if getattr(designer, "TABLE_STATISTICS", None) is not None:
            designer.TABLE_STATISTICS.update()

    def _cancel_running_fit(self):
        worker = self._worker
        if worker is None:
            return
        self._cancel_pending = True
        worker.requestInterruption()
        worker.wait()
        self._timer.stop()
        self._worker = None
        self._running = False
        self.fit = None
        self._refresh_parameter_values()
        self._sync_preview_viewport()

    def reject(self):
        self._close_dialog()

    def closeEvent(self, event):
        if self._running:
            self._cancel_running_fit()
        event.accept()

    def _close_dialog(self):
        if self._running:
            self._cancel_running_fit()
        if self.proceed_button.text() == "Done":
            super().accept()
        else:
            super().reject()
