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

class Cylinder:
    def __init__(self):
        pass

class Rectangle:
    def __init__(self):
        pass
    
class Wheels:
    def __init__(self):
        self.ground_clearance = 0.030
        
        self.diameter = 0.254
        self.width = 0.150
        
        self.wheel_front_X = -0.700
        self.wheel_front_Y = self.diameter/2
        
        self.wheel_rear_X = 0.700
        self.wheel_rear_Y = self.diameter/2

        self.wheel_front_Z = 1.0
        self.wheel_rear_Z = 1.1
        
class FrontWing:
    def __init__(self):
        wheels = Wheels()
        self.X_front_limit = wheels.wheel_front_X - wheels.diameter/2 - 700
        self.X_back_limit = wheels.wheel_front_X - wheels.diameter/2 - 75
        self.outter_height = 250
        self.inner_height = 500
        self.width = self.X_back_limit - self.X_front_limit
        
class RearWing:
    def __init__(self):
        wheels = Wheels()
        self.X_front_limit = wheels.wheel_rear_X - wheels.diameter/2 - 100
        self.X_back_limit = wheels.wheel_rear_X + wheels.diameter/2 + 250
        self.X_back_wheel_limit = wheels.wheel_rear_X + wheels.diameter/2 + 75
        self.inner_width = self.X_back_limit - self.X_front_limit
        self.outter_width = self.X_back_limit - self.X_back_wheel_limit
        self.outter_height = 500
        self.inner_height = 1200