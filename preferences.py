# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2021  Mikhail Rachinskiy
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


from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import EnumProperty, BoolProperty, FloatProperty

from . import ui, mod_update


# Operator properties
# ------------------------------------------


class ToolProps:

    # Modifier
    # ------------------------

    solver: EnumProperty(
        name="Solver",
        description="Method for calculating booleans",
        items=(
            ("FAST", "Fast", "Simple solver for the best performance, without support for overlapping geometry"),
            ("EXACT", "Exact", "Advanced solver for the best result"),
        ),
        default="FAST",
    )
    use_self: BoolProperty(
        name="Self",
        description="Allow self-intersection in operands",
    )
    threshold: FloatProperty(
        name="Overlap Threshold",
        description="Threshold for checking overlapping geometry",
        default=0.000001,
        min=0.0,
        step=0.0001,
        precision=6,
    )

    # Object
    # ------------------------

    use_pos_offset: BoolProperty(
        name="Correct Position",
        description=(
            "Shift objects position for a very small amount to avoid coplanar "
            "geometry errors during boolean operation (does not affect active object)"
        ),
    )
    pos_offset: FloatProperty(
        name="Position Offset",
        description="Position offset is randomly generated for each object in range [-x, +x] input value",
        default=0.005,
        min=0.0,
        step=0.01,
        precision=3,
        unit="LENGTH",
    )

    # Mesh
    # ------------------------

    merge_distance: FloatProperty(
        name="Merge Distance",
        description="Minimum distance between elements to merge",
        default=0.0002,
        min=0.00001,
        step=0.01,
        precision=5,
        unit="LENGTH",
    )
    cleanup: BoolProperty(
        name="Mesh Cleanup",
        description=(
            "Perform mesh cleanup in between boolean operations, "
            "enabling this option will greatly affect performance"
        ),
    )
    triangulate: BoolProperty(
        name="Triangulate",
        description=(
            "Triangulate geometry before boolean operation, "
            "in some cases may improve result of a boolean operation"
        ),
    )

    # Viewport Display
    # ------------------------

    display_secondary: EnumProperty(
        name="Secondary Object",
        description="How to display object in viewport",
        items=(
            ("BOUNDS", "Bounds", ""),
            ("WIRE", "Wire", ""),
            ("SOLID", "Solid", ""),
            ("TEXTURED", "Textured", ""),
        ),
        default="WIRE",
    )
    display_combined: EnumProperty(
        name="Combined Object",
        description="How to display object in viewport",
        items=(
            ("BOUNDS", "Bounds", ""),
            ("WIRE", "Wire", ""),
            ("SOLID", "Solid", ""),
            ("TEXTURED", "Textured", ""),
        ),
        default="BOUNDS",
    )


# Add-on preferences
# ------------------------------------------


class Preferences(ToolProps, mod_update.Preferences, AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        ui.prefs_ui(self, context)


# Window manager properties
# ------------------------------------------


def upd_mod_disable(self, context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            for md in ob.modifiers:
                if md.type == "BOOLEAN":
                    md.show_viewport = self.mod_disable


class WmProperties(PropertyGroup):
    prefs_active_tab: EnumProperty(
        items=(
            ("TOOLS", "Tools", ""),
            ("UPDATES", "Updates", ""),
        ),
    )
    mod_disable: BoolProperty(
        name="Non-destructive",
        description="Disable boolean modifiers on all objects",
        default=True,
        update=upd_mod_disable,
    )
