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
from geomdl import BSpline, utilities

from src.obj.curves import BSpline
from src.obj.param import Param, Attr, M, DEG
from src.obj.class_skin import Skin

logger = logging.getLogger(__name__)

class Wing:
    def __init__(self, program=None, project=None, parent=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.PROJECT = project
        self.parent = parent

        self.name = 'Wing'
        self.info = {'creation_date': '',
                      'modification_date': ''}
        
        self.params = {}

        self.attrs = {
            'direction': Attr('direction', 'Z+', ['Z+']), # To add in the future: 'X+', 'Y+'
            'connection': Attr('connection', 'Approximated', ['Interpolated','Approximated']) # Maybe in the future: 'Polyline'
        }

        self.stats = {
            'Test': Param('test', 0, M)
        }

        self.segments = []
        self.skin = Skin(self.DAEDALUS, self)
        self.LE_PS = None
        self.LE_SS = None
        self.TE_PS = None
        self.TE_SS = None
    
    def update(self):
        self.logger.info("Updating WING geometry...")
        self.build_connection()
        self.build_surface()

    def build_connection(self):
        self.logger.info("Building connection...")
        if len(self.segments) > 1:
            tmp_le_ps = []
            tmp_le_ss = []
            tmp_te_ps = []
            tmp_te_ss = []

            for i in range(len(self.segments)):
                
                # read an achor points --> connections between each spline
                tmp_le_ps.append(np.array(self.segments[i].ps_spline.control_points)[:,0]) #Coordinates of anchor of le and ps -> list: [X,Y,Z]
                tmp_le_ss.append(np.array(self.segments[i].ss_spline.control_points)[:,0])
                tmp_te_ps.append(np.array(self.segments[i].ps_spline.control_points)[:,-1])
                tmp_te_ss.append(np.array(self.segments[i].ss_spline.control_points)[:,-1])

            if tmp_le_ps: 
                # print("tmp_le_ps: ", tmp_le_ps)
                self.LE_PS = BSpline(self.DAEDALUS)
                self.LE_PS.control_points = np.array(tmp_le_ps).T
                #self.segments[i].skin.PS.u_fwd.control_points = np.array(tmp_le_ps).T
                #self.segments[i].skin.LE.u_rwd.control_points = np.array(tmp_le_ps).T
            
            if tmp_te_ps:
                # print("tmp_te_ps:", tmp_te_ps)
                self.TE_PS = BSpline(self.DAEDALUS)
                self.TE_PS.control_points = np.array(tmp_te_ps).T
                # self.segments[i].skin.PS.u_rwd.control_points = np.array(tmp_le_ps).T
                # self.segments[i].skin.TE.u_fwd.control_points = np.array(tmp_le_ps).T

            if tmp_le_ss:
                # print("tmp_le_ss:", tmp_le_ss)
                self.LE_SS = BSpline(self.DAEDALUS)
                self.LE_SS.control_points = np.array(tmp_le_ss).T
                # self.segments[i].skin.SS.u_rwd.control_points = np.array(tmp_le_ps).T
                # self.segments[i].skin.LE.u_fwd.control_points = np.array(tmp_le_ps).T

            if tmp_te_ss:
                # print("tmp_te_ss:", tmp_te_ss)
                self.TE_SS = BSpline(self.DAEDALUS)
                self.TE_SS.control_points = np.array(tmp_te_ss).T
                # self.segments[i].skin.SS.u_fwd.control_points = np.array(tmp_le_ps).T
                # self.segments[i].skin.TE.u_uwd.control_points = np.array(tmp_le_ps).T

            degree = len(tmp_le_ps)-1
            self.logger.debug(f'Degree: {degree}')

            # Determine connection mode from wing attributes
            connection_mode = 'approximated'
            if hasattr(self, 'attrs') and 'connection' in self.attrs:
                connection_attr = self.attrs['connection'].value.lower()
                if 'interpolated' in connection_attr:
                    connection_mode = 'interpolated'
                elif 'approximated' in connection_attr:
                    connection_mode = 'approximated'
            
            self.logger.debug(f'Connection mode: {connection_mode}')

            self.LE_PS.create(mode=connection_mode)
            self.TE_PS.create(mode=connection_mode)
            self.LE_SS.create(mode=connection_mode)
            self.TE_SS.create(mode=connection_mode)
        
    def build_surface(self):
        self.logger.info("Building surface...")
        self.skin.build()

        self.logger.debug(f'WNGWB > Wing > build_connection > Connection between two segments established')


