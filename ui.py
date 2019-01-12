# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2019  Mikhail Rachinskiy
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


from bpy.types import Panel

from . import var, addon_updater_ops


class Setup:
    bl_category = "Booltron"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"


class VIEW3D_PT_booltron_update(Panel, Setup):
    bl_label = "Update"

    @classmethod
    def poll(cls, context):
        return addon_updater_ops.updater.update_ready

    def draw(self, context):
        addon_updater_ops.update_notice_box_ui(self, context)


class VIEW3D_PT_booltron_destructive(Panel, Setup):
    bl_label = "Destructive"

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__package__].preferences
        theme = prefs.theme_icon
        icon_pfx = theme + "DESTR_"
        pcoll = var.preview_collections["icons"]

        col = layout.column(align=True)
        col.operator("object.booltron_destructive_difference", text="Difference", icon_value=pcoll[icon_pfx + "DIFFERENCE"].icon_id)
        col.operator("object.booltron_destructive_union", text="Union", icon_value=pcoll[icon_pfx + "UNION"].icon_id)
        col.operator("object.booltron_destructive_intersect", text="Intersect", icon_value=pcoll[icon_pfx + "INTERSECT"].icon_id)

        layout.operator("object.booltron_destructive_slice", text="Slice", icon_value=pcoll[icon_pfx + "SLICE"].icon_id)


class VIEW3D_PT_booltron_nondestructive(Panel, Setup):
    bl_label = "Non-destructive"

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.window_manager, "booltron_mod_disable", text="")

    def draw(self, context):
        layout = self.layout
        layout.active = context.window_manager.booltron_mod_disable
        prefs = context.preferences.addons[__package__].preferences
        theme = prefs.theme_icon
        icon_pfx = theme + "NONDESTR_"
        pcoll = var.preview_collections["icons"]

        col = layout.column(align=True)
        col.operator("object.booltron_nondestructive_difference", text="Difference", icon_value=pcoll[icon_pfx + "DIFFERENCE"].icon_id)
        col.operator("object.booltron_nondestructive_union", text="Union", icon_value=pcoll[icon_pfx + "UNION"].icon_id)
        col.operator("object.booltron_nondestructive_intersect", text="Intersect", icon_value=pcoll[icon_pfx + "INTERSECT"].icon_id)

        layout.operator("object.booltron_nondestructive_remove", text="Dismiss", icon_value=pcoll[icon_pfx + "REMOVE"].icon_id)
