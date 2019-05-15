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


from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, EnumProperty

from .boolean_methods import BooleanMethods
from .object_utils import ObjectUtils


class Setup(BooleanMethods, ObjectUtils):
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
    double_threshold: FloatProperty(
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

        col = layout.column()
        col.prop(self, "double_threshold")

        split = col.split(factor=0.49)
        split.prop(self, "use_pos_offset")
        sub = split.row()
        sub.enabled = self.use_pos_offset
        sub.prop(self, "pos_offset", text="")

        layout.label(text="Viewport Display")
        col = layout.column()
        col.prop(self, "display_secondary")
        col.prop(self, "display_combined")

    def execute(self, context):
        ob1 = context.object
        obs = context.selected_objects
        if ob1.select_get():
            obs.remove(ob1)

        for md in ob1.modifiers:
            if (
                md.type == "BOOLEAN" and
                md.operation == self.mode and
                md.object and
                "booltron_combined" in md.object
            ):
                ob2 = md.object
                break
        else:
            name = f"{ob1.name} COMBINED {self.mode[:3]}"
            ob2 = self.object_add(name)
            ob2.display_type = self.display_combined
            ob2["booltron_combined"] = self.mode
            self.boolean_mod(ob1, ob2, self.mode, name=self.mode[:3] + " COMBINED", md_apply=False, terminate=False)

        if self.use_pos_offset:
            self.object_pos_offset(obs)

        ob2_mats = ob2.data.materials

        for ob in obs:
            if ob.type == "MESH":
                self.boolean_mod(ob2, ob, "UNION", md_apply=False, terminate=False)
                ob.display_type = self.display_secondary
                for mat in ob.data.materials:
                    if mat.name not in ob2_mats:
                        ob2_mats.append(mat)

        return {"FINISHED"}

    def invoke(self, context, event):
        obs = [ob for ob in context.selected_objects if ob.type == "MESH"]

        if len(obs) < 2 or context.object.type != "MESH":
            self.report({"ERROR"}, "At least two Mesh objects must be selected")
            return {"CANCELLED"}

        prefs = context.preferences.addons[__package__].preferences
        self.double_threshold = prefs.nondestr_double_threshold
        self.use_pos_offset = prefs.nondestr_use_pos_offset
        self.pos_offset = prefs.nondestr_pos_offset
        self.display_secondary = prefs.display_secondary
        self.display_combined = prefs.display_combined

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        return self.execute(context)


class OBJECT_OT_booltron_nondestructive_union(Operator, Setup):
    bl_label = "Booltron Non-destructive Union"
    bl_description = "Combine active (primary) and selected (secondary) objects"
    bl_idname = "object.booltron_nondestructive_union"
    bl_options = {"REGISTER", "UNDO"}

    mode = "UNION"


class OBJECT_OT_booltron_nondestructive_difference(Operator, Setup):
    bl_label = "Booltron Non-destructive Difference"
    bl_description = "Subtract selected (secondary) objects from active (primary) object"
    bl_idname = "object.booltron_nondestructive_difference"
    bl_options = {"REGISTER", "UNDO"}

    mode = "DIFFERENCE"


class OBJECT_OT_booltron_nondestructive_intersect(Operator, Setup):
    bl_label = "Booltron Non-destructive Intersect"
    bl_description = "Keep the common part between active (primary) and selected (secondary) objects"
    bl_idname = "object.booltron_nondestructive_intersect"
    bl_options = {"REGISTER", "UNDO"}

    mode = "INTERSECT"


class OBJECT_OT_booltron_nondestructive_remove(Operator, ObjectUtils):
    bl_label = "Booltron Non-destructive Dismiss"
    bl_description = "Dismiss selected secondary objects from boolean operation"
    bl_idname = "object.booltron_nondestructive_remove"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obs = set(ob for ob in context.selected_objects if "booltron_combined" not in ob)
        is_empty = False

        if not obs:
            return {"CANCELLED"}

        for ob in context.scene.objects:
            if "booltron_combined" in ob:

                for md in ob.modifiers:
                    if md.type == "BOOLEAN" and (not md.object or md.object in obs):
                        ob.modifiers.remove(md)

                for md in ob.modifiers:
                    if md.type == "BOOLEAN":
                        break
                else:
                    is_empty = True
                    self.object_remove(ob)

        if is_empty:
            for ob in context.scene.objects:
                if ob.type == "MESH":
                    for md in ob.modifiers:
                        if md.type == "BOOLEAN" and not md.object:
                            ob.modifiers.remove(md)

        for ob in obs:
            ob.display_type = "TEXTURED"

        return {"FINISHED"}
