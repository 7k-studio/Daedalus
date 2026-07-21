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
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QDialog, QPushButton, QHBoxLayout, QComboBox, QLineEdit, QFormLayout
)
logger = logging.getLogger(__name__)

def fit_2_reference(current_airfoil, reference_airfoil, bounds=None):
    """ Fit the currently selected airfoil to the reference_airfoil by optimizing its parameters. """
    import numpy as np
    import math
    from scipy.interpolate import splprep, splev
    from scipy.optimize import minimize

    # Prepare reference points (flattened arrays)
    top_ref = np.array(reference_airfoil.top_curve)
    dwn_ref = np.array(reference_airfoil.dwn_curve)
    # Combine for error calculation
    ref_points = np.hstack((top_ref, dwn_ref)).T  # shape (N, 2)

    # Parameter names and initial values
    param_names = [
        "chord", "le_thickness", "le_depth", "le_offset", "le_angle",
        "te_thickness", "te_depth", "te_offset", "te_angle",
        "ps_fwd_angle", "ps_rwd_angle", "ps_fwd_accel", "ps_rwd_accel",
        "ss_fwd_angle", "ss_rwd_angle", "ss_fwd_accel", "ss_rwd_accel"
    ]
    # Fallback for missing params
    def get_param(k, default=0.0):
        return current_airfoil.params.get(k, default)
    initial_params = [get_param(k, 1.0 if "thickness" in k or "depth" in k else 0.0) for k in param_names]

    # Bounds (adjust as needed)
    if bounds is None:
        bounds = []
        for k in param_names:
            if "angle" in k:
                bounds.append((-90, 90))
            elif "thickness" in k or "depth" in k or "offset" in k:
                bounds.append((0, 2))
            elif k == "chord":
                bounds.append((0.01, 10))
            else:
                bounds.append((-2, 2))

    def CreateBSpline(const_points):
        l = len(const_points[0])
        t = np.linspace(0, 1, l-2, endpoint=True)
        t = np.append([0,0,0], t)
        t = np.append(t, [1,1,1])
        tck = [t, [const_points[0], const_points[1]], 3]
        u3 = np.linspace(0, 1, max(l*2, 70), endpoint=True)
        spline = splev(u3, tck)
        return spline

    def objective_function(p):
        # Unpack parameters
        chord, le_thickness, le_depth, le_offset, le_angle, te_thickness, te_depth, te_offset, te_angle, \
        ps_fwd_angle, ps_rwd_angle, ps_fwd_accel, ps_rwd_accel, ss_fwd_angle, ss_rwd_angle, ss_fwd_accel, ss_rwd_accel = p

        origin_X = 0
        origin_Y = 0

        # LE control points
        p_le_start = [origin_X, origin_Y]
        a0 = math.tan(math.radians(90 + le_angle))
        a1 = math.tan(math.radians(ps_fwd_angle))
        a2 = math.tan(math.radians(ss_fwd_angle))
        b0 = p_le_start[1] - a0 * p_le_start[0]
        b1 = p_le_start[1] + le_thickness/2 + le_offset - a1 * (p_le_start[0] + le_depth)
        b2 = p_le_start[1] - le_thickness/2 + le_offset - a2 * (p_le_start[0] + le_depth)
        p_le_t = [(b1-b0)/(a0-a1), a0*((b1-b0)/(a0-a1))+b0]
        p_le_d = [(b2-b0)/(a0-a2), a0*((b2-b0)/(a0-a2))+b0]
        p_le_ps = [origin_X+le_depth, origin_Y+le_thickness/2+le_offset]
        p_le_ss = [origin_X+le_depth, origin_Y-le_thickness/2+le_offset]
        le_constr = np.vstack([p_le_ss, p_le_d, p_le_t, p_le_ps]).T

        # TE control points
        p_te_ps = [origin_X+chord-te_depth, origin_Y+te_thickness/2+te_offset]
        p_te_ss = [origin_X+chord-te_depth, origin_Y-te_thickness/2+te_offset]
        p_te_start = [origin_X+chord+te_thickness/2, origin_Y]
        a3 = math.tan(math.radians(90 + te_angle))
        a4 = math.tan(math.radians(ps_rwd_angle))
        a5 = math.tan(math.radians(ss_rwd_angle))
        b3 = p_te_start[1] - a3 * p_te_start[0]
        b4 = p_te_start[1] + te_thickness/2 + te_offset - a4 * (p_te_start[0] - te_depth)
        b5 = p_te_start[1] - te_thickness/2 + te_offset - a5 * (p_te_start[0] - te_depth)
        p_te_t = [(b4-b3)/(a3-a4), a3*((b4-b3)/(a3-a4))+b3]
        p_te_d = [(b5-b3)/(a3-a5), a3*((b5-b3)/(a3-a5))+b3]
        te_constr = np.vstack([p_te_ss, p_te_d, p_te_start, p_te_t, p_te_ps]).T

        # PS control points
        p_ps_le = p_le_ps
        p_ps_te = p_te_ps
        p_ps_1 = [origin_X+ps_fwd_accel, a1*(origin_X+ps_fwd_accel)+b1]
        p_ps_2 = [p_ps_te[0]-ps_rwd_accel, a4*(p_ps_te[0]-ps_rwd_accel)+b4]
        ps_constr = np.vstack([p_ps_le, p_ps_1, p_ps_2, p_ps_te]).T

        # SS control points
        p_ss_le = p_le_ss
        p_ss_te = p_te_ss
        p_ss_1 = [origin_X+ss_fwd_accel, a2*(origin_X+ss_fwd_accel)+b2]
        p_ss_2 = [p_ss_te[0]-ss_rwd_accel, a5*(p_ss_te[0]-ss_rwd_accel)+b5]
        ss_constr = np.vstack([p_ss_le, p_ss_1, p_ss_2, p_ss_te]).T

        # Generate Splines
        le_spline = CreateBSpline(le_constr)
        te_spline = CreateBSpline(te_constr)
        ps_spline = CreateBSpline(ps_constr)
        ss_spline = CreateBSpline(ss_constr)

        # Combine all spline points
        all_spline_coords = np.hstack((le_spline, ps_spline, te_spline, ss_spline)).T  # shape (M, 2)

        # Compute error: sum of squared distances from each reference point to closest spline point
        error = 0
        for point in ref_points:
            distances = np.linalg.norm(all_spline_coords - point, axis=1)
            error += np.min(distances) ** 2
        return error
    
    # # Run optimization
    result = minimize(
        objective_function,
        initial_params,
        bounds=bounds,
        method='L-BFGS-B',
        options={'maxiter': 200, 'disp': True}
    )

    # Assign optimized parameters back to airfoil
    if result.success:
        for i, k in enumerate(param_names):
            current_airfoil.params[k] = result.x[i]
        logger.info(f"Airfoil '{current_airfoil.info.get('name', '')}' parameters fitted to reference.")
    else:
        logger.error("Optimization failed:", result.message)

    return result

