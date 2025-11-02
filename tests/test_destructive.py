# SPDX-FileCopyrightText: 2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import traceback

import bpy


def set_up(solver: str) -> None:
    bpy.ops.mesh.primitive_cube_add()
    ob2 = bpy.context.object
    ob2.scale = 0.5, 0.5, 1.5

    bpy.ops.mesh.primitive_cube_add()
    ob1 = bpy.context.object

    ob1.select_set(True)
    ob2.select_set(True)

    bpy.context.window_manager.booltron.destructive.solver = solver


def cleanup() -> None:
    for me in bpy.data.meshes:
        bpy.data.meshes.remove(me)


def main() -> None:
    tools = [
        bpy.ops.object.booltron_destructive_difference,
        bpy.ops.object.booltron_destructive_union,
        bpy.ops.object.booltron_destructive_intersect,
        bpy.ops.object.booltron_destructive_slice,
    ]

    solvers = ["MANIFOLD", "FLOAT", "EXACT"]
    if bpy.app.version < (4, 5, 0):
        solvers.pop(0)

    for tool in tools:
        while solvers:
            solver = solvers.pop()
        set_up(solver)
        tool()
        cleanup()


try:
    main()
except:
    traceback.print_exc()
    sys.exit(1)
