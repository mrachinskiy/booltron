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

    def boolean_optimized(self):
        scene = bpy.context.scene

        ob1 = bpy.context.active_object
        ob1.select = False

        obs = bpy.context.selected_objects
        ob2 = obs[0]

        if len(obs) != 1:
            scene.objects.active = ob2
            bpy.ops.object.join()
            scene.objects.active = ob1

        self.mesh_selection(ob2, "SELECT")
        self.mesh_selection(ob1, "DESELECT")
        self.boolean_mod(ob1, ob2, self.mode)

        ob1.select = True

    def boolean_batch(self):
        cleanup = self.method == "BATCH_CLEANUP"

        ob1 = bpy.context.active_object
        ob1.select = False

        self.mesh_selection(ob1, "DESELECT")

        for ob2 in bpy.context.selected_objects:
            self.mesh_selection(ob2, "SELECT")
            self.boolean_mod(ob1, ob2, self.mode)

            if cleanup:
                self.mesh_cleanup(ob1)

        ob1.select = True

    def boolean_mod(self, ob1, ob2, mode, terminate=True):
        md = ob1.modifiers.new("Boolean", "BOOLEAN")
        md.show_viewport = False
        md.show_render = False
        md.operation = mode
        if versioning.SOLVER_OPTION:
            md.solver = self.solver
        md.object = ob2
        bpy.ops.object.modifier_apply(modifier="Boolean")

        if terminate:
            me = ob2.data
            bpy.context.scene.objects.unlink(ob2)  # pre 2.78 compatibility
            bpy.data.objects.remove(ob2)
            bpy.data.meshes.remove(me)
