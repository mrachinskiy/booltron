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
from bpy.props import BoolProperty, FloatProperty, EnumProperty

from .. import var


class Nondestructive:
    solver: EnumProperty(
        name="Solver",
        description="Method for calculating booleans",
        items=(
            ("FAST", "Fast", "Simple solver for the best performance, without support for overlapping geometry"),
            ("EXACT", "Exact", "Advanced solver for the best result"),
        ),
        default="FAST",
    )
    use_self: BoolProperty(
        name="Self",
        description="Allow self-intersection in operands",
    )
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
    threshold: FloatProperty(
        name="Overlap Threshold",
        description="Threshold for checking overlapping geometry",
        default=0.000001,
        min=0.0,
        step=0.0001,
        precision=6,
    )
    display_secondary: EnumProperty(
        name="Secondary Object",
        description="How to display object in viewport",
        items=(
            ("BOUNDS", "Bounds", ""),
            ("WIRE", "Wire", ""),
            ("SOLID", "Solid", ""),
            ("TEXTURED", "Textured", ""),
        ),
        default="WIRE",
    )
    display_combined: EnumProperty(
        name="Combined Object",
        description="How to display object in viewport",
        items=(
            ("BOUNDS", "Bounds", ""),
            ("WIRE", "Wire", ""),
            ("SOLID", "Solid", ""),
            ("TEXTURED", "Textured", ""),
        ),
        default="BOUNDS",
    )
    first_run: BoolProperty(default=True, options={"HIDDEN"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(text="Modifier")

        if var.ver_291:
            col = layout.column()
            col.prop(self, "solver")

            if self.solver == "FAST":
                col.prop(self, "threshold")
            else:
                col.prop(self, "use_self")

        else:
            layout.prop(self, "threshold")

        layout.separator()

        layout.label(text="Object")
        row = layout.row(heading="Correct Position")
        row.prop(self, "use_pos_offset", text="")
        sub = row.row()
        sub.enabled = self.use_pos_offset
        sub.prop(self, "pos_offset", text="")

        layout.separator()

        layout.label(text="Viewport Display")
        col = layout.column()
        col.prop(self, "display_secondary")
        col.prop(self, "display_combined")

    def execute(self, context):
        from . import nondestructive_func
        return nondestructive_func.execute(self, context)

    def invoke(self, context, event):
        from . import nondestructive_func
        return nondestructive_func.invoke(self, context, event)


class OBJECT_OT_nondestructive_union(Nondestructive, Operator):
    bl_label = "Union"
    bl_description = "Combine active (primary) and selected (secondary) objects"
    bl_idname = "object.booltron_nondestructive_union"
    bl_options = {"REGISTER", "UNDO"}

    mode = "UNION"


class OBJECT_OT_nondestructive_difference(Nondestructive, Operator):
    bl_label = "Difference"
    bl_description = "Subtract selected (secondary) objects from active (primary) object"
    bl_idname = "object.booltron_nondestructive_difference"
    bl_options = {"REGISTER", "UNDO"}

    mode = "DIFFERENCE"


class OBJECT_OT_nondestructive_intersect(Nondestructive, Operator):
    bl_label = "Intersect"
    bl_description = "Keep the common part between active (primary) and selected (secondary) objects"
    bl_idname = "object.booltron_nondestructive_intersect"
    bl_options = {"REGISTER", "UNDO"}

    mode = "INTERSECT"


class OBJECT_OT_nondestructive_remove(Operator):
    bl_label = "Dismiss"
    bl_description = "Dismiss selected secondary objects from boolean operation"
    bl_idname = "object.booltron_nondestructive_remove"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from . import nondestructive_func
        return nondestructive_func.execute_remove(self, context)
