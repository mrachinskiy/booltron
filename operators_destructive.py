# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2014-2018  Mikhail Rachinskiy
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


from bpy.types import Operator
from bpy.props import BoolProperty

from .preferences import BooltronPreferences
from .boolean_methods import BooleanMethods
from .mesh_utils import MeshUtils
from .object_utils import ObjectUtils
from . import versioning


class Setup(BooleanMethods, MeshUtils, ObjectUtils):
    if versioning.SOLVER_OPTION:
        solver = BooltronPreferences.destr_solver
    cleanup = BooltronPreferences.cleanup
    triangulate = BooltronPreferences.triangulate
    pos_correct = BooltronPreferences.destr_pos_correct
    pos_offset = BooltronPreferences.destr_pos_offset
    keep_objects = BoolProperty(name="Keep Objects", description="Do not remove selected objects after boolean operation (Shortcut: hold Alt when using the tool)", options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout

        if versioning.SOLVER_OPTION:
            split = layout.split()
            split.label("Boolean Solver")
            split.prop(self, "solver", text="")

        layout.prop(self, "cleanup")
        layout.prop(self, "triangulate")

        split = layout.split()
        split.prop(self, "pos_correct")
        split.prop(self, "pos_offset", text="")

        layout.prop(self, "keep_objects")

    def execute(self, context):
        self.object_prepare()
        self.boolean_adaptive()
        self.mesh_check(context.active_object)
        return {"FINISHED"}

    def invoke(self, context, event):
        obs = context.selected_objects

        if len(obs) < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        prefs = context.user_preferences.addons[__package__].preferences
        self.cleanup = prefs.cleanup
        self.triangulate = prefs.triangulate
        self.pos_correct = prefs.destr_pos_correct
        self.pos_offset = prefs.destr_pos_offset
        self.is_overlap = False
        self.keep_objects = event.alt
        self.local_view = bool(context.space_data.local_view)

        if versioning.SOLVER_OPTION:
            self.solver = prefs.destr_solver

        if len(obs) > 2 and self.mode != "NONE":
            obs.remove(context.active_object)
            self.is_overlap = self.object_overlap(obs)

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=300 * context.user_preferences.view.ui_scale)

        return self.execute(context)


class OBJECT_OT_booltron_destructive_union(Operator, Setup):
    bl_label = "Booltron Destructive Union"
    bl_description = "Combine selected objects"
    bl_idname = "object.booltron_destructive_union"
    bl_options = {"REGISTER", "UNDO"}

    mode = "UNION"


class OBJECT_OT_booltron_destructive_difference(Operator, Setup):
    bl_label = "Booltron Destructive Difference"
    bl_description = "Subtract selected objects from active object"
    bl_idname = "object.booltron_destructive_difference"
    bl_options = {"REGISTER", "UNDO"}

    mode = "DIFFERENCE"


class OBJECT_OT_booltron_destructive_intersect(Operator, Setup):
    bl_label = "Booltron Destructive Intersect"
    bl_description = "Keep the common part between active and selected objects"
    bl_idname = "object.booltron_destructive_intersect"
    bl_options = {"REGISTER", "UNDO"}

    mode = "INTERSECT"


class OBJECT_OT_booltron_destructive_slice(Operator, Setup):
    bl_label = "Booltron Destructive Slice"
    bl_description = "Slice active object along the volume of selected objects"
    bl_idname = "object.booltron_destructive_slice"
    bl_options = {"REGISTER", "UNDO"}

    mode = "NONE"

    def execute(self, context):
        space_data = context.space_data
        scene = context.scene
        self.object_prepare()

        ob1 = context.active_object
        ob1.select = False
        self.mesh_prepare(ob1, select=False)

        for ob2 in context.selected_objects:

            self.mesh_prepare(ob2, select=True)

            # Create copy of main object
            # ---------------------------------

            ob1_copy = ob1.copy()
            ob1_copy.data = ob1.data.copy()
            base = scene.objects.link(ob1_copy)

            if self.local_view:
                base.layers_from_view(space_data)

            ob1_copy.layers = ob1.layers
            ob1_copy.select = True

            # Main object difference
            # ---------------------------------

            scene.objects.active = ob1
            self.boolean_mod(ob1, ob2, "DIFFERENCE", terminate=False)

            if self.mesh_check(ob1):
                return {"FINISHED"}

            # Copy object intersect
            # ---------------------------------

            scene.objects.active = ob1_copy
            self.boolean_mod(ob1_copy, ob2, "INTERSECT")

            if self.mesh_check(ob1_copy):
                return {"FINISHED"}

            if self.cleanup:
                self.mesh_cleanup(ob1)

        return {"FINISHED"}
