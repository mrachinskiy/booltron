# SPDX-FileCopyrightText: 2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import tempfile
import traceback
from pathlib import Path

import bpy


def set_up() -> None:
    bpy.ops.mesh.primitive_cube_add()
    ob2 = bpy.context.object
    ob2.name = "OB2"
    ob2.scale = 0.5, 0.5, 1.5

    bpy.ops.mesh.primitive_cube_add()
    ob1 = bpy.context.object
    ob1.name = "OB1"

    ob1.select_set(True)
    ob2.select_set(True)


def cleanup() -> None:
    for me in bpy.data.meshes:
        bpy.data.meshes.remove(me)

    for ng in bpy.data.node_groups:
        bpy.data.node_groups.remove(ng)


def test_dissmiss() -> None:
    bpy.ops.object.booltron_nondestructive_difference()
    ng_name = bpy.context.object.modifiers[0].node_group.name

    bpy.ops.object.booltron_secondary_del()
    assert bool(bpy.context.object.modifiers) == False
    assert bpy.data.node_groups.get(ng_name) == None


def test_select() -> None:
    bpy.ops.object.booltron_nondestructive_difference()
    md_name = bpy.context.object.modifiers[0].name

    bpy.ops.object.select_all(action="DESELECT")

    bpy.ops.object.booltron_secondary_select(modifier_name=md_name)
    assert len(bpy.context.selected_objects) == 1
    assert bpy.context.object.name == "OB2"
    assert bpy.context.object.select_get() == True


def test_mod_disable() -> None:
    bpy.ops.object.booltron_nondestructive_difference()
    mds = bpy.context.object.modifiers
    md = mds.new("Boolean", "BOOLEAN")

    bpy.context.scene.booltron.mod_disable = False

    assert len(mds) == 2
    for md in mds:
        assert md.show_viewport == False


def test_bake() -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        bpy.ops.wm.save_mainfile(filepath=str(path / "temp.blend"))

        bpy.ops.object.booltron_nondestructive_difference()
        bpy.ops.object.booltron_modifier_bake()

        assert (path / "blendcache_temp").exists() == True
        assert (path / "blendcache_temp" / "OB49_Difference").exists() == True

        bpy.ops.object.booltron_modifier_bake_del()

        assert (path / "blendcache_temp" / "OB49_Difference").exists() == False


def main() -> None:
    tools = (
        bpy.ops.object.booltron_nondestructive_difference,
        bpy.ops.object.booltron_nondestructive_union,
        bpy.ops.object.booltron_nondestructive_intersect,
        test_dissmiss,
        test_select,
        test_mod_disable,
        test_bake,
    )

    for tool in tools:
        set_up()
        tool()
        cleanup()


try:
    main()
except:
    traceback.print_exc()
    sys.exit(1)
