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


from typing import Iterable, Callable, Set

from bpy.types import Object, Context
import bmesh
from bmesh.types import BMesh
from mathutils import bvhtree


OperatorReport = Callable[[Set[str], str], None]


def _cleanup(bm: BMesh, merge_distance: float) -> None:
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge_distance)

    # Delete loose
    for v in bm.verts:
        if v.is_wire or not v.link_edges:
            bm.verts.remove(v)


class Utils:
    __slots__ = ("merge_distance", "triangulate", "report")

    def __init__(self, merge_distance=0.0002, triangulate=False, report: OperatorReport = lambda x, y: None) -> None:
        self.merge_distance = merge_distance
        self.triangulate = triangulate
        self.report = report

    def prepare(self, ob: Object, select=False) -> None:
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)

        _cleanup(bm, self.merge_distance)
        bmesh.ops.holes_fill(bm, edges=bm.edges)

        if self.triangulate:
            bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="SHORT_EDGE")

        for f in bm.faces:
            f.select = select

        bm.to_mesh(me)
        bm.free()

    def cleanup(self, ob: Object) -> None:
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)

        _cleanup(bm, self.merge_distance)

        bm.to_mesh(me)
        bm.free()

    def check(self, ob: Object) -> bool:
        bm = bmesh.new()
        bm.from_mesh(ob.data)

        for e in bm.edges:
            if not e.is_manifold:
                self.report({"ERROR"}, "Boolean operation result is non-manifold")
                bm.free()
                return True

        bm.free()
        return False


def detect_overlap(context: Context, obs: Iterable[Object], merge_distance: float):
    depsgraph = context.evaluated_depsgraph_get()
    bm = bmesh.new()

    for ob in obs:
        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh()
        me.transform(ob.matrix_world)

        bm.from_mesh(me)

        ob_eval.to_mesh_clear()

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge_distance)

    tree = bvhtree.BVHTree.FromBMesh(bm, epsilon=0.00001)
    overlap = tree.overlap(tree)

    bm.free()
    return bool(overlap)
