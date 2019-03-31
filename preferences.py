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


from bpy.types import AddonPreferences
from bpy.props import EnumProperty, BoolProperty, FloatProperty

from . import mod_update


# Add-on preferences
# ------------------------------------------


class BooltronPreferences(AddonPreferences):
    bl_idname = __package__

    active_section: EnumProperty(
        items=(
            ("DESTRUCTIVE", "Destructive", ""),
            ("NONDESTRUCTIVE", "Non-destructive", ""),
            ("UI", "Themes", ""),
            ("UPDATES", "Updates", ""),
        ),
    )
    update_use_auto_check: BoolProperty(
        name="Automatically check for updates",
        description="Automatically check for updates with specified interval",
        default=True,
    )
    update_interval: EnumProperty(
        name="Auto-check interval",
        description="Auto-check interval",
        items=(
            ("1", "Once a day", ""),
            ("7", "Once a week", ""),
            ("30", "Once a month", ""),
        ),
        default="7",
    )
    update_use_prerelease: BoolProperty(
        name="Update to pre-release",
        description="Update add-on to pre-release version if available",
    )
    theme_icon: EnumProperty(
        name="Icons",
        items=(
            ("LIGHT", "Light", ""),
            ("DARK", "Dark", ""),
        ),
    )
    cleanup: BoolProperty(
        name="Mesh Cleanup",
        description=(
            "Perform mesh cleanup in between boolean operations, "
            "enabling this option will greatly affect performance of a boolean operation"
        ),
    )
    triangulate: BoolProperty(
        name="Triangulate",
        description=(
            "Triangulate geometry before boolean operation, "
            "in some cases may improve result of a boolean operation"
        ),
    )
    destr_pos_correct: BoolProperty(
        name="Correct Position",
        description=(
            "Shift objects position for a very small amount to avoid coplanar "
            "geometry errors during boolean operation (does not affect active object)"
        ),
    )
    destr_pos_offset: FloatProperty(
        name="Position Offset",
        description="Position offset is randomly generated for each object in range [-x, +x] input value",
        default=0.005,
        min=0.0,
        step=0.01,
        precision=3,
        unit="LENGTH",
    )
    destr_double_threshold: FloatProperty(
        name="Overlap Threshold",
        description="Threshold for checking overlapping geometry",
        default=0.000001,
        min=0.0,
        step=0.0001,
        precision=6,
    )
    nondestr_pos_correct: BoolProperty(
        name="Correct Position",
        description=(
            "Shift objects position for a very small amount to avoid coplanar "
            "geometry errors during boolean operation (does not affect active object)"
        ),
    )
    nondestr_pos_offset: FloatProperty(
        name="Position Offset",
        description="Position offset is randomly generated for each object in range [-x, +x] input value",
        default=0.005,
        min=0.0,
        step=0.01,
        precision=3,
        unit="LENGTH",
    )
    nondestr_double_threshold: FloatProperty(
        name="Overlap Threshold",
        description="Threshold for checking overlapping geometry",
        default=0.000001,
        min=0.0,
        step=0.0001,
        precision=6,
    )
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

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        split = layout.split(factor=0.25)
        col = split.column()
        col.use_property_split = False
        col.scale_y = 1.3
        col.prop(self, "active_section", expand=True)

        box = split.box()

        if self.active_section == "DESTRUCTIVE":
            col = box.column()
            col.prop(self, "destr_double_threshold")

            split = col.split(factor=0.49)
            split.prop(self, "destr_pos_correct")
            sub = split.row()
            sub.active = self.destr_pos_correct
            sub.prop(self, "destr_pos_offset", text="")

            col.prop(self, "cleanup")
            col.prop(self, "triangulate")

        elif self.active_section == "NONDESTRUCTIVE":
            col = box.column()
            col.prop(self, "nondestr_double_threshold")

            split = col.split(factor=0.49)
            split.prop(self, "nondestr_pos_correct")
            sub = split.row()
            sub.active = self.nondestr_pos_correct
            sub.prop(self, "nondestr_pos_offset", text="")

            col.prop(self, "display_secondary")
            col.prop(self, "display_combined")

        elif self.active_section == "UI":
            col = box.column()
            col.prop(self, "theme_icon")

        elif self.active_section == "UPDATES":
            mod_update.prefs_ui(self, box)


# Window manager properties
# ------------------------------------------


def update_mod_disable(self, context):
    show = self.booltron_mod_disable

    for ob in context.scene.objects:
        if ob.type == "MESH":
            for md in ob.modifiers:
                if md.type == "BOOLEAN":
                    md.show_viewport = show


mod_disable = BoolProperty(
    description="Disable boolean modifiers on all objects",
    default=True,
    update=update_mod_disable,
)
