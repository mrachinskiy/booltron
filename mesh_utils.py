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
from mathutils import Vector, bvhtree


def delete_loose(bm):
    for v in bm.verts:
        if v.is_wire or not v.link_edges:
            bm.verts.remove(v)


class MeshUtils:

    def object_overlap(self, obs):
        scene = bpy.context.scene
        bm = bmesh.new()

        for ob in obs:
            me = ob.to_mesh(scene, True, "PREVIEW", calc_tessface=False)
            me.transform(ob.matrix_world)

            bm.from_mesh(me)

            bpy.data.meshes.remove(me)

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

        tree = bvhtree.BVHTree.FromBMesh(bm, epsilon=0.00001)
        overlap = tree.overlap(tree)

        bm.free()
        return bool(overlap)

    def object_prepare(self):
        if self.keep_objects:
            space_data = bpy.context.space_data
            scene = bpy.context.scene
            obs = bpy.context.selected_objects
            obs.remove(bpy.context.active_object)

            for ob in obs:
                ob_copy = ob.copy()
                ob_copy.data = ob.data.copy()
                base = scene.objects.link(ob_copy)

                if self.local_view:
                    base.layers_from_view(space_data)

                ob.select = False

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

    def mesh_prepare(self, ob, select=False):
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        delete_loose(bm)
        bmesh.ops.holes_fill(bm, edges=bm.edges)

        if self.triangulate:
            bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=3)

        for f in bm.faces:
            f.select = select

        bm.to_mesh(me)
        bm.free()

    def mesh_cleanup(self, ob):
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        delete_loose(bm)

        bm.to_mesh(me)
        bm.free()

    def mesh_check(self, ob):
        bm = bmesh.new()
        bm.from_mesh(ob.data)

        for e in bm.edges:
            if not e.is_manifold:
                self.report({"ERROR"}, "Boolean operation result is non-manifold")
                bm.free()
                return True

        bm.free()
        return False
