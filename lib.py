# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2014-2022 Mikhail Rachinskiy

import random
from typing import Optional

import bpy
from bpy.types import Object, Operator
from mathutils import Vector


def object_offset(obs: list[Object], offset: float) -> None:
    for ob in obs:
        x = random.uniform(-offset, offset)
        y = random.uniform(-offset, offset)
        z = random.uniform(-offset, offset)

        ob.matrix_basis.translation += Vector((x, y, z))


class ModUtils:
    __slots__ = ("is_destructive", "solver", "threshold", "use_self", "use_hole_tolerant")

    def __init__(self, op: Operator) -> None:
        for prop in self.__slots__:
            setattr(self, prop, getattr(op, prop))

    def add(self, ob1: Object, ob2: Object, mode: str, name: str = "Boolean", remove_ob2: Optional[bool] = None) -> None:
        if remove_ob2 is None:
            remove_ob2 = self.is_destructive

        md = ob1.modifiers.new(name, "BOOLEAN")
        md.show_viewport = not self.is_destructive
        md.operation = mode
        md.solver = self.solver
        md.use_self = self.use_self
        md.use_hole_tolerant = self.use_hole_tolerant
        md.double_threshold = self.threshold
        md.object = ob2

        if self.is_destructive:
            override = {"object": ob1}
            bpy.ops.object.modifier_apply(override, modifier=md.name)

        if remove_ob2:
            bpy.data.meshes.remove(ob2.data)
