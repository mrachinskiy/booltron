# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2014-2022 Mikhail Rachinskiy

from typing import Optional

import bpy
from bpy.types import Panel, Menu

from . import var, mod_update


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

    theme = "DARK" if value < 0.5 else "LIGHT"
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
        col.operator("object.booltron_nondestructive_remove", icon_value=_icon_menu("NONDESTR_REMOVE"))

# Panels
# ---------------------------


class SidebarSetup:
    bl_category = "Booltron"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


class VIEW3D_PT_booltron_update(mod_update.Sidebar, SidebarSetup, Panel):
    bl_label = "Update"


class VIEW3D_PT_booltron_destructive(SidebarSetup, Panel):
    bl_label = "Destructive"

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH", "EDIT_CURVE", "EDIT_TEXT", "SCULPT"}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.booltron_destructive_difference", icon_value=_icon("DESTR_DIFFERENCE"))
        col.operator("object.booltron_destructive_union", icon_value=_icon("DESTR_UNION"))
        col.operator("object.booltron_destructive_intersect", icon_value=_icon("DESTR_INTERSECT"))

        layout.operator("object.booltron_destructive_slice", icon_value=_icon("DESTR_SLICE"))


class VIEW3D_PT_booltron_nondestructive(SidebarSetup, Panel):
    bl_label = "Non-destructive"

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH", "EDIT_CURVE", "EDIT_TEXT", "SCULPT"}

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

        layout.operator("object.booltron_nondestructive_remove", icon_value=_icon("NONDESTR_REMOVE"))


# Preferences
# ---------------------------


def prefs_ui(self, context):
    props_wm = context.window_manager.booltron
    active_tab = props_wm.prefs_active_tab

    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    split = layout.split(factor=0.25)
    col = split.column()
    col.use_property_split = False
    col.scale_y = 1.3
    col.prop(props_wm, "prefs_active_tab", expand=True)

    box = split.box()

    if active_tab == "TOOLS":
        box = box.column()

        box.label(text="Modifier")
        col = box.box().column()
        col.prop(self, "solver")

        if self.solver == "FAST":
            col.prop(self, "threshold")
        else:
            col.prop(self, "use_self")
            col.prop(self, "use_hole_tolerant")

        box.separator(factor=2)

        box.label(text="Secondary Object")
        col = box.box().column()
        row = col.row(heading="Randomize Location")
        row.prop(self, "use_loc_rnd", text="")
        sub = row.row()
        sub.active = self.use_loc_rnd
        sub.prop(self, "loc_offset", text="")
        col.prop(self, "display_secondary", text="Display As")

        box.separator(factor=2)

        box.label(text="Combined Object")
        box.box().prop(self, "display_combined", text="Display As")

        box.separator(factor=2)

        box.label(text="Pre-processing")
        col = box.box().column()
        col.prop(self, "merge_distance")
        col.prop(self, "dissolve_distance")

    elif active_tab == "UPDATES":
        mod_update.prefs_ui(self, box)
