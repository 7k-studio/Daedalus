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
import math
import numpy as np
import src.utils.tools_program as tools
from src.obj.curves import BSpline, Line
from src.obj.param import Param, Attr, M, DEG

class LeadingEdge:
    """Set up detials for LEADING EDGE Spline"""
    def __init__(self, program):
        self.PROGRAM = program
        
        # self.type = Attr("type", "F", ["F"])

        self.attrs = {
            "type": Attr("type", "G2", ["G1", "G2"])
        }

        self.params = {
            "ps_tan":    Param("ps_tan",0.05,M),
            "ps_slope":  Param("ps_slope",-20,DEG),
            "ps_curv":   Param("ps_curv",0.05,M),
            "ss_tan":    Param("ss_tan",0.05,M),
            "ss_slope":  Param("ss_slope",-20,DEG),
            "ss_curv":   Param("ss_curv",0.05,M)
        }

        self.spline = BSpline(self.PROGRAM)

    def calc_position(self):

        index_min = min(range(len(self.spline.geom[0])), key=self.spline.geom[0].__getitem__)
        pos_X = self.spline.geom[0][index_min]
        pos_Y = self.spline.geom[1][index_min]

        return pos_X, pos_Y

class TrailingEdge:
    """Set up detials for TRAILING EDGE Spline"""
    def __init__(self, program):
        self.PROGRAM = program

        # self.type = Attr("type", "F", ["F"])

        self.attrs = {
            "type": Attr("type", "G2", ["G1", "G2"])
        }

        self.params = {
            "ps_tan":    Param("ps_tan",0.004,M),
            "ps_slope":  Param("ps_slope",-30,DEG),
            "ps_curv":   Param("ps_curv",0.004,M),
            "ss_tan":    Param("ss_tan",0.004,M),
            "ss_slope":  Param("ss_slope",-30,DEG),
            "ss_curv":   Param("ss_curv",0.004,M),
        }

        self.spline = BSpline(self.PROGRAM)
    
    def calc_position(self):

        index_max = max(range(len(self.spline.geom[0])), key=self.spline.geom[0].__getitem__)
        pos_X = self.spline.geom[0][index_max]
        pos_Y = self.spline.geom[1][index_max]

        return pos_X, pos_Y

class PressureSide:
    """Set up detials for PRESSURE SIDE Spline"""
    def __init__(self, program):
        self.PROGRAM = program

        # self.type = Attr("type", "C", ["C"])

        self.attrs = {
            "type": Attr("type", "G2", ["G1", "G2"])
        }

        self.params = {
            "fwd_wedge": Param("fwd_wedge",10,DEG),
            "fwd_tan":   Param("fwd_tan",0.05,M),
            "fwd_slope": Param("fwd_slope",0,DEG),
            "fwd_curv":  Param("fwd_curv",0.10,M),
            "rwd_wedge": Param("rwd_wedge",5,DEG),
            "rwd_tan":   Param("rwd_tan",0.10,M),
            "rwd_slope": Param("rwd_slope",0,DEG),
            "rwd_curv":  Param("rwd_curv",0.10,M)
        }

        self.spline = BSpline(self.PROGRAM)

class SuctionSide:
    """Set up detials for SUCTION SIDE Spline"""
    def __init__(self, program):
        self.PROGRAM = program

        self.attrs = {
            "type": Attr("type", "G2", ["G1", "G2"])
        }

        self.params = {
            "fwd_wedge": Param("fwd_wedge",10,DEG),
            "fwd_tan":   Param("fwd_tan",0.05,M),
            "fwd_slope": Param("fwd_slope",0,DEG),
            "fwd_curv":  Param("fwd_curv",0.10,M),
            "rwd_wedge": Param("rwd_wedge",5,DEG),
            "rwd_tan":   Param("rwd_tan",0.10,M),
            "rwd_slope": Param("rwd_slope",0,DEG),
            "rwd_curv":  Param("rwd_curv",0.10,M)
        }

        self.spline = BSpline(self.PROGRAM)


