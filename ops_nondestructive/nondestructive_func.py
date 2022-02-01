# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2022  Mikhail Rachinskiy
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


def execute(self, context):
    boolean_mod = lib.ModUtils(self).add

    ob1 = context.object
    obs = context.selected_objects
    if ob1.select_get():
        obs.remove(ob1)

    if self.use_pos_offset:
        lib.object_offset(obs, self.pos_offset)

    # Prepare combined object
    # ----------------------------------

    for md in ob1.modifiers:
        if (
            md.type == "BOOLEAN" and
            md.operation == self.mode and
            md.object and "booltron_combined" in md.object
        ):
            ob2 = md.object
            break
    else:
        ob2_name = f"{ob1.name} COMBINED {self.mode[:3]}"
        me = bpy.data.meshes.new(ob2_name)
        ob2 = bpy.data.objects.new(ob2_name, me)

        for coll in obs[0].users_collection:
            coll.objects.link(ob2)

        mod_name = self.mode[:3] + " COMBINED"
        boolean_mod(ob1, ob2, self.mode, name=mod_name)

        ob2["booltron_combined"] = self.mode

    ob2.display_type = self.display_combined

    # Merge secondary objects
    # ----------------------------------

    ob2_mats = ob2.data.materials

    for ob in obs:
        boolean_mod(ob2, ob, "UNION")
        ob.display_type = self.display_secondary
        for mat in ob.data.materials:
            if mat is not None and mat.name not in ob2_mats:
                ob2_mats.append(mat)

    return {"FINISHED"}


def invoke(self, context, event):
    obs = []
    app = obs.append

    for ob in context.selected_objects:
        if ob.type != "MESH":
            ob.select_set(False)
        app(ob)

    if len(obs) < 2 or context.object.type != "MESH":
        self.report({"ERROR"}, "At least two Mesh objects must be selected")
        return {"CANCELLED"}

    if self.first_run:
        self.first_run = False
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.solver = prefs.solver
        self.threshold = prefs.threshold
        self.use_pos_offset = prefs.use_pos_offset
        self.pos_offset = prefs.pos_offset
        self.display_secondary = prefs.display_secondary
        self.display_combined = prefs.display_combined

    if event.ctrl:
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    return self.execute(context)


def execute_remove(self, context):
    obs = set(ob for ob in context.selected_objects if "booltron_combined" not in ob)
    is_empty = False

    if not obs:
        return {"CANCELLED"}

    for ob in context.scene.objects:
        if "booltron_combined" in ob:

            for md in ob.modifiers:
                if md.type == "BOOLEAN" and (not md.object or md.object in obs):
                    ob.modifiers.remove(md)

            for md in ob.modifiers:
                if md.type == "BOOLEAN":
                    break
            else:
                is_empty = True
                bpy.data.meshes.remove(ob.data)

    if is_empty:
        for ob in context.scene.objects:
            if ob.type == "MESH":
                for md in ob.modifiers:
                    if md.type == "BOOLEAN" and not md.object:
                        ob.modifiers.remove(md)

    for ob in obs:
        ob.display_type = "TEXTURED"

    return {"FINISHED"}
