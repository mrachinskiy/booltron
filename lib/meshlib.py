# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Callable

import bmesh
import bpy
from bpy.types import Object
from mathutils import bvhtree


def _delete_loose(bm: bmesh.types.BMesh) -> None:
    for v in bm.verts:
        if v.is_wire or not v.link_edges:
            bm.verts.remove(v)


class Utils:
    __slots__ = "merge_distance", "dissolve_distance", "report"

    def __init__(self, report: Callable) -> None:
        self.report = report
        props = bpy.context.window_manager.booltron.destructive
        self.merge_distance = props.merge_distance
        self.dissolve_distance = props.dissolve_distance

    def prepare(self, ob: Object, select: bool = False) -> None:
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=self.merge_distance)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=self.dissolve_distance)
        _delete_loose(bm)
        bmesh.ops.holes_fill(bm, edges=bm.edges)

        for f in bm.faces:
            f.select = select

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


def detect_overlap(obs: list[Object]) -> bool:
    props = bpy.context.window_manager.booltron.destructive
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()

    for ob in obs:
        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh()
        me.transform(ob.matrix_world)

        bm.from_mesh(me)

        ob_eval.to_mesh_clear()

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=props.merge_distance)

    tree = bvhtree.BVHTree.FromBMesh(bm, epsilon=0.00001)
    overlap = tree.overlap(tree)

    bm.free()
    return bool(overlap)
