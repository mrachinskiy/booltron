# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2014-2022 Mikhail Rachinskiy

import bpy
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
        name="Self Intersection",
        description="Allow self-intersection in operands",
    )
    use_hole_tolerant: BoolProperty(
        name="Hole Tolerant",
        description="Better results when there are holes (slower)",
    )
    threshold: FloatProperty(
        name="Overlap Threshold",
        description="Threshold for checking overlapping geometry",
        default=0.000001,
        min=0.0,
        step=0.0001,
        precision=6,
    )

    # Secondary
    # ------------------------

    use_pos_offset: BoolProperty(
        name="Correct Position",
        description=(
            "Shift objects position for a very small amount to avoid coplanar "
            "geometry errors during boolean operation"
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
    display_secondary: EnumProperty(
        name="Display As",
        description="How to display object in viewport",
        items=(
            ("BOUNDS", "Bounds", ""),
            ("WIRE", "Wire", ""),
            ("SOLID", "Solid", ""),
            ("TEXTURED", "Textured", ""),
        ),
        default="WIRE",
    )

    # Combined
    # ------------------------

    display_combined: EnumProperty(
        name="Display As",
        description="How to display object in viewport",
        items=(
            ("BOUNDS", "Bounds", ""),
            ("WIRE", "Wire", ""),
            ("SOLID", "Solid", ""),
            ("TEXTURED", "Textured", ""),
        ),
        default="BOUNDS",
    )

    # Pre-processing
    # ------------------------

    merge_distance: FloatProperty(
        name="Merge Distance",
        description="Minimum distance between elements to merge",
        default=0.0003,
        soft_min=0.00001,
        min=0.000001,
        step=0.001,
        precision=5,
        unit="LENGTH",
    )
    dissolve_distance: FloatProperty(
        name="Degenerate Dissolve",
        description="Dissolve zero area faces and zero length edges",
        default=0.0001,
        soft_min=0.00001,
        min=0.000001,
        step=0.001,
        precision=5,
        unit="LENGTH",
    )


# Add-on preferences
# ------------------------------------------


class Preferences(ToolProps, mod_update.Preferences, AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        ui.prefs_ui(self, context)


# Window manager properties
# ------------------------------------------


class WmProperties(PropertyGroup):
    prefs_active_tab: EnumProperty(
        items=(
            ("TOOLS", "Tools", ""),
            ("UPDATES", "Updates", ""),
        ),
    )


# Scene properties
# ------------------------------------------


def upd_mod_disable(self, context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            for md in ob.modifiers:
                if md.type == "BOOLEAN":
                    md.show_viewport = self.mod_disable

    action = "Enable" if self.mod_disable else "Disable"
    bpy.ops.ed.undo_push(message=f"Non-destructive [{action}]")


class SceneProperties(PropertyGroup):
    mod_disable: BoolProperty(
        name="Non-destructive",
        description="Disable boolean modifiers on all objects",
        default=True,
        update=upd_mod_disable,
    )
