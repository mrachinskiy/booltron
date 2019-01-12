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


import bpy
import bmesh
from mathutils import bvhtree


def delete_loose(bm):
    for v in bm.verts:
        if v.is_wire or not v.link_edges:
            bm.verts.remove(v)


class MeshUtils:

    def object_overlap(self, obs):
        depsgraph = bpy.context.depsgraph
        bm = bmesh.new()

        for ob in obs:
            me = ob.to_mesh(depsgraph, True)
            me.transform(ob.matrix_world)

            bm.from_mesh(me)

            bpy.data.meshes.remove(me)

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

        tree = bvhtree.BVHTree.FromBMesh(bm, epsilon=0.00001)
        overlap = tree.overlap(tree)

        bm.free()
        return bool(overlap)

    def object_prepare(self):
        ob1 = bpy.context.active_object
        obs = bpy.context.selected_objects
        if ob1.select_get():
            obs.remove(ob1)

        if self.keep_objects:
            # TODO local view
            # space_data = bpy.context.space_data

            for ob in obs:
                ob_copy = ob.copy()
                ob_copy.data = ob.data.copy()

                for coll in ob.users_collection:
                    coll.objects.link(ob_copy)

                # if self.local_view:
                #     base.layers_from_view(space_data)

                ob_copy.select_set(True)
                ob.select_set(False)

        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.convert(target="MESH")

        if self.pos_correct:
            self.object_pos_correct(obs)

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
