# SPDX-FileCopyrightText: 2014-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import EnumProperty
from bpy.types import Operator, Object

from .. import preferences, var
from .cache import (
    OBJECT_OT_nondestructive_cache,
    OBJECT_OT_nondestructive_cache_del,
    OBJECT_OT_nondestructive_instance_copy,
)


def _iter_modifiers(ob: Object, mode: str) -> None:
    from ..lib import modlib
    ModGN = modlib.ModGN

    mods = []
    for md in ob.modifiers:
        if ModGN.is_gn_mod(md) and ModGN.check_mode(md, mode):
            mods.append((md.name, md.name + " ", ""))  # Add trailing space to deny UI translation

    mods.append(("__NEW__", "+ New Modifier", ""))

    Nondestructive.modifiers = tuple(mods)


class Nondestructive:
    mode: str
    modifiers: tuple[tuple[str, str, str]]
    modifier_name: EnumProperty(
        name="Modifier",
        items=lambda x, y: Nondestructive.modifiers,
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

        row = col.row(heading="Randomize Location")
        row.prop(props, "use_loc_rnd", text="")
        sub = row.row()
        sub.enabled = props.use_loc_rnd
        sub.prop(props, "loc_offset", text="")

        col.prop(props, "merge_distance")
        col.prop(props, "display_secondary")

        layout.separator()

        layout.label(text="Modifier")
        col = layout.box().column()
        col.prop(self, "modifier_name")

        sub = col.row()
        if bpy.data.is_saved:
            sub.prop(props, "use_cache")
        else:
            sub.alert = True
            sub.prop(props, "use_cache", text="")
            sub.label(text="File not saved", icon="ERROR")

        layout.separator()

    def execute(self, context):
        from ..lib import modlib

        ob1 = context.object
        obs = context.selected_objects
        if ob1.select_get():
            obs.remove(ob1)

        # Secondary objects
        # ----------------------------------

        props = context.window_manager.booltron.non_destructive
        Mod = modlib.ModGN(self.mode)

        for ob in obs:
            ob.display_type = props.display_secondary

        if self.modifier_name == "__NEW__":
            md = Mod.add(ob1, obs)
        else:
            Mod.extend(ob1.modifiers[self.modifier_name], obs)

        if props.use_cache:
            Mod.cache(md)

        return {"FINISHED"}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
                ob.select_set(False)

        if len(context.selected_objects) < 2 or context.object.type != "MESH":
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        props = context.window_manager.booltron.non_destructive

        if props.first_run:
            props.first_run = False
            prefs = context.preferences.addons[var.ADDON_ID].preferences
            for prop in preferences.ToolProps.__annotations__:
                setattr(props, prop, getattr(prefs, prop))

        _iter_modifiers(context.object, self.mode)

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        return self.execute(context)


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
        from ..lib import modlib

        ModGN = modlib.ModGN

        obs = {ob for ob in context.selected_objects if "booltron_combined" not in ob}
        gn_mods = []
        is_combined_empty = False

        if not obs:
            return {"CANCELLED"}

        for ob in context.scene.objects:
            if "booltron_combined" in ob:

                for md in ob.modifiers:
                    if md.type == "BOOLEAN" and (not md.object or md.object in obs):
                        ob.modifiers.remove(md)

                for md in ob.modifiers:
                    if md.type == "BOOLEAN":
                        break
                else:
                    is_combined_empty = True
                    bpy.data.meshes.remove(ob.data)

            else:

                for md in ob.modifiers:
                    if ModGN.is_gn_mod(md) and ModGN.has_obs(md, obs):
                        gn_mods.append(md)

        for md in gn_mods:
            ModGN.remove(md, obs)

        if is_combined_empty:
            for ob in context.scene.objects:
                if ob.type != "MESH":
                    continue
                for md in ob.modifiers:
                    if md.type == "BOOLEAN" and not md.object:
                        ob.modifiers.remove(md)

        for ob in obs:
            ob.display_type = "TEXTURED"

        return {"FINISHED"}
