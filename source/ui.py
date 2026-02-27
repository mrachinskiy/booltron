# SPDX-FileCopyrightText: 2014-2026 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

import bpy
from bpy.types import Menu, Panel

from . import var


# Previews
# ---------------------------


_previews = None


def clear_previews() -> None:
    import bpy.utils.previews
    global _previews

    if _previews is not None:
        bpy.utils.previews.remove(_previews)
        _previews = None


def _scan_icons() -> None:
    import bpy.utils.previews
    global _previews

    _previews = bpy.utils.previews.new()

    for child in var.ICONS_DIR.iterdir():
        if child.is_dir():
            for subchild in child.iterdir():
                if subchild.is_file() and subchild.suffix == ".png":
                    filename = child.name + subchild.stem
                    _previews.load(filename.upper(), str(subchild), "IMAGE")


def _icon(name: str, override: Optional[float] = None) -> int:
    if _previews is None:
        _scan_icons()

    if override is not None:
        value = override
    else:
        value = bpy.context.preferences.themes[0].user_interface.wcol_tool.text.v

    theme = "LIGHT" if value < 0.5 else "DARK"
    return _previews[theme + name].icon_id


def _icon_menu(name: str) -> int:
    return _icon(name, override=bpy.context.preferences.themes[0].user_interface.wcol_menu_item.text.v)


# Menus
# ---------------------------


def draw_booltron_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("VIEW3D_MT_booltron")


class VIEW3D_MT_booltron(Menu):
    bl_label = "Booltron"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        scene_props = context.scene.booltron

        layout.operator("object.booltron_destructive_difference", icon_value=_icon_menu("DESTR_DIFFERENCE"))
        layout.operator("object.booltron_destructive_union", icon_value=_icon_menu("DESTR_UNION"))
        layout.operator("object.booltron_destructive_intersect", icon_value=_icon_menu("DESTR_INTERSECT"))
        layout.operator("object.booltron_destructive_slice", icon_value=_icon_menu("DESTR_SLICE"))

        layout.separator()

        layout.prop(scene_props, "mod_disable")
        col = layout.column()
        col.active = scene_props.mod_disable
        col.operator("object.booltron_nondestructive_difference", icon_value=_icon_menu("NONDESTR_DIFFERENCE"))
        col.operator("object.booltron_nondestructive_union", icon_value=_icon_menu("NONDESTR_UNION"))
        col.operator("object.booltron_nondestructive_intersect", icon_value=_icon_menu("NONDESTR_INTERSECT"))
        col.operator("object.booltron_secondary_del", icon_value=_icon_menu("NONDESTR_REMOVE"))
        col.operator("object.booltron_secondary_select", icon_value=_icon("NONDESTR_SELECT"))

        col.separator()

        col.operator("object.booltron_modifier_bake")
        col.operator("object.booltron_modifier_bake_del")
        col.operator("object.booltron_instance_copy")


# Panels
# ---------------------------


class SidebarSetup:
    bl_category = "Booltron"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH", "EDIT_CURVE", "EDIT_TEXT", "SCULPT"}


class VIEW3D_PT_booltron_destructive(SidebarSetup, Panel):
    bl_label = "Destructive"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.booltron_destructive_difference", icon_value=_icon("DESTR_DIFFERENCE"))
        col.operator("object.booltron_destructive_union", icon_value=_icon("DESTR_UNION"))
        col.operator("object.booltron_destructive_intersect", icon_value=_icon("DESTR_INTERSECT"))

        layout.operator("object.booltron_destructive_slice", icon_value=_icon("DESTR_SLICE"))


class VIEW3D_PT_booltron_nondestructive(SidebarSetup, Panel):
    bl_label = "Non-destructive"

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.booltron, "mod_disable", text="")

    def draw(self, context):
        layout = self.layout
        layout.active = context.scene.booltron.mod_disable

        col = layout.column(align=True)
        col.operator("object.booltron_nondestructive_difference", icon_value=_icon("NONDESTR_DIFFERENCE"))
        col.operator("object.booltron_nondestructive_union", icon_value=_icon("NONDESTR_UNION"))
        col.operator("object.booltron_nondestructive_intersect", icon_value=_icon("NONDESTR_INTERSECT"))

        row = layout.row(align=True)
        row.operator("object.booltron_secondary_del", icon_value=_icon("NONDESTR_REMOVE"))
        row.operator("object.booltron_secondary_select", icon_value=_icon("NONDESTR_SELECT"), text="Select")

        header, panel = layout.panel("bake", default_closed=True)
        header.label(text="Bake")
        if panel:
            row = panel.row(align=True)
            row.operator("object.booltron_modifier_bake")
            row.operator("object.booltron_modifier_bake_del", icon="TRASH", text="")

            panel.operator("object.booltron_instance_copy")


# Preferences
# ---------------------------


def prefs_ui(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    main = layout.column()

    main.label(text="Primary Object")
    col = main.box().column()
    col.prop(self, "solver")
    col.prop(self, "use_self")
    col.prop(self, "use_hole_tolerant")

    split = col.split(factor=0.4)
    split.alignment = "RIGHT"
    split.label(text="Attributes")
    split.row()
    col.prop(self, "attribute_edge_intersect")

    main.separator()

    main.label(text="Secondary Object")
    col = main.box().column()
    col.prop(self, "solver_secondary")
    col.prop(self, "use_self_secondary")
    col.prop(self, "use_hole_tolerant_secondary")
    col.prop(self, "display_secondary", text="Display As")
    col.prop(self, "loc_offset", text="Randomize Location")

    main.separator()

    main.label(text="Pre-processing")
    col = main.box().column()
    col.prop(self, "merge_distance")
    col.prop(self, "dissolve_distance")

    main.separator()

    main.label(text="Modifier")
    main.box().prop(self, "use_bake")
