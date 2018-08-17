# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2014-2018  Mikhail Rachinskiy
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

from . import versioning, addon_updater_ops


class Setup:
    bl_category = "Booltron"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None


class VIEW3D_PT_booltron_update(Panel, Setup):
    bl_label = "Update"

    @classmethod
    def poll(cls, context):
        return addon_updater_ops.updater.update_ready

    def draw(self, context):
        addon_updater_ops.update_notice_box_ui(self, context)


class VIEW3D_PT_booltron_options(Panel, Setup):
    bl_label = "Options"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prefs = context.user_preferences.addons[__package__].preferences

        if versioning.SOLVER_OPTION:
            layout.prop(prefs, "solver", text="")

        layout.prop(prefs, "method", text="")

        col = layout.column()
        col.prop(prefs, "triangulate")
        col.prop(prefs, "pos_correct")

        row = layout.row()
        row.active = prefs.pos_correct
        row.prop(prefs, "pos_offset")


class VIEW3D_PT_booltron_tools(Panel, Setup):
    bl_label = "Tools"

    def draw(self, context):
        addon_updater_ops.check_for_update_background()

        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.booltron_union", text="Union")
        col.operator("object.booltron_difference", text="Difference")
        col.operator("object.booltron_intersect", text="Intersect")

        col = layout.column(align=True)
        col.operator("object.booltron_slice", text="Slice")
        col.operator("object.booltron_subtract", text="Subtract")
