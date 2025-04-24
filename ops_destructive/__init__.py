# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import BoolProperty, FloatVectorProperty
from bpy.types import Operator

from .. import preferences, var


def _cursor_state(func):
    def wrapper(self, context):
        context.window.cursor_set("WAIT")
        result = func(self, context)
        context.window.cursor_set("DEFAULT")
        return result
    return wrapper


class Destructive:
    mode: str
    is_overlap = False
    keep_objects: BoolProperty(
        name="Keep Objects",
        description=(
            "Do not remove selected objects after boolean operation "
            "(Shortcut: hold Alt when using the tool)"
        ),
        options={"SKIP_SAVE"},
    )

    def draw(self, context):
        props = context.window_manager.booltron.destructive
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(text="Primary Object")
        col = layout.box().column()
        col.prop(props, "solver")

        if props.solver == "FAST":
            col.prop(props, "threshold")
        elif props.solver == "EXACT":
            col.prop(props, "use_self")
            col.prop(props, "use_hole_tolerant")

        layout.separator()

        layout.label(text="Secondary Object")
        col = layout.box().column()

        if self.mode != "SLICE":
            col.prop(props, "solver_secondary")

            if props.solver_secondary == "FAST":
                col.prop(props, "threshold_secondary")
            elif props.solver_secondary == "EXACT":
                col.prop(props, "use_self_secondary")
                col.prop(props, "use_hole_tolerant_secondary")

        col.prop(self, "keep_objects")

        row = col.row()
        row.use_property_split = False
        row.prop(props, "use_loc_rnd")
        sub = col.column()
        sub.enabled = props.use_loc_rnd
        sub.prop(props, "loc_offset", text="Offset")
        sub.prop(props, "seed")

        layout.separator()

        layout.label(text="Pre-processing")
        col = layout.box().column()
        col.prop(props, "merge_distance")
        col.prop(props, "dissolve_distance", text="Degenerate Dissolve", text_ctxt="Operator")

        layout.separator()

    @_cursor_state
    def execute(self, context):
        from ..lib import meshlib, modlib, objectlib

        props = context.window_manager.booltron.destructive
        Mesh = meshlib.Utils(self.report)
        boolean = modlib.ModBoolean().add

        ob1, obs = objectlib.prepare_objects(self.keep_objects, props.seed)

        Mesh.prepare(ob1)
        for ob in obs:
            Mesh.prepare(ob, select=True)

        if props.solver == "MANIFOLD" or props.solver_secondary == "MANIFOLD":
            if meshlib.is_nonmanifold(obs + [ob1]):
                self.report({"ERROR"}, "Non-manifold input, choose different solver")
                if self.keep_objects:
                    for ob in obs:
                        bpy.data.meshes.remove(ob.data)
                return {"FINISHED"}

        ob2 = obs.pop()
        if obs:
            if self.is_overlap:
                for ob3 in obs:
                    boolean(ob2, ob3, "SECONDARY")
            else:
                obs.append(ob2)
                with context.temp_override(active_object=ob2, selected_editable_objects=obs):
                    bpy.ops.object.join()

        boolean(ob1, ob2, self.mode)
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
            from ..lib import meshlib
            obs.remove(context.object)
            self.is_overlap = meshlib.detect_overlap(obs)

        props = context.window_manager.booltron.destructive

        if props.first_run:
            props.first_run = False
            prefs = context.preferences.addons[var.ADDON_ID].preferences
            for prop in preferences.ToolProps.__annotations__:
                setattr(props, prop, getattr(prefs, prop))

        self.keep_objects = event.alt

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        return self.execute(context)


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

    @_cursor_state
    def execute(self, context):
        from ..lib import meshlib, modlib, objectlib

        props = context.window_manager.booltron.destructive
        Mesh = meshlib.Utils(self.report)
        boolean = modlib.ModBoolean().add

        ob1, obs = objectlib.prepare_objects(self.keep_objects, props.seed)

        Mesh.prepare(ob1)
        for ob in obs:
            Mesh.prepare(ob, select=True)

        if props.solver == "MANIFOLD" or props.solver_secondary == "MANIFOLD":
            if meshlib.is_nonmanifold(obs + [ob1]):
                self.report({"ERROR"}, "Non-manifold input, choose different solver")
                if self.keep_objects:
                    for ob in obs:
                        bpy.data.meshes.remove(ob.data)
                return {"FINISHED"}

        for ob2 in obs:

            # Create copy of main object
            # ---------------------------------

            ob1_copy = ob1.copy()
            ob1_copy.data = ob1.data.copy()
            objectlib.ob_link(ob1_copy, ob1.users_collection)
            ob1_copy.select_set(True)

            # Main object difference
            # ---------------------------------

            ob2.matrix_basis.translation += self.overlap_distance / 2

            boolean(ob1, ob2, "DIFFERENCE", remove_ob2=False)

            if Mesh.check(ob1):
                return {"FINISHED"}

            # Main object copy intersect
            # ---------------------------------

            ob2.matrix_basis.translation -= self.overlap_distance

            boolean(ob1_copy, ob2, "INTERSECT")

            if Mesh.check(ob1_copy):
                return {"FINISHED"}

        ob1.select_set(False)
        context.view_layer.objects.active = ob1_copy

        return {"FINISHED"}