class Fit2RefWindow(QDialog):
    def __init__(self, parent=None, current_airfoil=None, reference_airfoil=None):

        super().__init__(parent)
        self.setWindowTitle("Fit 2 Reference")
        self.resize(400, 500)
        self.current_airfoil = current_airfoil
        self.reference_airfoil = reference_airfoil

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        self.param_defs = [
            ("Chord:", "chord_box"),
            ("LE thickness:", "le_thickness_box"),
            ("LE depth:", "le_depth_box"),
            ("LE offset:", "le_offset_box"),
            ("LE angle:", "le_angle_box"),
            ("TE thickness:", "te_thickness_box"),
            ("TE depth:", "te_depth_box"),
            ("TE offset:", "te_offset_box"),
            ("TE angle:", "te_angle_box"),
            ("PS fwd angle:", "ps_fwd_angle_box"),
            ("PS rwd angle:", "ps_rwd_angle_box"),
            ("PS fwd accel:", "ps_fwd_accel_box"),
            ("PS rwd accel:", "ps_rwd_accel_box"),
            ("SS fwd angle:", "ss_fwd_angle_box"),
            ("SS rwd angle:", "ss_rwd_angle_box"),
            ("SS fwd accel:", "ss_fwd_accel_box"),
            ("SS rwd accel:", "ss_rwd_accel_box"),
        ]

        self.combo_boxes = {}
        self.input_mins = {}
        self.input_maxs = {}

        for label_text, box_attr in self.param_defs:
            label = QLabel(label_text)
            combo = QComboBox()
            combo.addItems(["Variable", "Restrained", "Fixed"])
            input_min = QLineEdit()
            input_max = QLineEdit()
            input_min.setPlaceholderText("Min")
            input_max.setPlaceholderText("Max")
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.addWidget(combo)
            row_layout.addWidget(input_min)
            row_layout.addWidget(input_max)
            form_layout.addRow(label, row_widget)
            setattr(self, box_attr, combo)
            self.combo_boxes[box_attr] = combo
            self.input_mins[box_attr] = input_min
            self.input_maxs[box_attr] = input_max

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        btn_box = QHBoxLayout()
        self.proceed_btn = QPushButton("Proceed")
        self.cancel_btn = QPushButton("Close")
        btn_box.addWidget(self.proceed_btn)
        btn_box.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_box)

        self.proceed_btn.clicked.connect(self.run_fit)
        self.cancel_btn.clicked.connect(self.reject)

    def get_bounds(self, params):
        bounds = []
        param_keys = [
            "chord", "le_thickness", "le_depth", "le_offset", "le_angle",
            "te_thickness", "te_depth", "te_offset", "te_angle",
            "ps_fwd_angle", "ps_rwd_angle", "ps_fwd_accel", "ps_rwd_accel",
            "ss_fwd_angle", "ss_rwd_angle", "ss_fwd_accel", "ss_rwd_accel"
        ]
        for i, key in enumerate(param_keys):
            combo = self.combo_boxes[self.param_defs[i][1]]
            min_edit = self.input_mins[self.param_defs[i][1]]
            max_edit = self.input_maxs[self.param_defs[i][1]]
            if combo.currentText() == "Restrain":
                min_val = min_edit.text().strip()
                max_val = max_edit.text().strip()
                min_bound = float(min_val) if min_val else None
                max_bound = float(max_val) if max_val else None
                bounds.append((min_bound, max_bound))
                # For chord, if max is empty, use params["chord"] as default
            if combo.currentText() == "Fixed":
                #if key == "chord" and max_val == "":
                min_bound = params.get(param_keys[i], None)
                max_bound = params.get(param_keys[i], None)
                bounds.append((min_bound, max_bound))
            else:
                bounds.append((None, None))
        return bounds

    def run_fit(self):
        params = self.current_airfoil.params
        bounds = self.get_bounds(params)
        logger.debug(bounds)
        result = fit_2_reference(self.current_airfoil, self.reference_airfoil, bounds=bounds)
        if result.success:
            self.accept()


# For testing the dialog independently
if __name__ == "__main__":
    import sys
    import os
    # Add parent directory to sys.path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    app = QApplication(sys.argv)
    dlg = Fit2RefWindow()
    if dlg.exec_():
        logger.info("Preferences saved.")
    else:
        logger.info("Cancelled.")
