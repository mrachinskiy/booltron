# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2014-2022 Mikhail Rachinskiy

from bpy.types import Operator
from bpy.props import BoolProperty


class Nondestructive:
    first_run: BoolProperty(default=True, options={"HIDDEN"})
    is_destructive = False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        props = context.window_manager.booltron.non_destructive

        layout.label(text="Modifier")
        col = layout.box().column()
        col.prop(props, "solver")

        if props.solver == "FAST":
            col.prop(props, "threshold")
        else:
            col.prop(props, "use_self")
            col.prop(props, "use_hole_tolerant")

        layout.separator()

        layout.label(text="Secondary Object")
        col = layout.box().column()
        row = col.row(heading="Randomize Location")
        row.prop(props, "use_loc_rnd", text="")
        sub = row.row()
        sub.enabled = props.use_loc_rnd
        sub.prop(props, "loc_offset", text="")
        col.prop(props, "display_secondary")

        layout.separator()

        layout.label(text="Combined Object")
        layout.box().prop(props, "display_combined")

        layout.separator()

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