class ChordLine:
    def __init__(self, parent):
        self.AIRFOIL = parent
        self.line = Line()
    
    def calc_chord(self):

        index_min = min(range(len(self.AIRFOIL.LE.spline.geom[0])), key=self.AIRFOIL.LE.spline.geom[0].__getitem__)
        X_min = self.AIRFOIL.LE.spline.geom[0][index_min]
        Y_min = self.AIRFOIL.LE.spline.geom[1][index_min]

        index_max = max(range(len(self.AIRFOIL.TE.spline.geom[0])), key=self.AIRFOIL.TE.spline.geom[0].__getitem__)
        X_max = self.AIRFOIL.TE.spline.geom[0][index_max]
        Y_max = self.AIRFOIL.TE.spline.geom[1][index_max]

        chord = math.sqrt((X_max-X_min)**2 + (Y_max-Y_min)**2)

        return chord

class CamberLine:
    def __init__(self):
        pass

class Airfoil:
    def __init__(self, program, parent=None):
        self.PROGRAM = program
        self.parent = parent

        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = ""
        self.path = ""
        self.format = 'ddls-parametric'
        self._is_pressure_side_up = True
        self.visible = False

        #Active parameters
        self.info = {
            'creation_date': '',
            'modification_date': '',
            'description': ''
            }

        self.params = {
            "origin_X":  Param("origin_X",0,M),
            "origin_Y":  Param("origin_Y",0,M),
            "stretch":   Param("stretch",1,M),
            "incline":   Param("incline",0,DEG),
            "LE_thickness": Param("thickness",0.1,M),
            "LE_angle":     Param("angle",0.0,DEG),
            "TE_thickness": Param("thickness",0.01,M),
            "TE_angle":     Param("angle",0.0,DEG),
        }

        self.attrs = {
            
        }

        self.stats = {
            "Chord": Param("Chord", 1, M),
            "Position LE X": Param("Position LE X", 0, M),
            "Position LE Y": Param("Position LE Y", 0, M),
            "Position TE X": Param("Position TE X", 0, M),
            "Position TE Y": Param("Position TE Y", 0, M),
        }

        self.LE = LeadingEdge(self.PROGRAM)
        self.TE = TrailingEdge(self.PROGRAM)
        self.PS = PressureSide(self.PROGRAM)
        self.SS = SuctionSide(self.PROGRAM)

        self.CHORD = ChordLine(self)

    def construct(self):

        # Creating orignin points
        p_le_org = [self.params['origin_X'].value, self.params['origin_Y'].value]
        p_te_org = tools.vec_translate(p_le_org, self.params['stretch'].value, self.params["incline"].value)

        if self._is_pressure_side_up:
            factor = 1
        else:
            factor = -1

        # Creating up (u) and down (d) point for Leading Edge PS and SS handle 
        p_le_u = tools.vec_translate(p_le_org, factor * self.params['LE_thickness'].value/2, 90+(factor*self.params["LE_angle"].value))
        p_le_d = tools.vec_translate(p_le_org, -factor * self.params['LE_thickness'].value/2, 90+(factor*self.params["LE_angle"].value))

        # Creating up (u) and down (d) point for Trailing Edge PS and SS handle 
        p_te_u = tools.vec_translate(p_te_org, factor*self.params['TE_thickness'].value/2, 90+(factor*self.params["TE_angle"].value))
        p_te_d = tools.vec_translate(p_te_org, -factor*self.params['TE_thickness'].value/2, 90+(factor*self.params["TE_angle"].value))

        #===================================
        # Creating handle for Pressure Side
        #===================================
        ### G1 continuity ###
        try:
            # PS (upper-like) forward tangent should move toward chordwards (inward), not further away.
            p_ps_fwd_tan = tools.vec_translate(p_le_u, self.PS.params['fwd_tan'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["LE_angle"].value+factor*self.PS.params["fwd_wedge"].value))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_le_u

        try:
            p_ps_rwd_tan = tools.vec_translate(p_te_u, -self.PS.params['rwd_tan'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["TE_angle"].value-factor*self.PS.params["rwd_wedge"].value))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_te_u

        ### G2 continuity ###
        if self.PS.attrs['type'].value == 'G2':
            try:
                p_ps_fwd_crv = tools.vec_translate(p_ps_fwd_tan, self.PS.params['fwd_curv'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["LE_angle"].value+factor*self.PS.params["fwd_wedge"].value+factor*self.PS.params["fwd_slope"].value))
            except ZeroDivisionError:
                p_ps_fwd_crv = p_ps_fwd_tan

            try:
                p_ps_rwd_crv = tools.vec_translate(p_ps_rwd_tan, -self.PS.params['rwd_curv'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["TE_angle"].value-factor*self.PS.params["rwd_wedge"].value-factor*self.PS.params["rwd_slope"].value))
            except ZeroDivisionError:
                p_ps_fwd_tan = p_ps_rwd_tan
        else:
            p_ps_fwd_crv = None
            p_ps_rwd_crv = None

        #===================================
        # Creating handle for Suction Side
        #===================================
        try:
            # SS (lower-like) forward tangent should move toward chordwards (inward) as well.
            p_ss_fwd_tan = tools.vec_translate(p_le_d, self.SS.params['fwd_tan'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["LE_angle"].value-factor*self.SS.params["fwd_wedge"].value))
        except ZeroDivisionError:
            p_ss_fwd_tan = p_le_d

        try:
            p_ss_rwd_tan = tools.vec_translate(p_te_d, -self.SS.params['rwd_tan'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["TE_angle"].value+factor*self.SS.params["rwd_wedge"].value))
        except ZeroDivisionError:
            p_ss_fwd_tan = p_te_d

        ### G2 continuity ###
        if self.SS.attrs['type'].value == 'G2':
            try:
                p_ss_fwd_crv = tools.vec_translate(p_ss_fwd_tan, self.SS.params['fwd_curv'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["LE_angle"].value-factor*self.SS.params["fwd_wedge"].value-factor*self.SS.params["fwd_slope"].value))
            except ZeroDivisionError:
                p_ss_fwd_crv = p_ss_fwd_tan

            try:
                p_ss_rwd_crv = tools.vec_translate(p_ss_rwd_tan, -self.SS.params['rwd_curv'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["TE_angle"].value+factor*self.SS.params["rwd_wedge"].value+factor*self.SS.params["rwd_slope"].value))
            except ZeroDivisionError:
                p_ss_rwd_crv = p_ss_rwd_tan
        else:
            p_ss_fwd_crv = None
            p_ss_rwd_crv = None

        #===================================
        # Creating handle for Leading Edge
        #===================================
        try:
            p_le_ps_tan = tools.vec_translate(p_le_u, -self.LE.params['ps_tan'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["LE_angle"].value+factor*self.PS.params["fwd_wedge"].value))
        except ZeroDivisionError:
            p_le_ps_tan = p_le_u

        try:
            p_le_ss_tan = tools.vec_translate(p_le_d, -self.LE.params['ss_tan'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["LE_angle"].value-factor*self.SS.params["fwd_wedge"].value))
        except ZeroDivisionError:
            p_le_ss_tan = p_le_d

        ### G2 continuity ###
        if self.LE.attrs['type'].value == 'G2':
            try:
                p_le_ps_crv = tools.vec_translate(p_le_ps_tan, -self.LE.params['ps_curv'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["LE_angle"].value+factor*self.PS.params["fwd_wedge"].value-factor*self.LE.params["ps_slope"].value))
            except ZeroDivisionError:
                p_le_ps_crv = p_le_ps_tan

            try:
                p_le_ss_crv = tools.vec_translate(p_le_ss_tan, -self.LE.params['ss_curv'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["LE_angle"].value-factor*self.SS.params["fwd_wedge"].value+factor*self.LE.params["ss_slope"].value))
            except ZeroDivisionError:
                p_le_ss_tan = p_le_ss_tan
        else:
            p_le_ps_crv = None
            p_le_ss_crv = None

        #===================================
        # Creating handle for Trailing Edge
        #===================================
        try:
            # TE-side tangents also should move inside toward chord (backward), not over-shoot +x.
            p_te_ps_tan = tools.vec_translate(p_te_u, self.TE.params['ps_tan'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["TE_angle"].value-factor*self.PS.params["rwd_wedge"].value))
        except ZeroDivisionError:
            p_te_ps_tan = p_te_u

        try:
            p_te_ss_tan = tools.vec_translate(p_te_d, self.TE.params['ss_tan'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["TE_angle"].value+factor*self.SS.params["rwd_wedge"].value))
        except ZeroDivisionError:
            p_te_ss_tan = p_te_d

        ### G2 continuity ###
        if self.TE.attrs['type'].value == 'G2':
            try:
                p_te_ps_crv = tools.vec_translate(p_te_ps_tan, self.TE.params['ps_curv'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["TE_angle"].value-factor*self.PS.params["rwd_wedge"].value+factor*self.TE.params["ps_slope"].value))
            except ZeroDivisionError:
                p_te_ps_crv = p_te_ps_tan

            try:
                p_te_ss_crv = tools.vec_translate(p_te_ss_tan, self.TE.params['ss_curv'].value*self.params['stretch'].value, (factor*self.params["incline"].value+factor*self.params["TE_angle"].value+factor*self.SS.params["rwd_wedge"].value-factor*self.TE.params["ss_slope"].value))
            except ZeroDivisionError:
                p_te_ss_crv = p_te_ss_tan
        else:
            p_te_ps_crv = None
            p_te_ss_crv = None

        # create LE array
        le_control_points = [p_le_u, p_le_ps_tan, p_le_ps_crv, p_le_ss_crv, p_le_ss_tan, p_le_d]
        self.LE.spline.control_points = np.vstack([le_p for le_p in le_control_points if le_p is not None]).T
        # create TE array
        te_control_points = [p_te_u, p_te_ps_tan, p_te_ps_crv, p_te_ss_crv, p_te_ss_tan, p_te_d]
        self.TE.spline.control_points = np.vstack([te_p for te_p in te_control_points if te_p is not None]).T
        # create PS array
        ps_control_points = [p_le_u, p_ps_fwd_tan, p_ps_fwd_crv, p_ps_rwd_crv, p_ps_rwd_tan, p_te_u]
        self.PS.spline.control_points = np.vstack([ps_p for ps_p in ps_control_points if ps_p is not None]).T
        # create SS array
        ss_control_points = [p_le_d, p_ss_fwd_tan, p_ss_fwd_crv, p_ss_rwd_crv, p_ss_rwd_tan, p_te_d]
        self.SS.spline.control_points = np.vstack([ss_p for ss_p in ss_control_points if ss_p is not None]).T

        self.LE.spline.create()
        self.TE.spline.create()
        self.PS.spline.create()
        self.SS.spline.create()
        
        self.logger.info("3D AIRFOIL geometry updated - geometry stored in curves.BSpline objects")

        self.logger.debug("LE, TE, PS, SS geometry established")

    def update(self):
        """Update airfoil 2D geometry (called during design)."""
        self.logger.info("Recalculating airfoil geometry...")
        self.construct()

        self.logger.info("Recalculating airfoil statistics...")
        self.stats['Chord'].set(self.CHORD.calc_chord())
        pos_le_x, pos_le_y = self.LE.calc_position()
        self.stats['Position LE X'].set(pos_le_x)
        self.stats['Position LE Y'].set(pos_le_y)
        pos_te_x, pos_te_y = self.TE.calc_position()
        self.stats['Position TE X'].set(pos_te_x)
        self.stats['Position TE Y'].set(pos_te_y)

        
