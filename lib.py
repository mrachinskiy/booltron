# SPDX-FileCopyrightText: 2014-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import random
from typing import Optional

import bpy
from bpy.types import Object
from mathutils import Vector


def object_offset(obs: list[Object], offset: float) -> None:
    for ob in obs:
        x = random.uniform(-offset, offset)
        y = random.uniform(-offset, offset)
        z = random.uniform(-offset, offset)

        ob.matrix_basis.translation += Vector((x, y, z))


class ModUtils:
    __slots__ = "is_destructive", "solver", "threshold", "use_self", "use_hole_tolerant"

    def __init__(self, is_destructive: bool) -> None:
        self.is_destructive = is_destructive
        if is_destructive:
            props = bpy.context.window_manager.booltron.destructive
        else:
            props = bpy.context.window_manager.booltron.non_destructive
        self.solver = props.solver
        self.threshold = props.threshold
        self.use_self = props.use_self
        self.use_hole_tolerant = props.use_hole_tolerant

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
            with bpy.context.temp_override(object=ob1):
                bpy.ops.object.modifier_apply(modifier=md.name)

        if remove_ob2:
            bpy.data.meshes.remove(ob2.data)
