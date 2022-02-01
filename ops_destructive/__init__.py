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


from bpy.types import Operator
from bpy.props import BoolProperty

from .. import preferences


class Destructive(preferences.ToolProps):
    keep_objects: BoolProperty(
        name="Keep Objects",
        description=(
            "Do not remove selected objects after boolean operation "
            "(Shortcut: hold Alt when using the tool)"
        ),
        options={"SKIP_SAVE"},
    )
    first_run: BoolProperty(default=True, options={"HIDDEN"})
    is_destructive = True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(text="Modifier")
        col = layout.box().column()
        col.prop(self, "solver")

        if self.solver == "FAST":
            col.prop(self, "threshold")
        else:
            col.prop(self, "use_self")
            col.prop(self, "use_hole_tolerant")

        layout.separator()

        layout.label(text="Secondary Object")
        col = layout.box().column()
        row = col.row(heading="Correct Position")
        row.prop(self, "use_pos_offset", text="")
        sub = row.row()
        sub.enabled = self.use_pos_offset
        sub.prop(self, "pos_offset", text="")
        col.prop(self, "keep_objects")

        layout.separator()

        layout.label(text="Pre-processing")
        layout.box().prop(self, "merge_distance")

        layout.separator()

    def execute(self, context):
        from . import destructive_func
        return destructive_func.execute(self, context)

    def invoke(self, context, event):
        from . import destructive_func
        return destructive_func.invoke(self, context, event)


class OBJECT_OT_destructive_union(Destructive, Operator):
    bl_label = "Union"
    bl_description = "Combine selected objects"
    bl_idname = "object.booltron_destructive_union"
    bl_options = {"REGISTER", "UNDO"}

    mode = "UNION"


class OBJECT_OT_destructive_difference(Destructive, Operator):
    bl_label = "Difference"
    bl_description = "Subtract selected objects from active object"
    bl_idname = "object.booltron_destructive_difference"
    bl_options = {"REGISTER", "UNDO"}

    mode = "DIFFERENCE"


class OBJECT_OT_destructive_intersect(Destructive, Operator):
    bl_label = "Intersect"
    bl_description = "Keep the common part between active and selected objects"
    bl_idname = "object.booltron_destructive_intersect"
    bl_options = {"REGISTER", "UNDO"}

    mode = "INTERSECT"


class OBJECT_OT_destructive_slice(Destructive, Operator):
    bl_label = "Slice"
    bl_description = "Slice active object along the volume of selected objects"
    bl_idname = "object.booltron_destructive_slice"
    bl_options = {"REGISTER", "UNDO"}

    mode = None

    def execute(self, context):
        from . import destructive_func
        return destructive_func.execute_slice(self, context)
