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
import bmesh
from mathutils import bvhtree


def delete_loose(bm):
    for v in bm.verts:
        if v.is_wire or not v.link_edges:
            bm.verts.remove(v)


class MeshUtils:

    def object_overlap(self, context, obs):
        depsgraph = context.evaluated_depsgraph_get()
        bm = bmesh.new()

        for ob in obs:
            ob_eval = ob.evaluated_get(depsgraph)
            me = ob_eval.to_mesh()
            me.transform(ob.matrix_world)

            bm.from_mesh(me)

            ob_eval.to_mesh_clear()

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=self.merge_distance)

        tree = bvhtree.BVHTree.FromBMesh(bm, epsilon=0.00001)
        overlap = tree.overlap(tree)

        bm.free()
        return bool(overlap)

    def object_prepare(self, context):
        ob1 = context.object
        obs = list(context.selected_objects)
        if ob1.select_get():
            obs.remove(ob1)

        if self.keep_objects:
            space_data = context.space_data
            use_local_view = bool(space_data.local_view)
            obs_copy = []
            app = obs_copy.append

            for ob in obs:
                ob_copy = ob.copy()
                ob_copy.data = ob.data.copy()

                for coll in ob.users_collection:
                    coll.objects.link(ob_copy)

                if use_local_view:
                    ob_copy.local_view_set(space_data, True)

                ob_copy.select_set(True)
                ob.select_set(False)
                app(ob_copy)

            obs = obs_copy

        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.convert(target="MESH")

        if self.use_pos_offset:
            self.object_pos_offset(obs)

    def mesh_prepare(self, ob, select=False):
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=self.merge_distance)
        delete_loose(bm)
        bmesh.ops.holes_fill(bm, edges=bm.edges)

        if self.triangulate:
            bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="SHORT_EDGE")

        for f in bm.faces:
            f.select = select

        bm.to_mesh(me)
        bm.free()

    def mesh_cleanup(self, ob):
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=self.merge_distance)
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
