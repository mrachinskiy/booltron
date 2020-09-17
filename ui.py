# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2020  Mikhail Rachinskiy
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


import bpy
from bpy.types import Panel, Menu

from . import var, mod_update


# Utils
# ---------------------------


class Setup:
    bl_category = "Booltron"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"


def _get_icon(name, override=None):
    if override is not None:
        value = override
    else:
        value = bpy.context.preferences.themes[0].user_interface.wcol_tool.text.v

    theme = "DARK" if value < 0.5 else "LIGHT"
    return var.preview_collections["icons"][theme + name].icon_id


def _icon(name, override=None):
    global _icon
    _icon = _get_icon

    if "icons" not in var.preview_collections:
        import os
        import bpy.utils.previews

        pcoll = bpy.utils.previews.new()

        for entry in os.scandir(var.ICONS_DIR):
            if entry.is_dir():
                for subentry in os.scandir(entry.path):
                    if subentry.is_file() and subentry.name.endswith(".png"):
                        filename = entry.name + os.path.splitext(subentry.name)[0]
                        pcoll.load(filename.upper(), subentry.path, "IMAGE")

        var.preview_collections["icons"] = pcoll

    return _get_icon(name, override)


def _icon_menu(name):
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


class VIEW3D_PT_booltron_update(Setup, Panel):
    bl_label = "Update"

    @classmethod
    def poll(cls, context):
        return mod_update.state.update_available

    def draw(self, context):
        mod_update.sidebar_ui(self, context)


class VIEW3D_PT_booltron_destructive(Setup, Panel):
    bl_label = "Destructive"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.booltron_destructive_difference", icon_value=_icon("DESTR_DIFFERENCE"))
        col.operator("object.booltron_destructive_union", icon_value=_icon("DESTR_UNION"))
        col.operator("object.booltron_destructive_intersect", icon_value=_icon("DESTR_INTERSECT"))

        layout.operator("object.booltron_destructive_slice", icon_value=_icon("DESTR_SLICE"))


class VIEW3D_PT_booltron_nondestructive(Setup, Panel):
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

    if active_tab == "DESTRUCTIVE":
        col = box.column()
        col.prop(self, "destr_double_threshold")

        row = col.row(heading="Correct Position")
        row.prop(self, "destr_use_pos_offset", text="")
        sub = row.row()
        sub.active = self.destr_use_pos_offset
        sub.prop(self, "destr_pos_offset", text="")

        col.prop(self, "merge_distance")
        col.prop(self, "cleanup")
        col.prop(self, "triangulate")

    elif active_tab == "NONDESTRUCTIVE":
        col = box.column()
        col.prop(self, "nondestr_double_threshold")

        row = col.row(heading="Correct Position")
        row.prop(self, "nondestr_use_pos_offset", text="")
        sub = row.row()
        sub.active = self.nondestr_use_pos_offset
        sub.prop(self, "nondestr_pos_offset", text="")

        box.label(text="Viewport Display")
        col = box.column()
        col.prop(self, "display_secondary")
        col.prop(self, "display_combined")

    elif active_tab == "UPDATES":
        mod_update.prefs_ui(self, box)
