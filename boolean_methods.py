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


class BooleanMethods:

    def boolean_adaptive(self, context):
        ob1 = context.object
        ob1.select_set(False)

        obs = list(context.selected_objects)
        ob2 = obs.pop()

        if obs:
            if self.is_overlap:
                self.mesh_prepare(ob2, select=True)

                for ob3 in obs:
                    self.mesh_prepare(ob3, select=True)
                    self.boolean_mod(ob2, ob3, "UNION")

                    if self.cleanup:
                        self.mesh_cleanup(ob2)
            else:
                override = {"active_object": ob2}
                bpy.ops.object.join(override)

        if not self.is_overlap:
            self.mesh_prepare(ob2, select=True)

        self.mesh_prepare(ob1, select=False)
        self.boolean_mod(ob1, ob2, self.mode)

        if self.cleanup:
            self.mesh_cleanup(ob1)

        ob1.select_set(True)

    def boolean_mod(self, ob1, ob2, mode, name="Boolean", md_apply=True, terminate=True):
        md = ob1.modifiers.new(name, "BOOLEAN")
        md.show_viewport = not md_apply
        md.operation = mode
        md.double_threshold = self.double_threshold
        md.object = ob2

        if md_apply:
            override = {"object": ob1}
            bpy.ops.object.modifier_apply(override, modifier=md.name)

        if terminate:
            self.object_remove(ob2)
