# SPDX-FileCopyrightText: 2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import sys
import time
import traceback
from pathlib import Path

import bpy


def get_logger(name: str) -> logging.Logger:
    log = logging.getLogger(name)

    if not log.hasHandlers():
        log.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s %(message)s", "%Y-%m-%d")

        fh = logging.FileHandler(Path(__file__).parent / f"{name}.log", encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)

        log.addHandler(fh)

    return log


def set_up(solver: str) -> None:
    props = bpy.context.window_manager.booltron.destructive
    props.solver = solver
    props.solver_secondary = solver

    bpy.ops.mesh.primitive_cylinder_add()
    ob2 = bpy.context.object
    ob2.scale = 0.15, 0.15, 1
    ob2.location = -1, -1, 0

    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64)
    ob1 = bpy.context.object

    ob1.select_set(True)
    ob2.select_set(True)

    coll = bpy.context.collection
    vec = ob2.location.copy()
    row = 6

    for i in range(2, row ** 2 + 1):
        if i > row and (i % row) == 1:
            vec.x = -1
            vec.y += 0.4
        else:
            vec.x += 0.4

        ob2_copy = ob2.copy()
        ob2_copy.location = vec
        coll.objects.link(ob2_copy)
        ob2_copy.select_set(True)


def cleanup() -> None:
    for me in bpy.data.meshes:
        bpy.data.meshes.remove(me)


def main() -> None:
    log = get_logger("performance")
    ver = ".".join(str(i) for i in bpy.app.version)

    solvers = ("FLOAT", "EXACT")
    if bpy.app.version >= (4, 5, 0):
        solvers = ("MANIFOLD",) + solvers

    for solver in solvers:
        set_up(solver)
        a = time.time()

        bpy.ops.object.booltron_destructive_difference()

        b = time.time()
        cleanup()

        log.info(f"{ver} {solver} {b-a:.3f}")


try:
    main()
except:
    traceback.print_exc()
    sys.exit(1)