class SeligAirfoil:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = ""
        self.path = ""
        self.format = 'XY-points'
        self.visible = False
        
        self.curve = []


class Airfoil_030ddls:
    def __init__(self, program):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = ""
        self.path = ""
        self.format = '030-ddls-parametric'
        self.PROGRAM = program
        self.visible = False

        #Active parameters
        self.infos = {
            'name': 'Airfoil',
            'creation_date': '',
            'modification_date': '',
            'description': ''}

        self.params = {
            "chord": 1,
            "origin_X": 0,
            "origin_Y": 0,
            "le_thickness": 0.05,
            "le_depth": 0.04,
            "le_offset": 0,
            "le_angle": 0.02,
            "te_thickness": 0.01,
            "te_depth": 0.01,
            "te_offset": 0,
            "te_angle": 0.05,
            "ps_fwd_angle": 22,
            "ps_rwd_angle": -15,
            "ps_fwd_accel": 0.20,
            "ps_rwd_accel": 0.10,
            "ss_fwd_angle": -11,
            "ss_rwd_angle": -3,
            "ss_fwd_accel": 0.16,
            "ss_rwd_accel": 0.40
        }

        self.unit = {
            "chord":        "length",
            "origin_X":     "length",
            "origin_Y":     "length",
            "le_thickness": "length",
            "le_depth":     "length",
            "le_offset":    "length",
            "le_angle":     "angle",
            "te_thickness": "length",
            "te_depth":     "length",
            "te_offset":    "length",
            "te_angle":     "angle",
            "ps_fwd_angle": "angle",
            "ps_rwd_angle": "angle",
            "ps_fwd_accel": "length",
            "ps_rwd_accel": "length",
            "ss_fwd_angle": "angle",
            "ss_rwd_angle": "angle",
            "ss_fwd_accel": "length",
            "ss_rwd_accel": "length"
        }

        # self.geom = {
        #     'le': [],
        #     'ps': [],
        #     'ss': [],
        #     'te': []
        # }

        self.le_spline = BSpline(self.PROGRAM)
        self.te_spline = BSpline(self.PROGRAM)
        self.ps_spline = BSpline(self.PROGRAM)
        self.ss_spline = BSpline(self.PROGRAM)

        # self.constr = {
        #     'le': [],
        #     'ps': [],
        #     'ss': [],
        #     'te': []
        # }

    def construct(self):
        # Leading Edge calculations
        p_le_start = [self.params['origin_X'], self.params['origin_Y']+self.params['le_offset']]
        p_le_end = [p_le_start[0]+self.params['le_depth']*math.cos(np.radians(self.params['le_angle'])),p_le_start[1]+(self.params['le_depth']*math.sin(np.radians(self.params['le_angle'])))]

        a0 = math.tan(np.radians(90+self.params['le_angle'])) # Directional param of the leading edge straight and the pararel one
        a1 = math.tan(np.radians(self.params['ps_fwd_angle']+self.params['le_angle'])) # Directional param of the pressure side forward slope
        a2 = math.tan(np.radians(self.params['ss_fwd_angle']+self.params['le_angle'])) # Directional param of the suction side forward slope

        b0 = p_le_start[1]-a0*p_le_start[0] # Positional parameter of the leading edge straight 'Origin Point'
        b0p = p_le_end[1]-a0*p_le_end[0]
        b1 = p_le_end[1]+(self.params['le_thickness']/2*math.cos(np.radians(self.params['le_angle'])))-a1*(p_le_end[0]-self.params['le_thickness']/2*math.sin(np.radians(self.params['le_angle'])))
        b2 = p_le_end[1]-(self.params['le_thickness']/2*math.cos(np.radians(self.params['le_angle'])))-a2*(p_le_end[0]+self.params['le_thickness']/2*math.sin(np.radians(self.params['le_angle'])))

        p_le_t = [(b1-b0)/(a0-a1),a0*((b1-b0)/(a0-a1))+b0] # G1 upper point
        p_le_d = [(b2-b0)/(a0-a2),a0*((b2-b0)/(a0-a2))+b0] # G1 lower point
        p_le_ps = [(b1-b0p)/(a0-a1),a0*((b1-b0p)/(a0-a1))+b0p] # G0 with with the pressure side
        p_le_ss = [(b2-b0p)/(a0-a2),a0*((b2-b0p)/(a0-a2))+b0p] # G0 with with the suction side

        le_constr = np.vstack([p_le_ss, p_le_d, p_le_t, p_le_ps]).T

        p_te_start = [self.params['origin_X']+self.params['chord'], self.params['origin_Y']+self.params['te_offset']]
        p_te_end = [p_te_start[0]-self.params['te_depth']*math.cos(np.radians(self.params['te_angle'])), p_te_start[1]-(self.params['te_depth']*math.sin(np.radians(self.params['te_angle'])))]
        a3 = math.tan(np.radians(90+self.params['te_angle']))
        a4 = math.tan(np.radians(self.params['ps_rwd_angle']+self.params['te_angle']))
        a5 = math.tan(np.radians(self.params['ss_rwd_angle']+self.params['te_angle']))
        b3 = p_te_start[1]-a3*p_te_start[0]
        b3p = p_te_end[1]-a3*p_te_end[0]
        b4 = p_te_end[1]+(self.params['te_thickness']/2*math.cos(np.radians(self.params['te_angle'])))-a4*(p_te_end[0]-self.params['te_thickness']/2*math.sin(np.radians(self.params['te_angle'])))
        b5 = p_te_end[1]-(self.params['te_thickness']/2*math.cos(np.radians(self.params['te_angle'])))-a5*(p_te_end[0]+self.params['te_thickness']/2*math.sin(np.radians(self.params['te_angle'])))

        p_te_t = [(b4-b3)/(a3-a4),a3*((b4-b3)/(a3-a4))+b3] # G1 upper point
        p_te_d = [(b5-b3)/(a3-a5),a3*((b5-b3)/(a3-a5))+b3] # G1 lower point
        p_te_ps = [(b4-b3p)/(a3-a4),a3*((b4-b3p)/(a3-a4))+b3p] # G0 with with the pressure side
        p_te_ss = [(b5-b3p)/(a3-a5),a3*((b5-b3p)/(a3-a5))+b3p] # G0 with with the suction side

        te_constr = np.vstack([p_te_ss, p_te_d, p_te_t, p_te_ps]).T

        p_ps_le = p_le_ps
        p_ps_te = p_te_ps
        p_ps_1 = [self.params['origin_X']+self.params['ps_fwd_accel'], a1*(self.params['origin_X']+self.params['ps_fwd_accel'])+b1]
        p_ps_2 = [p_ps_te[0]-self.params['ps_rwd_accel'], a4*(p_ps_te[0]-self.params['ps_rwd_accel'])+b4]   
        ps_constr = np.vstack([p_ps_le, p_ps_1, p_ps_2, p_ps_te]).T
        p_ss_le = p_le_ss
        p_ss_te = p_te_ss
        p_ss_1 = [self.params['origin_X']+self.params['ss_fwd_accel'], a2*(self.params['origin_X']+self.params['ss_fwd_accel'])+b2]
        p_ss_2 = [p_ss_te[0]-self.params['ss_rwd_accel'], a5*(p_ss_te[0]-self.params['ss_rwd_accel'])+b5]   
        ss_constr = np.vstack([p_ss_le, p_ss_1, p_ss_2, p_ss_te]).T

        # Generate Splines
        # le_spline = CreateBSpline(le_constr)
        # te_spline = CreateBSpline(te_constr)
        # ps_spline = CreateBSpline(ps_constr)
        # ss_spline = CreateBSpline(ss_constr)

        self.le_spline.control_points = le_constr
        self.te_spline.control_points = te_constr
        self.ps_spline.control_points = ps_constr
        self.ss_spline.control_points = ss_constr

        self.le_spline.create()
        self.te_spline.create()
        self.ps_spline.create()
        self.ss_spline.create()

    def update(self):
        self.logger.info("Recalculating airfoil geometry...")
        self.construct()