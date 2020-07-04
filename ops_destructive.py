# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2020  Mikhail Rachinskiy
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
from bpy.props import BoolProperty, FloatProperty

from .boolean_methods import BooleanMethods
from .mesh_utils import MeshUtils
from .object_utils import ObjectUtils


class Setup(BooleanMethods, MeshUtils, ObjectUtils):
    use_pos_offset: BoolProperty(
        name="Correct Position",
        description=(
            "Shift objects position for a very small amount to avoid coplanar "
            "geometry errors during boolean operation (does not affect active object)"
        ),
    )
    pos_offset: FloatProperty(
        name="Position Offset",
        description="Position offset is randomly generated for each object in range [-x, +x] input value",
        default=0.005,
        min=0.0,
        step=0.01,
        precision=3,
        unit="LENGTH",
    )
    double_threshold: FloatProperty(
        name="Overlap Threshold",
        description="Threshold for checking overlapping geometry",
        default=0.000001,
        min=0.0,
        step=0.0001,
        precision=6,
    )
    merge_distance: FloatProperty(
        name="Merge Distance",
        description="Minimum distance between elements to merge",
        default=0.0002,
        min=0.00001,
        step=0.01,
        precision=5,
        unit="LENGTH",
    )
    cleanup: BoolProperty(
        name="Mesh Cleanup",
        description=(
            "Perform mesh cleanup in between boolean operations, "
            "enabling this option will greatly affect performance of a boolean operation"
        ),
    )
    triangulate: BoolProperty(
        name="Triangulate",
        description=(
            "Triangulate geometry before boolean operation, "
            "in some cases may improve result of a boolean operation"
        ),
    )
    keep_objects: BoolProperty(
        name="Keep Objects",
        description=(
            "Do not remove selected objects after boolean operation "
            "(Shortcut: hold Alt when using the tool)"
        ),
        options={"SKIP_SAVE"},
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(self, "double_threshold")

        split = col.split(factor=0.49)
        split.prop(self, "use_pos_offset")
        sub = split.row()
        sub.enabled = self.use_pos_offset
        sub.prop(self, "pos_offset", text="")

        col.prop(self, "merge_distance")
        col.prop(self, "cleanup")
        col.prop(self, "triangulate")
        col.prop(self, "keep_objects")

    def execute(self, context):
        self.object_prepare(context)
        self.boolean_adaptive(context)
        self.mesh_check(context.object)
        return {"FINISHED"}

    def invoke(self, context, event):
        obs = context.selected_objects

        if len(obs) < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        prefs = context.preferences.addons[__package__].preferences
        self.double_threshold = prefs.destr_double_threshold
        self.use_pos_offset = prefs.destr_use_pos_offset
        self.pos_offset = prefs.destr_pos_offset
        self.merge_distance = prefs.merge_distance
        self.cleanup = prefs.cleanup
        self.triangulate = prefs.triangulate
        self.keep_objects = event.alt
        self.is_overlap = False

        if len(obs) > 2 and self.mode != "NONE":
            obs.remove(context.object)
            self.is_overlap = self.object_overlap(context, obs)

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        return self.execute(context)


class OBJECT_OT_destructive_union(Setup, Operator):
    bl_label = "Union"
    bl_description = "Combine selected objects"
    bl_idname = "object.booltron_destructive_union"
    bl_options = {"REGISTER", "UNDO"}

    mode = "UNION"


class OBJECT_OT_destructive_difference(Setup, Operator):
    bl_label = "Difference"
    bl_description = "Subtract selected objects from active object"
    bl_idname = "object.booltron_destructive_difference"
    bl_options = {"REGISTER", "UNDO"}

    mode = "DIFFERENCE"


class OBJECT_OT_destructive_intersect(Setup, Operator):
    bl_label = "Intersect"
    bl_description = "Keep the common part between active and selected objects"
    bl_idname = "object.booltron_destructive_intersect"
    bl_options = {"REGISTER", "UNDO"}

    mode = "INTERSECT"


class OBJECT_OT_destructive_slice(Setup, Operator):
    bl_label = "Slice"
    bl_description = "Slice active object along the volume of selected objects"
    bl_idname = "object.booltron_destructive_slice"
    bl_options = {"REGISTER", "UNDO"}

    mode = "NONE"

    def execute(self, context):
        space_data = context.space_data
        use_local_view = bool(space_data.local_view)
        self.object_prepare(context)

        ob1 = context.object
        ob1.select_set(False)
        self.mesh_prepare(ob1, select=False)

        for ob2 in context.selected_objects:

            self.mesh_prepare(ob2, select=True)

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

            self.boolean_mod(ob1, ob2, "DIFFERENCE", terminate=False)

            if self.mesh_check(ob1):
                return {"FINISHED"}

            # Copy object intersect
            # ---------------------------------

            self.boolean_mod(ob1_copy, ob2, "INTERSECT")

            if self.mesh_check(ob1_copy):
                return {"FINISHED"}

            if self.cleanup:
                self.mesh_cleanup(ob1)

        context.view_layer.objects.active = ob1_copy

        return {"FINISHED"}
