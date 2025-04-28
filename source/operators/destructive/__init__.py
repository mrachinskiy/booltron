# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import BoolProperty, FloatVectorProperty
from bpy.types import Operator


def _cursor_state(func):
    def wrapper(self, context):
        context.window.cursor_set("WAIT")
        result = func(self, context)
        context.window.cursor_set("DEFAULT")
        return result
    return wrapper


class Destructive:
    mode: str
    is_overlap = True
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

        if props.solver == "EXACT":
            col.prop(props, "use_self")
            col.prop(props, "use_hole_tolerant")

        layout.separator()

        layout.label(text="Secondary Object")
        col = layout.box().column()

        if self.mode != "SLICE":
            col.prop(props, "solver_secondary")

            if props.solver_secondary == "EXACT":
                col.prop(props, "use_self_secondary")
                col.prop(props, "use_hole_tolerant_secondary")

        col.prop(self, "keep_objects")

        col.prop(props, "use_loc_rnd")
        if props.use_loc_rnd:
            col.prop(props, "loc_offset", text="Offset")
            col.prop(props, "seed")

        layout.separator()

        layout.label(text="Pre-processing")
        col = layout.box().column()
        col.prop(props, "merge_distance")
        col.prop(props, "dissolve_distance", text="Degenerate Dissolve", text_ctxt="Operator")

        layout.separator()

    @_cursor_state
    def execute(self, context):
        from ...lib import meshlib, modlib, objectlib

        props = context.window_manager.booltron.destructive

        ob1, obs = objectlib.prepare_objects(self.keep_objects)
        meshlib.prepare((ob1,), props.merge_distance, props.dissolve_distance)
        meshlib.prepare(obs, props.merge_distance, props.dissolve_distance, select=True)

        if props.solver == "MANIFOLD" or props.solver_secondary == "MANIFOLD":
            if meshlib.is_nonmanifold_eval(obs + [ob1]):
                self.report({"ERROR"}, "Non-manifold input, choose different solver")
                if self.keep_objects:
                    for ob in obs:
                        bpy.data.meshes.remove(ob.data)
                return {"FINISHED"}

        Mod = modlib.ModGN(self.mode, props.asdict())
        if self.is_overlap or len(obs) == 1:
            Mod.add_and_apply(ob1, obs)
        else:
            ob2 = obs[0]
            with context.temp_override(active_object=ob2, selected_editable_objects=obs):
                bpy.ops.object.join()
            Mod.add_and_apply(ob1, (ob2,))

        if meshlib.is_nonmanifold(ob1):
            self.report({"ERROR"}, "Boolean operation result is non-manifold")

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
            from ...lib import meshlib
            obs.remove(context.object)
            self.is_overlap = meshlib.detect_overlap(obs)

        props = context.window_manager.booltron.destructive
        if props.first_run:
            props.first_run = False
            props.set_from_prefs()
        props.use_loc_rnd = False

        self.keep_objects = event.alt

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        return self.execute(context)


class OBJECT_OT_destructive_difference(Destructive, Operator):
    bl_label = "Difference"
    bl_description = "Subtract selected objects from active object"
    bl_idname = "object.booltron_destructive_difference"
    bl_options = {"REGISTER", "UNDO"}

    mode = "DIFFERENCE"


class OBJECT_OT_destructive_union(Destructive, Operator):
    bl_label = "Union"
    bl_description = "Combine selected objects"
    bl_idname = "object.booltron_destructive_union"
    bl_options = {"REGISTER", "UNDO"}

    mode = "UNION"


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
        from ...lib import meshlib, modlib, objectlib

        props = context.window_manager.booltron.destructive

        ob1, obs = objectlib.prepare_objects(self.keep_objects)
        meshlib.prepare((ob1,), props.merge_distance, props.dissolve_distance)
        meshlib.prepare(obs, props.merge_distance, props.dissolve_distance, select=True)

        if props.solver == "MANIFOLD" or props.solver_secondary == "MANIFOLD":
            if meshlib.is_nonmanifold_eval(obs + [ob1]):
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

            modlib.ModGN("DIFFERENCE", props.asdict()).add_and_apply(ob1, (ob2,), remove_obs=False)

            if meshlib.is_nonmanifold(ob1):
                self.report({"ERROR"}, "Boolean operation result is non-manifold")
                return {"FINISHED"}

            # Main object copy intersect
            # ---------------------------------

            ob2.matrix_basis.translation -= self.overlap_distance

            modlib.ModGN("INTERSECT", props.asdict()).add_and_apply(ob1_copy, (ob2,))

            if meshlib.is_nonmanifold(ob1_copy):
                self.report({"ERROR"}, "Boolean operation result is non-manifold")
                return {"FINISHED"}

        ob1.select_set(False)
        context.view_layer.objects.active = ob1_copy

        return {"FINISHED"}
