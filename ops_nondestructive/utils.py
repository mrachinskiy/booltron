# SPDX-FileCopyrightText: 2014-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator


class OBJECT_OT_secondary_del(Operator):
    bl_label = "Dismiss"
    bl_description = "Dismiss selected secondary objects from boolean operation"
    bl_idname = "object.booltron_secondary_del"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from ..lib import modlib
        from . import versioning

        versioning.detect_and_migrate()

        ModGN = modlib.ModGN
        obs = frozenset(context.selected_objects)

        if not obs:
            return {"CANCELLED"}

        for ob in context.scene.objects:
            bake_invalidate = False
            for md in ob.modifiers[:]:
                if ModGN.is_gn_mod(md):
                    if ModGN.has_obs(md, obs):
                        md = ModGN.remove(md, obs)
                        bake_invalidate = True
                    if md is not None and ModGN.is_baked(md) and bake_invalidate:
                        ModGN.bake(md)

        return {"FINISHED"}


class OBJECT_OT_secondary_select(Operator):
    bl_label = "Select Secondary"
    bl_description = "Select secondary objects used by given modifier"
    bl_idname = "object.booltron_secondary_select"
    bl_options = {"REGISTER", "UNDO"}

    modifiers: tuple[str]

    modifier_name: StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    use_extend: BoolProperty(name="Extend", description="Extend selection")

    def _draw_popup_menu(op, self, context):
        layout = self.layout
        layout.operator_context = "EXEC_DEFAULT"
        for name in op.modifiers:
            layout.operator(op.bl_idname, text=name, translate=False).modifier_name = name

    def execute(self, context):
        md = context.object.modifiers[self.modifier_name]

        if not self.use_extend:
            for ob in context.selected_objects:
                ob.select_set(False)

        active = None
        for node in md.node_group.nodes:
            if node.type == "OBJECT_INFO":
                ob = node.inputs[0].default_value
                if ob is not None and ob.visible_get():
                    ob.select_set(True)
                    active = ob

        context.view_layer.objects.active = active

        return {"FINISHED"}

    def invoke(self, context, event):
        from ..lib import modlib
        ModGN = modlib.ModGN

        if context.object is None:
            return {"CANCELLED"}

        mods = []
        for md in context.object.modifiers:
            if ModGN.is_gn_mod(md):
                mods.append(md.name)

        if not mods:
            self.report({"ERROR"}, "Object does not have Booltron modifiers")
            return {"CANCELLED"}
        elif len(mods) == 1:
            self.modifier_name = mods[0]
            return self.execute(context)

        self.modifiers = tuple(mods)
        context.window_manager.popup_menu(self._draw_popup_menu, title="Modifiers")
        return {"CANCELLED"}
