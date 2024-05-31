# SPDX-FileCopyrightText: 2014-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import BoolProperty, FloatVectorProperty
from bpy.types import Operator


class Destructive:
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
    is_overlap = False

    def draw(self, context):
        props = context.window_manager.booltron.destructive
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

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
        col.prop(self, "keep_objects")

        layout.separator()

        layout.label(text="Pre-processing")
        col = layout.box().column()
        col.prop(props, "merge_distance")
        col.prop(props, "dissolve_distance", text="Degenerate Dissolve", text_ctxt="Operator")

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

    mode = "SLICE"

    overlap_distance: FloatVectorProperty(
        name="Overlap",
        description="Displace secondary object to create overlap between slices",
        subtype="TRANSLATION",
        step=0.1,
        precision=3,
    )

    def draw(self, context):
        super().draw(context)

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(text="Slice")
        layout.box().prop(self, "overlap_distance")

        layout.separator()

    def execute(self, context):
        from . import destructive_func
        return destructive_func.execute_slice(self, context)
