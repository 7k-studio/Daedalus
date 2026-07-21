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
from src.obj.class_param import Param, Attr, M, DEG

class LeadingEdge:
    """Set up detials for LEADING EDGE Spline"""
    def __init__(self, program):
        self.PROGRAM = program
        
        self.type = Attr("type", "F", ["F"])

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

        self.type = Attr("type", "F", ["F"])

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

        self.type = Attr("type", "C", ["C"])

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

        self.type = Attr("type", "C", ["C"])

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

        # Creating up (u) and down (d) point for Leading Edge PS and SS handle 
        p_le_u = tools.vec_translate(p_le_org, self.params['LE_thickness'].value/2, 90+self.params["LE_angle"].value)
        p_le_d = tools.vec_translate(p_le_org, -self.params['LE_thickness'].value/2, 90+self.params["LE_angle"].value)

        # Creating up (u) and down (d) point for Trailing Edge PS and SS handle 
        p_te_u = tools.vec_translate(p_te_org, self.params['TE_thickness'].value/2, 90+self.params["TE_angle"].value)
        p_te_d = tools.vec_translate(p_te_org, -self.params['TE_thickness'].value/2, 90+self.params["TE_angle"].value)

        #===================================
        # Creating handle for Pressure Side
        #===================================
        try:
            # PS (upper-like) forward tangent should move toward chordwards (inward), not further away.
            p_ps_fwd_tan = tools.vec_translate(p_le_u, self.PS.params['fwd_tan'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["LE_angle"].value+self.PS.params["fwd_wedge"].value))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_le_u

        try:
            p_ps_rwd_tan = tools.vec_translate(p_te_u, -self.PS.params['rwd_tan'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["TE_angle"].value-self.PS.params["rwd_wedge"].value))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_te_u

        try:
            p_ps_fwd_crv = tools.vec_translate(p_ps_fwd_tan, self.PS.params['fwd_curv'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["LE_angle"].value+self.PS.params["fwd_wedge"].value+self.PS.params["fwd_slope"].value))
        except ZeroDivisionError:
            p_ps_fwd_crv = p_ps_fwd_tan

        try:
            p_ps_rwd_crv = tools.vec_translate(p_ps_rwd_tan, -self.PS.params['rwd_curv'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["TE_angle"].value-self.PS.params["rwd_wedge"].value-self.PS.params["rwd_slope"].value))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_ps_rwd_tan

        #===================================
        # Creating handle for Suction Side
        #===================================
        try:
            # SS (lower-like) forward tangent should move toward chordwards (inward) as well.
            p_ss_fwd_tan = tools.vec_translate(p_le_d, self.SS.params['fwd_tan'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["LE_angle"].value-self.SS.params["fwd_wedge"].value))
        except ZeroDivisionError:
            p_ss_fwd_tan = p_le_d

        try:
            p_ss_rwd_tan = tools.vec_translate(p_te_d, -self.SS.params['rwd_tan'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["TE_angle"].value+self.SS.params["rwd_wedge"].value))
        except ZeroDivisionError:
            p_ss_fwd_tan = p_te_d

        try:
            p_ss_fwd_crv = tools.vec_translate(p_ss_fwd_tan, self.SS.params['fwd_curv'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["LE_angle"].value-self.SS.params["fwd_wedge"].value-self.SS.params["fwd_slope"].value))
        except ZeroDivisionError:
            p_ss_fwd_crv = p_ss_fwd_tan

        try:
            p_ss_rwd_crv = tools.vec_translate(p_ss_rwd_tan, -self.SS.params['rwd_curv'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["TE_angle"].value+self.SS.params["rwd_wedge"].value+self.SS.params["rwd_slope"].value))
        except ZeroDivisionError:
            p_ss_rwd_crv = p_ss_rwd_tan

        #===================================
        # Creating handle for Leading Edge
        #===================================
        try:
            p_le_ps_tan = tools.vec_translate(p_le_u, -self.LE.params['ps_tan'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["LE_angle"].value+self.PS.params["fwd_wedge"].value))
        except ZeroDivisionError:
            p_le_ps_tan = p_le_u

        try:
            p_le_ss_tan = tools.vec_translate(p_le_d, -self.LE.params['ss_tan'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["LE_angle"].value-self.SS.params["fwd_wedge"].value))
        except ZeroDivisionError:
            p_le_ss_tan = p_le_d

        try:
            p_le_ps_crv = tools.vec_translate(p_le_ps_tan, -self.LE.params['ps_curv'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["LE_angle"].value+self.PS.params["fwd_wedge"].value-self.LE.params["ps_slope"].value))
        except ZeroDivisionError:
            p_le_ps_crv = p_le_ps_tan

        try:
            p_le_ss_crv = tools.vec_translate(p_le_ss_tan, -self.LE.params['ss_curv'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["LE_angle"].value-self.SS.params["fwd_wedge"].value+self.LE.params["ss_slope"].value))
        except ZeroDivisionError:
            p_le_ss_tan = p_le_ss_tan

        #===================================
        # Creating handle for Trailing Edge
        #===================================
        try:
            # TE-side tangents also should move inside toward chord (backward), not over-shoot +x.
            p_te_ps_tan = tools.vec_translate(p_te_u, self.TE.params['ps_tan'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["TE_angle"].value-self.PS.params["rwd_wedge"].value))
        except ZeroDivisionError:
            p_te_ps_tan = p_te_u

        try:
            p_te_ss_tan = tools.vec_translate(p_te_d, self.TE.params['ss_tan'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["TE_angle"].value+self.SS.params["rwd_wedge"].value))
        except ZeroDivisionError:
            p_te_ss_tan = p_te_d

        try:
            p_te_ps_crv = tools.vec_translate(p_te_ps_tan, self.TE.params['ps_curv'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["TE_angle"].value-self.PS.params["rwd_wedge"].value+self.TE.params["ps_slope"].value))
        except ZeroDivisionError:
            p_te_ps_crv = p_te_ps_tan

        try:
            p_te_ss_crv = tools.vec_translate(p_te_ss_tan, self.TE.params['ss_curv'].value*self.params['stretch'].value, (self.params["incline"].value+self.params["TE_angle"].value+self.SS.params["rwd_wedge"].value-self.TE.params["ss_slope"].value))
        except ZeroDivisionError:
            p_te_ss_crv = p_te_ss_tan

        self.LE.spline.control_points = np.vstack([p_le_u, p_le_ps_tan, p_le_ps_crv, p_le_ss_crv, p_le_ss_tan, p_le_d]).T
        self.TE.spline.control_points = np.vstack([p_te_u, p_te_ps_tan, p_te_ps_crv, p_te_ss_crv, p_te_ss_tan, p_te_d]).T
        self.PS.spline.control_points = np.vstack([p_le_u, p_ps_fwd_tan, p_ps_fwd_crv, p_ps_rwd_crv, p_ps_rwd_tan, p_te_u]).T
        self.SS.spline.control_points = np.vstack([p_le_d, p_ss_fwd_tan, p_ss_fwd_crv, p_ss_rwd_crv, p_ss_rwd_tan, p_te_d]).T

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
        self.format = 'selig'
        self.visible = False
        
        self.top_curve = []
        self.dwn_curve = []