# SPDX-FileCopyrightText: 2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import traceback

import bpy
from bpy.types import Object


def add_md(ob1: Object, ob2: Object, mode: str) -> None:
    md = ob1.modifiers.new(mode[:3] + " COMBINED", "BOOLEAN")
    md.show_viewport = False
    try:  # VER < 5.0
        md.solver = "FAST"
    except:
        md.solver = "FLOAT"
    md.operation = mode
    md.object = ob2


def add_secondary(loc: tuple[float, float, float]) -> Object:
    bpy.ops.mesh.primitive_cube_add()
    ob = bpy.context.object
    ob.scale = 0.25, 0.25, 1.5
    ob.location = loc
    return ob


def add_combined(mode: str, ob1: Object, *locs: tuple[float, float, float]) -> tuple[str, str, set[Object]]:
    name = f"COMBINED {mode[:3]}"
    me = bpy.data.meshes.new(name)
    c = bpy.data.objects.new(name, me)
    c["booltron_combined"] = mode
    bpy.context.scene.collection.objects.link(c)

    obs = set()
    for loc in locs:
        ob2 = add_secondary(loc)
        add_md(c, ob2, "UNION")
        obs.add(ob2)

    add_md(ob1, c, mode)
    return mode, c.name, obs


def set_up() -> tuple[Object, tuple[tuple[str, str, set[Object]]]]:
    bpy.ops.mesh.primitive_cube_add()
    ob = bpy.context.object

    m1 = add_combined("DIFFERENCE", ob, (0.5, 0.5, 0), (-0.5, 0.5, 0))
    m2 = add_combined("UNION", ob, (0.5, -0.5, 0), (-0.5, -0.5, 0))
    m3 = add_combined("DIFFERENCE", ob, (0.85, -0.85, 1), (-0.85, -0.85, 1))

    return ob, (m1, m2, m3)


def main() -> None:
    ob, mod_setup = set_up()
    bpy.ops.object.empty_add()  # Dummy object so Dissmiss won't affect modifier setup
    bpy.ops.object.booltron_secondary_del()

    assert len(ob.modifiers) == 3

    for md, (mode, comb_name, obs) in zip(ob.modifiers, mod_setup):
        assert bpy.data.meshes.get(comb_name) == None
        assert md.type == "NODES"
        assert md.node_group["booltron"] == mode

        md_obs = set()
        for node in md.node_group.nodes:
            if node.type == "OBJECT_INFO":
                md_obs.add(node.inputs["Object"].default_value)
        assert md_obs == obs


try:
    main()
except:
    traceback.print_exc()
    sys.exit(1)
