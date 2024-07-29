# SPDX-FileCopyrightText: 2014-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import random

import bpy
from bpy.types import Collection, Object
from mathutils import Vector


def object_offset(obs: list[Object], offset: float) -> None:
    for ob in obs:
        x = random.uniform(-offset, offset)
        y = random.uniform(-offset, offset)
        z = random.uniform(-offset, offset)

        ob.matrix_basis.translation += Vector((x, y, z))


def ob_link(ob: Object, colls: tuple[Collection]) -> None:
    for coll in colls:
        coll.objects.link(ob)

    if (sd := bpy.context.space_data).local_view:
        ob.local_view_set(sd, True)
