# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2022  Mikhail Rachinskiy
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


from typing import Optional

import bpy
from bpy.types import Panel, Menu

from . import var, mod_update


# Icon utils
# ---------------------------


def scan_icons() -> None:
    import bpy.utils.previews

    pcoll = bpy.utils.previews.new()

    for child in var.ICONS_DIR.iterdir():
        if child.is_dir():
            for subchild in child.iterdir():
                if subchild.is_file() and subchild.suffix == ".png":
                    filename = child.name + subchild.stem
                    pcoll.load(filename.upper(), str(subchild), "IMAGE")

    var.preview_collections["icons"] = pcoll


def _icon(name: str, override: Optional[float] = None) -> int:
    if "icons" not in var.preview_collections:
        scan_icons()

    if override is not None:
        value = override
    else:
        value = bpy.context.preferences.themes[0].user_interface.wcol_tool.text.v

    theme = "DARK" if value < 0.5 else "LIGHT"
    return var.preview_collections["icons"][theme + name].icon_id


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
        wm_props = context.window_manager.booltron

        layout.operator("object.booltron_destructive_difference", icon_value=_icon_menu("DESTR_DIFFERENCE"))
        layout.operator("object.booltron_destructive_union", icon_value=_icon_menu("DESTR_UNION"))
        layout.operator("object.booltron_destructive_intersect", icon_value=_icon_menu("DESTR_INTERSECT"))
        layout.operator("object.booltron_destructive_slice", icon_value=_icon_menu("DESTR_SLICE"))

        layout.separator()

        layout.prop(wm_props, "mod_disable")
        col = layout.column()
        col.active = wm_props.mod_disable
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
    bl_context = "objectmode"


class VIEW3D_PT_booltron_update(mod_update.Sidebar, SidebarSetup, Panel):
    bl_label = "Update"


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
        layout.prop(context.window_manager.booltron, "mod_disable", text="")

    def draw(self, context):
        layout = self.layout
        layout.active = context.window_manager.booltron.mod_disable

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
        row = col.row(heading="Correct Position")
        row.prop(self, "use_pos_offset", text="")
        sub = row.row()
        sub.active = self.use_pos_offset
        sub.prop(self, "pos_offset", text="")
        col.prop(self, "display_secondary", text="Display As")

        box.separator(factor=2)

        box.label(text="Combined Object")
        box.box().prop(self, "display_combined", text="Display As")

        box.separator(factor=2)

        box.label(text="Pre-processing")
        box.box().prop(self, "merge_distance")

    elif active_tab == "UPDATES":
        mod_update.prefs_ui(self, box)
