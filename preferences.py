# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty
from bpy.types import AddonPreferences, PropertyGroup

from . import ui


# Operator properties
# ------------------------------------------


class ToolProps:

    # Primary
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

    use_loc_rnd: BoolProperty(
        name="Randomize Location",
        description=(
            "Shift objects location for a very small amount to avoid coplanar "
            "geometry errors during boolean operation"
        ),
    )
    loc_offset: FloatProperty(
        name="Location Offset",
        description="Location offset is randomly generated for each object in range [-x, +x] input value",
        default=0.005,
        min=0.0,
        step=0.01,
        precision=3,
        unit="LENGTH",
    )
    seed: IntProperty(
        name="Seed",
        description="Get different offset values",
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

    # Post-processing
    # ------------------------

    use_bake: BoolProperty(
        name="Bake",
        description="Bake modifier result",
    )


# Duplicate solver properties
for prop in ("solver", "use_self", "use_hole_tolerant", "threshold"):
    ToolProps.__annotations__[f"{prop}_secondary"] = ToolProps.__annotations__[prop]


class ToolPropsGroup(ToolProps, PropertyGroup):
    first_run: BoolProperty(default=True)


# Add-on preferences
# ------------------------------------------


class Preferences(ToolProps, AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        ui.prefs_ui(self, context)


# Window manager properties
# ------------------------------------------


class WmProperties(PropertyGroup):
    destructive: PointerProperty(type=ToolPropsGroup)
    non_destructive: PointerProperty(type=ToolPropsGroup)


# Scene properties
# ------------------------------------------


def upd_mod_disable(self, context):
    from .lib import modlib

    modlib.disable_mods(self.mod_disable)
    action = "Enable" if self.mod_disable else "Disable"
    bpy.ops.ed.undo_push(message=f"Non-destructive [{action}]")


class SceneProperties(PropertyGroup):
    mod_disable: BoolProperty(
        name="Non-destructive",
        description="Disable boolean modifiers on all objects",
        default=True,
        update=upd_mod_disable,
    )
