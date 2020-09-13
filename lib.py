# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2020  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import bpy

import random

from mathutils import Vector


def object_offset(obs, offset):
    for ob in obs:
        x = random.uniform(-offset, offset)
        y = random.uniform(-offset, offset)
        z = random.uniform(-offset, offset)

        ob.matrix_basis.translation += Vector((x, y, z))


class ModUtils:
    __slots__ = ("apply", "remove_ob2", "threshold")

    def __init__(self, apply=False, remove_ob2=False, threshold=0.000001):
        self.apply = apply
        self.remove_ob2 = remove_ob2
        self.threshold = threshold

    def add(self, ob1, ob2, mode, name="Boolean", remove_ob2=None):
        if remove_ob2 is None:
            remove_ob2 = self.remove_ob2

        md = ob1.modifiers.new(name, "BOOLEAN")
        md.show_viewport = not self.apply
        md.operation = mode
        md.double_threshold = self.threshold
        md.object = ob2

        if self.apply:
            override = {"object": ob1}
            bpy.ops.object.modifier_apply(override, modifier=md.name)

        if remove_ob2:
            bpy.data.meshes.remove(ob2.data)
