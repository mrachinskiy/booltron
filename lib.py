# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2021  Mikhail Rachinskiy
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


import random
from typing import Iterable, Optional

import bpy
from bpy.types import Object
from mathutils import Vector


def object_offset(obs: Iterable[Object], offset: float):
    for ob in obs:
        x = random.uniform(-offset, offset)
        y = random.uniform(-offset, offset)
        z = random.uniform(-offset, offset)

        ob.matrix_basis.translation += Vector((x, y, z))


class ModUtils:
    __slots__ = ("apply", "remove_ob2", "solver", "threshold", "use_self")

    def __init__(self, apply=False, remove_ob2=False, solver="FAST", threshold=0.000001, use_self=False):
        self.apply = apply
        self.remove_ob2 = remove_ob2
        self.solver = solver
        self.threshold = threshold
        self.use_self = use_self

    def add(self, ob1: Object, ob2: Object, mode: str, name: str = "Boolean", remove_ob2: Optional[bool] = None):
        if remove_ob2 is None:
            remove_ob2 = self.remove_ob2

        md = ob1.modifiers.new(name, "BOOLEAN")
        md.show_viewport = not self.apply
        md.operation = mode
        if hasattr(md, "solver"):
            md.solver = self.solver
        if hasattr(md, "use_self"):
            md.use_self = self.use_self
        md.double_threshold = self.threshold
        md.object = ob2

        if self.apply:
            override = {"object": ob1}
            bpy.ops.object.modifier_apply(override, modifier=md.name)

        if remove_ob2:
            bpy.data.meshes.remove(ob2.data)
