# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

# Migration utilities from deprecated combined object
# to the new Geometry Nodes workflow

import bpy
from bpy.types import Modifier, Object


def detect_and_migrate() -> bool:
    for ob in bpy.context.scene.objects:
        if ob.type == "MESH" and "booltron_combined" in ob:
            _migrate_scene()
            return


def _replace_mod(ob: Object, md_old: Modifier, md_new: Modifier):
        index_old = ob.modifiers.find(md_old.name)
        index_new = ob.modifiers.find(md_new.name)

        ob.modifiers.move(index_new, index_old)
        ob.modifiers.remove(md_old)


def _migrate_scene() -> None:
    from ..lib import modlib

    modlib.disable_mods(False)

    combined_obs = set()
    for ob in bpy.context.scene.objects:

        if ob.type != "MESH":
            continue

        for md in ob.modifiers[:]:
            if md.type == "BOOLEAN" and md.object is not None and "booltron_combined" in md.object:
                secondary_obs = []
                override = {
                    "solver": md.solver,
                    "use_self": md.use_self,
                    "use_hole_tolerant": md.use_hole_tolerant,
                }

                for md_secondary in md.object.modifiers:
                    if md_secondary.type == "BOOLEAN" and md_secondary.object is not None:
                        secondary_obs.append(md_secondary.object)
                        override["solver_secondary"] = md_secondary.solver
                        override["use_self_secondary"] = md_secondary.use_self
                        override["use_hole_tolerant_secondary"] = md_secondary.use_hole_tolerant

                if not secondary_obs:
                    combined_obs.add(md.object)
                    ob.modifiers.remove(md)
                    continue

                if override["solver"] == "FAST":
                    override["solver"] = "FLOAT"
                    override["use_self"] = False
                    override["use_hole_tolerant"] = False
                if override["solver_secondary"] == "FAST":
                    override["solver_secondary"] = "FLOAT"
                    override["use_self_secondary"] = False
                    override["use_hole_tolerant_secondary"] = False

                Mod = modlib.ModGN(md.operation, override)
                md_new = Mod.add(ob, secondary_obs)
                md_new.show_viewport = False
                combined_obs.add(md.object)
                _replace_mod(ob, md, md_new)

    for ob in combined_obs:
        bpy.data.meshes.remove(ob.data)

    modlib.disable_mods(True)
