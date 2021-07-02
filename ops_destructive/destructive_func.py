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


import bpy

from .. import var, lib
from . import mesh_lib


def cursor_state(func):
    def wrapper(*args):
        bpy.context.window.cursor_set("WAIT")
        result = func(*args)
        bpy.context.window.cursor_set("DEFAULT")
        return result
    return wrapper


def prepare_objects(self, context):
    ob1 = context.object
    obs = context.selected_objects
    if ob1.select_get():
        obs.remove(ob1)

    if self.keep_objects:
        space_data = context.space_data
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

    if self.use_pos_offset:
        lib.object_offset(obs, self.pos_offset)

    return obs


@cursor_state
def execute(self, context):
    Mesh = mesh_lib.Utils(self)
    boolean_mod = lib.ModUtils(self).add

    ob1 = context.object
    obs = prepare_objects(self, context)
    ob2 = obs.pop()

    if obs:
        if self.is_overlap:
            Mesh.prepare(ob2, select=True)
            for ob3 in obs:
                Mesh.prepare(ob3, select=True)
                boolean_mod(ob2, ob3, "UNION")
                if self.cleanup:
                    Mesh.cleanup(ob2)
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

    if self.cleanup:
        Mesh.cleanup(ob1)

    Mesh.check(ob1)

    return {"FINISHED"}


def invoke(self, context, event):
    obs = []
    app = obs.append

    for ob in context.selected_objects:
        if ob.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
            ob.select_set(False)
            continue
        app(ob)

    if len(obs) < 2:
        self.report({"ERROR"}, "At least two objects must be selected")
        return {"CANCELLED"}

    if self.first_run:
        self.first_run = False
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.solver = prefs.solver
        self.threshold = prefs.threshold
        self.use_pos_offset = prefs.use_pos_offset
        self.pos_offset = prefs.pos_offset
        self.merge_distance = prefs.merge_distance
        self.cleanup = prefs.cleanup
        self.triangulate = prefs.triangulate

    self.keep_objects = event.alt
    self.is_overlap = False

    if len(obs) > 2 and self.mode is not None:
        obs.remove(context.object)
        self.is_overlap = mesh_lib.detect_overlap(context, obs, self.merge_distance)

    if event.ctrl:
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    return self.execute(context)


@cursor_state
def execute_slice(self, context):
    Mesh = mesh_lib.Utils(self)
    boolean_mod = lib.ModUtils(self).add

    space_data = context.space_data
    use_local_view = bool(space_data.local_view)

    ob1 = context.object
    obs = prepare_objects(self, context)

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

        boolean_mod(ob1, ob2, "DIFFERENCE", remove_ob2=False)

        if Mesh.check(ob1):
            return {"FINISHED"}

        # Copy object intersect
        # ---------------------------------

        boolean_mod(ob1_copy, ob2, "INTERSECT")

        if Mesh.check(ob1_copy):
            return {"FINISHED"}

        if self.cleanup:
            Mesh.cleanup(ob1)

    ob1.select_set(False)
    context.view_layer.objects.active = ob1_copy

    return {"FINISHED"}
