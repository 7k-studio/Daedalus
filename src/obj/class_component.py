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

from src.obj.class_param import Param, M, DEG

class Component:
    def __init__(self, program=None, project=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.PROJECT = project

        self.name = 'Component'
        self.info = {'creation_date': '',
                      'modification_date': ''}
        
        self.params = {
            'origin_X': Param('origin_X', 0, M),
            'origin_Y': Param('origin_Y', 0, M),
            'origin_Z': Param('origin_Z', 0, M),
        }

        self.attrs = {
            
        }

        self.stats = {
            'Test': Param('test', 0, M)
        }

        self.wings = []

    def move(self, cmp_X:float, cmp_Y:float, cmp_Z:float):

        self.logger.debug(f"WNGWB > Moving COMPONENT geometry by X:{cmp_X}, Y:{cmp_Y}, Z:{cmp_Z}...")

        tmp_X = self.params['origin_X'].get() + cmp_X
        tmp_Y = self.params['origin_Y'].get() + cmp_Y
        tmp_Z = self.params['origin_Z'].get() + cmp_Z

        return tmp_X, tmp_Y, tmp_Z
    
    def update(self, dummy1, dummy2, dummy3):
        self.logger.info("Updating COMPONENT...")
        self.logger.debug("   This function is pointless :( ")
        #self.params['origin_X'] = 0
        #self.params['origin_Y'] = 0
        #self.params['origin_Z'] = 0

    def transform(self, grandparent_index):

        cmp_X = self.PROJECT.components[grandparent_index].params['origin_X'].get()
        cmp_Y = self.PROJECT.components[grandparent_index].params['origin_Y'].get()
        cmp_Z = self.PROJECT.components[grandparent_index].params['origin_Z'].get()

        self.logger.info("Transforming component...")
        self.params['origin_X'].set(self.params['origin_X'].get() + cmp_X)
        self.params['origin_Y'].set(self.params['origin_Y'].get() + cmp_Y)
        self.params['origin_Z'].set(self.params['origin_Z'].get() + cmp_Z)
        self.logger.debug("Done!")
