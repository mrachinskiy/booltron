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


import bpy
from bpy.types import Operator

from .preferences import OperatorProps
from .boolean_methods import BooleanMethods
from .mesh_utils import MeshUtils
from . import versioning


class Setup(OperatorProps, BooleanMethods, MeshUtils):

    def draw(self, context):
        layout = self.layout

        if versioning.SOLVER_OPTION:
            split = layout.split()
            split.label("Boolean Solver")
            split.prop(self, "solver", text="")

        split = layout.split()
        split.label("Boolean Method")
        split.prop(self, "method", text="")

        layout.prop(self, "triangulate")

        split = layout.split()
        split.prop(self, "pos_correct", text="Correct Position")
        split.prop(self, "pos_offset", text="")

    def invoke(self, context, event):
        if len(context.selected_objects) < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        prefs = context.user_preferences.addons[__package__].preferences
        self.solver = prefs.solver
        self.method = prefs.method
        self.triangulate = prefs.triangulate
        self.pos_correct = prefs.pos_correct
        self.pos_offset = prefs.pos_offset

        return self.execute(context)


class OBJECT_OT_booltron_union(Operator, Setup):
    bl_label = "Booltron Union"
    bl_description = "Combine selected objects"
    bl_idname = "object.booltron_union"
    bl_options = {"REGISTER", "UNDO"}

    mode = "UNION"

    def execute(self, context):
        self.prepare_selected()

        if self.method == "OPTIMIZED":
            self.boolean_optimized()

            if not self.is_manifold(context.active_object):
                return {"FINISHED"}

            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.separate(type="LOOSE")
            bpy.ops.object.mode_set(mode="OBJECT")

            if len(context.selected_objects) != 1:
                self.boolean_batch()

                if not self.is_manifold(context.active_object):
                    return {"FINISHED"}

        else:
            self.boolean_batch()

            if not self.is_manifold(context.active_object):
                return {"FINISHED"}

        return {"FINISHED"}


class OBJECT_OT_booltron_difference(Operator, Setup):
    bl_label = "Booltron Difference"
    bl_description = "Subtract selected objects from active object"
    bl_idname = "object.booltron_difference"
    bl_options = {"REGISTER", "UNDO"}

    mode = "DIFFERENCE"

    def execute(self, context):
        self.prepare_selected()

        if self.method == "OPTIMIZED":
            self.boolean_optimized()
        else:
            self.boolean_batch()

        if not self.is_manifold(context.active_object):
            return {"FINISHED"}

        return {"FINISHED"}


class OBJECT_OT_booltron_intersect(Operator, Setup):
    bl_label = "Booltron Intersect"
    bl_description = "Keep the common part of all selected objects"
    bl_idname = "object.booltron_intersect"
    bl_options = {"REGISTER", "UNDO"}

    mode = "INTERSECT"

    def execute(self, context):
        self.prepare_selected()
        self.boolean_batch()

        if not self.is_manifold(context.active_object):
            return {"FINISHED"}

        return {"FINISHED"}


class OBJECT_OT_booltron_slice(Operator, Setup):
    bl_label = "Booltron Slice"
    bl_description = "Slice active object along the volume of selected objects"
    bl_idname = "object.booltron_slice"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        cleanup = self.method == "BATCH_CLEANUP"
        scene = context.scene
        self.prepare_selected()

        ob1 = context.active_object
        ob1.select = False
        self.mesh_selection(ob1, "DESELECT")

        for ob2 in context.selected_objects:

            self.mesh_selection(ob2, "SELECT")

            # Create copy of main object
            # ---------------------------------

            ob1_copy = ob1.copy()
            ob1_copy.data = ob1.data.copy()
            scene.objects.link(ob1_copy)
            ob1_copy.layers = ob1.layers
            ob1_copy.select = True

            # Main object difference
            # ---------------------------------

            scene.objects.active = ob1
            self.boolean_mod(ob1, ob2, "DIFFERENCE", terminate=False)

            if not self.is_manifold(ob1):
                return {"FINISHED"}

            # Copy object intersect
            # ---------------------------------

            scene.objects.active = ob1_copy
            self.boolean_mod(ob1_copy, ob2, "INTERSECT")

            if not self.is_manifold(ob1_copy):
                return {"FINISHED"}

            if cleanup:
                self.mesh_cleanup(ob1)

        return {"FINISHED"}


class OBJECT_OT_booltron_subtract(Operator, Setup):
    bl_label = "Booltron Subtract"
    bl_description = "Subtract selected objects from active object, subtracted objects will not be removed"
    bl_idname = "object.booltron_subtract"
    bl_options = {"REGISTER", "UNDO"}

    mode = "DIFFERENCE"

    def execute(self, context):
        scene = context.scene

        # Create subtract object copies
        # ---------------------------------

        oba = context.active_object
        oba.select = False

        obs = context.selected_objects
        obs_copy = []
        oba.select = True

        for ob in obs:
            ob_copy = ob.copy()
            ob_copy.data = ob.data.copy()
            scene.objects.link(ob_copy)

            obs_copy.append(ob_copy)

            ob.select = False

        # Boolean operations
        # ---------------------------------

        self.prepare_selected()

        if self.method == "OPTIMIZED":
            self.boolean_optimized()
        else:
            self.boolean_batch()

        # Restore selection
        # ---------------------------------

        for ob in obs:
            ob.select = True

        oba.select = False

        return {"FINISHED"}
