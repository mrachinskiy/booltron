# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bmesh
import bpy
from bpy.types import Object
from mathutils import bvhtree


def _delete_loose(bm: bmesh.types.BMesh) -> None:
    for v in bm.verts:
        if v.is_wire or not v.link_edges:
            bm.verts.remove(v)


def prepare(obs: list[Object], merge_distance: float, dissolve_distance: float, select: bool = False) -> None:
    for ob in obs:
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge_distance)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=dissolve_distance)
        _delete_loose(bm)
        bmesh.ops.holes_fill(bm, edges=bm.edges)

        for f in bm.faces:
            f.select = select

        bm.to_mesh(me)
        bm.free()


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


def is_nonmanifold(ob: Object) -> bool:
    bm = bmesh.new()
    bm.from_mesh(ob.data)

    for e in bm.edges:
        if not e.is_manifold:
            bm.free()
            return True

    bm.free()
    return False


def is_nonmanifold_eval(obs: list[Object]) -> bool:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()

    for ob in obs:
        ob_eval = ob.evaluated_get(depsgraph)
        bm.from_mesh(ob_eval.to_mesh())
        ob_eval.to_mesh_clear()

    for e in bm.edges:
        if not e.is_manifold:
            bm.free()
            return True

    bm.free()
    return False
