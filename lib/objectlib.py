# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
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


def prepare_objects(keep_objects: bool) -> tuple[Object, list[Object]]:
    props = bpy.context.window_manager.booltron.destructive

    ob1 = bpy.context.object
    obs = bpy.context.selected_objects
    if ob1.select_get():
        obs.remove(ob1)

    if keep_objects:
        obs_copy = []

        for ob in obs:
            ob_copy = ob.copy()
            ob_copy.data = ob.data.copy()
            ob_link(ob_copy, ob.users_collection)
            ob_copy.select_set(True)
            ob.select_set(False)
            obs_copy.append(ob_copy)

        obs = obs_copy

    bpy.ops.object.make_single_user(object=True, obdata=True)
    bpy.ops.object.convert(target="MESH")

    if props.use_loc_rnd:
        object_offset(obs, props.loc_offset)

    return ob1, obs
