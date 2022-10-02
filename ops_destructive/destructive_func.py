# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2014-2022 Mikhail Rachinskiy

import bpy
from bpy.types import Object

from .. import var, lib
from . import mesh_lib


def _cursor_state(func):
    def wrapper(*args):
        bpy.context.window.cursor_set("WAIT")
        result = func(*args)
        bpy.context.window.cursor_set("DEFAULT")
        return result
    return wrapper


def _prepare_objects(self) -> tuple[Object, list[Object]]:
    ob1 = bpy.context.object
    obs = bpy.context.selected_objects
    if ob1.select_get():
        obs.remove(ob1)

    if self.keep_objects:
        space_data = bpy.context.space_data
        use_local_view = bool(space_data.local_view)
        obs_copy = []
        app = obs_copy.append

        for ob in obs:
            ob_copy = ob.copy()
            ob_copy.data = ob.data.copy()

            for coll in ob.users_collection:
                coll.objects.link(ob_copy)

            if use_local_view:
                ob_copy.local_view_set(space_data, True)

            ob_copy.select_set(True)
            ob.select_set(False)
            app(ob_copy)

        obs = obs_copy

    bpy.ops.object.make_single_user(object=True, obdata=True)
    bpy.ops.object.convert(target="MESH")

    if self.use_loc_rnd:
        lib.object_offset(obs, self.loc_offset)

    return ob1, obs


@_cursor_state
def execute(self, context):
    Mesh = mesh_lib.Utils(self)
    boolean_mod = lib.ModUtils(self).add

    ob1, obs = _prepare_objects(self)
    ob2 = obs.pop()

    if obs:
        if self.is_overlap:
            Mesh.prepare(ob2, select=True)
            for ob3 in obs:
                Mesh.prepare(ob3, select=True)
                boolean_mod(ob2, ob3, "UNION")
        else:
            obs.append(ob2)
            override = {
                "active_object": ob2,
                "selected_editable_objects": obs,
            }
            bpy.ops.object.join(override)

    if not self.is_overlap:
        Mesh.prepare(ob2, select=True)

    Mesh.prepare(ob1, select=False)
    boolean_mod(ob1, ob2, self.mode)

    Mesh.check(ob1)

    return {"FINISHED"}


def invoke(self, context, event):
    if context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.ed.undo_push()

    for ob in context.selected_objects:
        if ob.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
            ob.select_set(False)

    obs = context.selected_objects

    if len(obs) < 2:
        self.report({"ERROR"}, "At least two objects must be selected")
        return {"CANCELLED"}

    if len(obs) > 2 and self.mode != "SLICE":
        obs.remove(context.object)
        self.is_overlap = mesh_lib.detect_overlap(obs, self.merge_distance)

    if self.first_run or not event.ctrl:
        self.first_run = False
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.solver = prefs.solver
        self.threshold = prefs.threshold
        self.use_loc_rnd = prefs.use_loc_rnd
        self.loc_offset = prefs.loc_offset
        self.merge_distance = prefs.merge_distance

    self.keep_objects = event.alt

    if event.ctrl:
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    return self.execute(context)


@_cursor_state
def execute_slice(self, context):
    Mesh = mesh_lib.Utils(self)
    boolean_mod = lib.ModUtils(self).add

    space_data = context.space_data
    use_local_view = bool(space_data.local_view)

    ob1, obs = _prepare_objects(self)

    Mesh.prepare(ob1, select=False)

    for ob2 in obs:

        Mesh.prepare(ob2, select=True)

        # Create copy of main object
        # ---------------------------------

        ob1_copy = ob1.copy()
        ob1_copy.data = ob1.data.copy()

        for coll in ob1.users_collection:
            coll.objects.link(ob1_copy)

        if use_local_view:
            ob1_copy.local_view_set(space_data, True)

        ob1_copy.select_set(True)

        # Main object difference
        # ---------------------------------

        ob2.matrix_world.translation += self.overlap_distance / 2

        boolean_mod(ob1, ob2, "DIFFERENCE", remove_ob2=False)

        if Mesh.check(ob1):
            return {"FINISHED"}

        # Main object copy intersect
        # ---------------------------------

        ob2.matrix_world.translation -= self.overlap_distance

        boolean_mod(ob1_copy, ob2, "INTERSECT")

        if Mesh.check(ob1_copy):
            return {"FINISHED"}

    ob1.select_set(False)
    context.view_layer.objects.active = ob1_copy

    return {"FINISHED"}
