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


import random

import bpy
import bmesh
from mathutils import Vector


class MeshUtils:

    def prepare_selected(self):
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.convert(target="MESH")

        if self.pos_correct:
            obs = bpy.context.selected_objects
            obs.remove(bpy.context.active_object)

            for ob in obs:
                x = random.uniform(-self.pos_offset, self.pos_offset)
                y = random.uniform(-self.pos_offset, self.pos_offset)
                z = random.uniform(-self.pos_offset, self.pos_offset)

                ob.location += Vector((x, y, z))

    def mesh_selection(self, ob, select_action):
        scene = bpy.context.scene
        ops_me = bpy.ops.mesh

        active_object = bpy.context.active_object
        scene.objects.active = ob
        bpy.ops.object.mode_set(mode="EDIT")

        ops_me.reveal()

        ops_me.select_all(action="SELECT")
        ops_me.delete_loose()

        ops_me.select_all(action="SELECT")
        ops_me.remove_doubles(threshold=0.0001)

        ops_me.select_all(action="SELECT")
        ops_me.fill_holes(sides=0)

        if self.triangulate:
            ops_me.select_all(action="SELECT")
            ops_me.quads_convert_to_tris()

        ops_me.select_all(action=select_action)

        bpy.ops.object.mode_set(mode="OBJECT")
        scene.objects.active = active_object

    def is_manifold(self, ob):
        bm = bmesh.new()
        bm.from_mesh(ob.data)

        for edge in bm.edges:
            if not edge.is_manifold:
                bm.free()
                self.report({"ERROR"}, "Boolean operation result is non-manifold")
                return False

        bm.free()
        return True

    def mesh_cleanup(self, ob):
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        bm.to_mesh(me)
        bm.free()
