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


import bpy

from . import versioning


class BooleanMethods:

    def boolean_adaptive(self):
        carve_difference = versioning.SOLVER_OPTION and self.solver == "CARVE" and self.mode == "DIFFERENCE"
        batch = self.is_overlap and not carve_difference

        print(bpy.context.selected_objects)

        ob1 = bpy.context.active_object
        ob1.select = False

        obs = bpy.context.selected_objects
        ob2 = obs.pop()

        if obs:
            scene = bpy.context.scene
            scene.objects.active = ob2

            if batch:
                self.mesh_prepare(ob2, select=True)

                for ob3 in obs:
                    self.mesh_prepare(ob3, select=True)
                    self.boolean_mod(ob2, ob3, "UNION")

                    if self.cleanup:
                        self.mesh_cleanup(ob2)
            else:
                bpy.ops.object.join()

            scene.objects.active = ob1

        if not batch:
            self.mesh_prepare(ob2, select=True)

        self.mesh_prepare(ob1, select=False)
        self.boolean_mod(ob1, ob2, self.mode)

        if self.cleanup:
            self.mesh_cleanup(ob1)

        ob1.select = True

    def boolean_mod(self, ob1, ob2, mode, md_name="Boolean", md_apply=True, terminate=True):
        md = ob1.modifiers.new(md_name, "BOOLEAN")
        md.show_viewport = not md_apply
        md.operation = mode
        if versioning.SOLVER_OPTION:
            md.solver = self.solver
        md.object = ob2

        if md_apply:
            bpy.ops.object.modifier_apply(modifier=md.name)

        if terminate:
            self.object_remove(ob2)
