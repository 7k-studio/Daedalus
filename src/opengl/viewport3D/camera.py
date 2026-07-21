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

import math
from PyQt6 import QtGui


class Camera3D:
    """Small camera abstraction for the 3D viewport."""

    def __init__(self, target=None, distance=8.0, yaw=45.0, pitch=20.0,
                 fov_y=45.0, near=0.05, far=1000.0):
        self.target = target if target is not None else QtGui.QVector3D(0.0, 0.0, 0.0)
        self.distance = float(distance)
        self.yaw = float(yaw)
        self.pitch = float(pitch)
        self.fov_y = float(fov_y)
        self.near = float(near)
        self.far = float(far)

    def eye_position(self):
        eye = self.spherical_to_cartesian(
            self.distance,
            math.radians(self.yaw),
            math.radians(self.pitch),
        )
        return QtGui.QVector3D(eye[0], eye[1], eye[2]) + self.target

    def spherical_to_cartesian(self, r, yaw_rad, pitch_rad):
        x = r * math.cos(pitch_rad) * math.sin(yaw_rad)
        y = r * math.sin(pitch_rad)
        z = r * math.cos(pitch_rad) * math.cos(yaw_rad)
        return x, y, z

    def basis(self):
        yaw_r = math.radians(self.yaw)
        pitch_r = math.radians(self.pitch)

        fx = -math.cos(pitch_r) * math.sin(yaw_r)
        fy = -math.sin(pitch_r)
        fz = -math.cos(pitch_r) * math.cos(yaw_r)

        forward = QtGui.QVector3D(fx, fy, fz)
        forward.normalize()

        up = QtGui.QVector3D(0.0, 1.0, 0.0)
        right = QtGui.QVector3D.crossProduct(forward, up)
        right.normalize()

        up_corrected = QtGui.QVector3D.crossProduct(right, forward)
        up_corrected.normalize()
        return right, up_corrected, forward

    def pan(self, dx, dy, viewport_width, viewport_height):
        right, up, _ = self.basis()
        width = max(1, viewport_width)
        height = max(1, viewport_height)

        scale_y = 2.0 * self.distance * math.tan(math.radians(self.fov_y * 0.5)) / height
        scale_x = scale_y * (width / float(height))

        move = right * (-dx * scale_x) + up * (dy * scale_y)
        self.target += move

    def dolly(self, dy):
        factor = math.pow(1.01, dy)
        self.distance = max(0.05, min(self.far * 0.5, self.distance * factor))

    def reset(self):
        self.target = QtGui.QVector3D(0.0, 0.0, 0.0)
        self.distance = 8.0
        self.yaw = 45.0
        self.pitch = 20.0

    def position(self, yaw, pitch):
        self.target = QtGui.QVector3D(0.0, 0.0, 0.0)
        self.distance = 8.0
        self.yaw = yaw
        self.pitch = pitch
