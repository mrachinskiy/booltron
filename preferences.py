# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
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


from bpy.types import AddonPreferences
from bpy.props import EnumProperty, BoolProperty, FloatProperty

from . import versioning, addon_updater_ops


# Add-on preferences
# ------------------------------------------


def property_split(data, layout, label, prop, ratio=0.0):
    split = layout.split(align=True, percentage=ratio)
    split.alignment = "RIGHT"
    split.label(label)
    split.prop(data, prop, text="")


class BooltronPreferences(AddonPreferences):
    bl_idname = __package__

    active_section = EnumProperty(
        items=(
            ("DESTRUCTIVE", "Destructive", ""),
            ("NONDESTRUCTIVE", "Non-destructive", ""),
            ("UPDATER", "Update", ""),
        ),
        options={"SKIP_SAVE"},
    )
    update_auto_check = BoolProperty(name="Automatically check for updates", description="Automatically check for updates with specified interval", default=True)
    update_interval = EnumProperty(
        name="Interval",
        description="Interval",
        items=(
            ("1", "Once a day", ""),
            ("7", "Once a week", ""),
            ("30", "Once a month", ""),
        ),
        default="7",
    )
    cleanup = BoolProperty(name="Mesh Cleanup", description="Perform mesh cleanup in between boolean operations, enabling this option will greatly affect performance of a boolean operation")
    triangulate = BoolProperty(name="Triangulate", description="Triangulate geometry before boolean operation, in some cases may improve result of a boolean operation")
    destr_pos_correct = BoolProperty(name="Correct Position", description="Shift objects position for a very small amount to avoid coplanar geometry errors during boolean operation (does not affect active object)")
    destr_pos_offset = FloatProperty(name="Position Offset", description="Position offset is randomly generated for each object in range [-x, +x] input value", default=0.005, min=0.0, step=0.1, precision=3, unit="LENGTH")
    nondestr_pos_correct = destr_pos_correct
    nondestr_pos_offset = destr_pos_offset
    display_secondary = EnumProperty(
        name="Display As",
        description="Maximum draw type to display object with in viewport",
        items=(
            ("BOUNDS", "Bounds", ""),
            ("WIRE", "Wire", ""),
            ("SOLID", "Solid", ""),
            ("TEXTURED", "Textured", ""),
        ),
        default="WIRE",
    )
    display_combined = EnumProperty(
        name="Display As",
        description="Maximum draw type to display object with in viewport",
        items=(
            ("BOUNDS", "Bounds", ""),
            ("WIRE", "Wire", ""),
            ("SOLID", "Solid", ""),
            ("TEXTURED", "Textured", ""),
        ),
        default="BOUNDS",
    )

    if versioning.SOLVER_OPTION:

        destr_solver = EnumProperty(
            name="Boolean Solver",
            description="Specify solver for boolean operations",
            items=(
                ("BMESH", "BMesh", "BMesh solver is faster, but less stable and cannot handle coplanar geometry"),
                ("CARVE", "Carve", "Carve solver is slower, but more stable and can handle simple cases of coplanar geometry"),
            ),
        )
        nondestr_solver = destr_solver

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.row().prop(self, "active_section", expand=True)
        col.separator()

        if self.active_section == "DESTRUCTIVE":
            col = layout.column()
            if versioning.SOLVER_OPTION:
                property_split(self, col, "Boolean Solver", "destr_solver", ratio=1 / 3)
            property_split(self, col, "Mesh Cleanup", "cleanup", ratio=1 / 3)
            property_split(self, col, "Triangulate", "triangulate", ratio=1 / 3)
            property_split(self, col, "Correct Position", "destr_pos_correct", ratio=1 / 3)
            sub = col.column()
            sub.active = self.destr_pos_correct
            property_split(self, sub, "Position Offset", "destr_pos_offset", ratio=1 / 3)

        if self.active_section == "NONDESTRUCTIVE":
            col = layout.column()
            if versioning.SOLVER_OPTION:
                property_split(self, col, "Boolean Solver", "nondestr_solver", ratio=1 / 3)
            property_split(self, col, "Correct Position", "nondestr_pos_correct", ratio=1 / 3)
            sub = col.column()
            sub.active = self.nondestr_pos_correct
            property_split(self, sub, "Position Offset", "nondestr_pos_offset", ratio=1 / 3)
            layout.label("Viewport Display")
            col = layout.column()
            property_split(self, col, "Secondary Object", "display_secondary", ratio=1 / 3)
            property_split(self, col, "Combined Object", "display_combined", ratio=1 / 3)

        elif self.active_section == "UPDATER":
            addon_updater_ops.update_settings_ui(self, context)


# Window manager properties
# ------------------------------------------


def update_mod_disable(self, context):
    show = self.booltron_mod_disable

    for ob in context.scene.objects:
        if ob.type == "MESH":

            for md in ob.modifiers:
                if md.type == "BOOLEAN":

                    md.show_viewport = show


mod_disable = BoolProperty(description="Disable boolean modifiers on all objects", default=True, update=update_mod_disable)
