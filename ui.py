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
from bpy.types import Panel

from . import var, mod_update


class Setup:
    bl_category = "Booltron"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def __init__(self):
        prefs = bpy.context.preferences.addons[__package__].preferences
        self.pcoll = var.preview_collections["icons"]
        self.theme = prefs.theme_icon

    def icon_get(self, name):
        return self.pcoll[self.theme + name].icon_id


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
        col.operator("object.booltron_destructive_difference", text="Difference", icon_value=self.icon_get("DESTR_DIFFERENCE"))
        col.operator("object.booltron_destructive_union", text="Union", icon_value=self.icon_get("DESTR_UNION"))
        col.operator("object.booltron_destructive_intersect", text="Intersect", icon_value=self.icon_get("DESTR_INTERSECT"))

        layout.operator("object.booltron_destructive_slice", text="Slice", icon_value=self.icon_get("DESTR_SLICE"))


class VIEW3D_PT_booltron_nondestructive(Setup, Panel):
    bl_label = "Non-destructive"

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.window_manager.booltron, "mod_disable", text="")

    def draw(self, context):
        layout = self.layout
        layout.active = context.window_manager.booltron.mod_disable

        col = layout.column(align=True)
        col.operator("object.booltron_nondestructive_difference", text="Difference", icon_value=self.icon_get("NONDESTR_DIFFERENCE"))
        col.operator("object.booltron_nondestructive_union", text="Union", icon_value=self.icon_get("NONDESTR_UNION"))
        col.operator("object.booltron_nondestructive_intersect", text="Intersect", icon_value=self.icon_get("NONDESTR_INTERSECT"))

        layout.operator("object.booltron_nondestructive_remove", text="Dismiss", icon_value=self.icon_get("NONDESTR_REMOVE"))
