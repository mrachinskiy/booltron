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


from bpy.types import AddonPreferences
from bpy.props import EnumProperty, BoolProperty, FloatProperty

from . import versioning, addon_updater_ops


class OperatorProps:
    """Unified add-on and operator settings"""

    solver = EnumProperty(
        name="Boolean Solver",
        description="Specify solver for boolean operations",
        items=(
            ("BMESH", "BMesh", "BMesh solver is faster, but less stable and cannot handle coplanar geometry"),
            ("CARVE", "Carve", "Carve solver is slower, but more stable and can handle simple cases of coplanar geometry"),
        ),
        default="BMESH",
    )
    method = EnumProperty(
        name="Boolean Method",
        description="Specify boolean method for Union, Difference and Intersect tools (Intersect tool does not support optimized method and will use batch method instead)",
        items=(
            ("OPTIMIZED",     "Optimized",            "A single boolean operation with all objects at once, fastest, but in certain cases gives unpredictable result"),
            ("BATCH",         "Batch",                "Boolean operation for each selected object one by one, much slower, but overall gives more predictable result than optimized method"),
            ("BATCH_CLEANUP", "Batch + Mesh Cleanup", "Perform mesh cleanup operation in between boolean operations, slowest, but gives better result in cases where simple batch method fails"),
        ),
        default="OPTIMIZED",
    )
    triangulate = BoolProperty(name="Triangulate", description="Triangulate geometry before boolean operation (in certain cases may improve result of a boolean operation)")
    pos_correct = BoolProperty(name="Correct Position", description="Shift objects position for a very small amount to avoid coplanar geometry errors during boolean operation (does not affect active object)")
    pos_offset = FloatProperty(name="Position Offset", description="Position offset is randomly generated for each object in range [-x, +x] input value", default=0.005, min=0.0, step=0.1, precision=3)


class BooltronPreferences(AddonPreferences, OperatorProps):
    bl_idname = __package__

    active_section = EnumProperty(
        items=(
            ("TOOLS", "Tools", ""),
            ("UPDATER", "Updater", ""),
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

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.row().prop(self, "active_section", expand=True)

        col.separator()

        if self.active_section == "TOOLS":
            split = layout.split(percentage=1 / 3)
            split.enabled = versioning.SOLVER_OPTION
            split.alignment = "RIGHT"
            split.label("Boolean Solver")

            if versioning.SOLVER_OPTION:
                split.prop(self, "solver", text="")
            else:
                split.alignment = "LEFT"
                split.label("(!) Not available on this version of Blender")

            split = layout.split(percentage=1 / 3)
            split.alignment = "RIGHT"
            split.label("Boolean Method")
            split.prop(self, "method", text="")

            split = layout.split(percentage=1 / 3)
            split.alignment = "RIGHT"
            split.label("Triangulate")
            split.prop(self, "triangulate", text="")

            split = layout.split(percentage=1 / 3)
            split.alignment = "RIGHT"
            split.label("Correct Position")
            split.prop(self, "pos_correct", text="")

            split = layout.split(percentage=1 / 3)
            split.active = self.pos_correct
            split.alignment = "RIGHT"
            split.label("Position Offset")
            split.prop(self, "pos_offset", text="")

        elif self.active_section == "UPDATER":
            addon_updater_ops.update_settings_ui(self, context)
