# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import EnumProperty
from bpy.types import Object, Operator

from .bake import (OBJECT_OT_instance_copy, OBJECT_OT_modifier_bake,
                   OBJECT_OT_modifier_bake_del)
from .utils import OBJECT_OT_secondary_del, OBJECT_OT_secondary_select


modifiers: tuple[tuple[str, str, str]] = (("__NEW__", "", ""),)


def _iter_modifiers(ob: Object, mode: str) -> None:
    global modifiers

    from ...lib.modlib import ModGN

    mods = []
    for md in ob.modifiers:
        if ModGN.is_gn_mod(md) and ModGN.check_mode(md, mode):
            mods.append((md.name, md.name + " ", ""))  # Add trailing space to deny UI translation

    mods.append(("__NEW__", "+ New Modifier", ""))

    modifiers = tuple(mods)


def _popup_warnings(warnings: list, is_manifold_solver: bool) -> None:
    icons = {
        "ERROR": "CANCEL",
        "WARNING": "ERROR",
    }

    def draw(self, context):
        for warn in warnings:
            if warn.type == "ERROR" and is_manifold_solver:
                self.layout.label(text="Non-manifold input, choose different solver", icon=icons[warn.type])
                continue
            if warn.type != "INFO":
                self.layout.label(text=warn.message, icon=icons[warn.type])

    bpy.context.window_manager.popup_menu(draw, title="Warning")


class Nondestructive:
    mode: str
    modifier_name: EnumProperty(
        name="Modifier",
        items=lambda x, y: modifiers,
        options={"SKIP_SAVE"},
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        props = context.window_manager.booltron.non_destructive

        layout.label(text="Primary Object")
        col = layout.box().column()
        col.prop(props, "solver")

        if props.solver == "EXACT":
            col.prop(props, "use_self")
            col.prop(props, "use_hole_tolerant")

        layout.separator()

        layout.label(text="Secondary Object")
        col = layout.box().column()
        col.prop(props, "solver_secondary")

        if props.solver_secondary == "EXACT":
            col.prop(props, "use_self_secondary")
            col.prop(props, "use_hole_tolerant_secondary")

        col.prop(props, "display_secondary")

        col.prop(props, "use_loc_rnd")
        if props.use_loc_rnd:
            col.prop(props, "loc_offset", text="Offset")
            col.prop(props, "seed")

        layout.separator()

        layout.label(text="Pre-processing")
        col = layout.box().column()
        col.prop(props, "merge_distance")

        layout.separator()

        layout.label(text="Modifier")
        col = layout.box().column()
        col.prop(self, "modifier_name")

        sub = col.row()
        if bpy.data.is_saved:
            sub.prop(props, "use_bake")
        else:
            sub.alert = True
            sub.prop(props, "use_bake", text="")
            sub.label(text="File not saved", icon="ERROR")

        layout.separator()

    def execute(self, context):
        from ...lib import modlib
        from . import versioning

        versioning.detect_and_migrate()

        ob1 = context.object
        obs = context.selected_objects
        if ob1.select_get():
            obs.remove(ob1)

        # Secondary objects
        # ----------------------------------

        props = context.window_manager.booltron.non_destructive
        for ob in obs:
            modlib.secondary_visibility_set(ob, props.display_secondary)

        # Modifier
        # ----------------------------------

        Mod = modlib.ModGN(self.mode, props.asdict())

        if self.modifier_name == "__NEW__":
            md = Mod.add(ob1, obs)
        else:
            md = ob1.modifiers[self.modifier_name]
            Mod.extend(md, obs)

        if bpy.app.version >= (4, 3, 0):  # VER
            context.view_layer.update()
            if md.node_warnings:
                _popup_warnings(md.node_warnings, props.solver == "MANIFOLD" or props.solver_secondary == "MANIFOLD")
                return {"FINISHED"}

        # Bake
        # ----------------------------------

        i = ob1.modifiers.find(md.name)
        for md in ob1.modifiers[i:]:
            if Mod.is_gn_mod(md) and (Mod.is_baked(md) or props.use_bake):
                Mod.bake(md)

        return {"FINISHED"}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
                ob.select_set(False)

        if len(context.selected_objects) < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        props = context.window_manager.booltron.non_destructive
        if props.first_run:
            props.first_run = False
            props.set_from_prefs()
        props.use_loc_rnd = False

        _iter_modifiers(context.object, self.mode)

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        return self.execute(context)


class OBJECT_OT_nondestructive_difference(Nondestructive, Operator):
    bl_label = "Difference"
    bl_description = "Subtract selected (secondary) objects from active (primary) object"
    bl_idname = "object.booltron_nondestructive_difference"
    bl_options = {"REGISTER", "UNDO"}

    mode = "DIFFERENCE"


class OBJECT_OT_nondestructive_union(Nondestructive, Operator):
    bl_label = "Union"
    bl_description = "Combine active (primary) and selected (secondary) objects"
    bl_idname = "object.booltron_nondestructive_union"
    bl_options = {"REGISTER", "UNDO"}

    mode = "UNION"


class OBJECT_OT_nondestructive_intersect(Nondestructive, Operator):
    bl_label = "Intersect"
    bl_description = "Keep the common part between active (primary) and selected (secondary) objects"
    bl_idname = "object.booltron_nondestructive_intersect"
    bl_options = {"REGISTER", "UNDO"}

    mode = "INTERSECT"
