# SPDX-FileCopyrightText: 2014-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Iterator
from pathlib import Path

import bpy
from bpy.types import BlendData, GeometryNode, Modifier, NodeGroup, Object

from .. import var


def _ng_import(filepath: Path, ng_name: str) -> BlendData:
    with bpy.data.libraries.load(str(filepath)) as (data_from, data_to):
        data_to.node_groups = [ng_name]
    return data_to.node_groups[0]


def _find_connected(node: GeometryNode) -> Iterator[GeometryNode]:
    for output in node.outputs:
        for link in output.links:
            if not (link.to_node.type == "MESH_BOOLEAN" and link.to_node.name == "SECONDARY"):
                yield link.to_node
                yield from _find_connected(link.to_node)


class ModBoolean:
    __slots__ = "solver", "threshold", "use_self", "use_hole_tolerant"

    def __init__(self) -> None:
        props = bpy.context.window_manager.booltron.destructive
        self.solver = props.solver
        self.threshold = props.threshold
        self.use_self = props.use_self
        self.use_hole_tolerant = props.use_hole_tolerant

    def add(self, ob1: Object, ob2: Object, mode: str, remove_ob2: bool | None = None) -> None:
        if remove_ob2 is None:
            remove_ob2 = True

        md = ob1.modifiers.new(mode.title(), "BOOLEAN")
        md.show_viewport = False
        md.show_expanded = False
        md.operation = mode
        md.solver = self.solver
        md.use_self = self.use_self
        md.use_hole_tolerant = self.use_hole_tolerant
        md.double_threshold = self.threshold
        md.object = ob2

        with bpy.context.temp_override(object=ob1):
            bpy.ops.object.modifier_apply(modifier=md.name)

        if remove_ob2:
            bpy.data.meshes.remove(ob2.data)


class ModGN:
    __slots__ = (
        "mode",
        "solver",
        "use_self",
        "use_hole_tolerant",
        "solver_secondary",
        "use_self_secondary",
        "use_hole_tolerant_secondary",
        "loc_offset",
        "merge_distance",
    )

    def __init__(self, mode: str) -> None:
        props = bpy.context.window_manager.booltron.non_destructive
        self.mode = mode

        self.solver = props.solver
        self.use_self = props.use_self
        self.use_hole_tolerant = props.use_hole_tolerant
        if props.solver == "FAST":
            self.solver = "FLOAT"
            self.use_self = False
            self.use_hole_tolerant = False

        self.solver_secondary = props.solver_secondary
        self.use_self_secondary = props.use_self_secondary
        self.use_hole_tolerant_secondary = props.use_hole_tolerant_secondary
        if props.solver_secondary == "FAST":
            self.solver_secondary = "FLOAT"
            self.use_self_secondary = False
            self.use_hole_tolerant_secondary = False

        self.loc_offset = props.loc_offset if props.use_loc_rnd else 0.0
        self.merge_distance = props.merge_distance

    def add(self, ob1: Object, obs: list[Object]) -> Modifier:
        name = f"{ob1.name} {self.mode.title()}"
        ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
        ng["booltron"] = self.mode
        ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        rnd_loc_socket = ng.interface.new_socket("Randomize Location", in_out="INPUT", socket_type="NodeSocketFloat")
        rnd_loc_socket.subtype = "DISTANCE"
        rnd_loc_socket.min_value = 0.0
        rnd_loc_socket.force_non_field = True

        nodes = ng.nodes

        in_ = nodes.new("NodeGroupInput")
        in_.location.x = -200
        in_.select = False

        out = nodes.new("NodeGroupOutput")
        out.location.x = 400
        out.select = False

        bake = nodes.new("GeometryNodeBake")
        bake.location.x = 200
        bake.select = False

        ng.links.new(bake.outputs[0], out.inputs[0])

        primary = nodes.new("GeometryNodeMeshBoolean")
        primary.name = "PRIMARY"
        primary.operation = self.mode
        primary.solver = self.solver
        primary.inputs[2].default_value = self.use_self
        primary.inputs[3].default_value = self.use_hole_tolerant
        primary.select = False


        ng.links.new(in_.outputs[0], primary.inputs[0 if self.mode == "DIFFERENCE" else 1])
        ng.links.new(primary.outputs[0], bake.inputs[0])

        secondary = nodes.new("GeometryNodeMeshBoolean")
        secondary.name = "SECONDARY"
        secondary.operation = "UNION"
        secondary.solver = self.solver_secondary
        secondary.inputs[2].default_value = self.use_self_secondary
        secondary.inputs[3].default_value = self.use_hole_tolerant_secondary
        secondary.location.y = -250
        secondary.select = False

        ng.links.new(secondary.outputs[0], primary.inputs[1])

        seed = 0
        for ob in obs:
            node = self._ob_add(ng, in_, ob)
            node.inputs[2].default_value = seed
            ng.links.new(node.outputs[0], secondary.inputs[1])
            seed += 1

        md = ob1.modifiers.new(self.mode.title(), "NODES")
        md["Socket_2"] = self.loc_offset
        md.show_expanded = False
        md.show_in_editmode = False
        md.node_group = ng

        return md

    def extend(self, md: Modifier, obs: list[Object]) -> None:
        md.show_viewport = False

        ng = md.node_group
        nodes = ng.nodes
        ng_rnd_loc = bpy.data.node_groups.get("Randomize Location")
        seed = 0

        existing_obs = set()
        for node in nodes[:]:

            if node.type == "OBJECT_INFO":
                ng_ob = node.inputs[0].default_value
                if ng_ob is None:
                    nodes.remove(node)
                else:
                    existing_obs.add(ng_ob)

            elif node.type == "MESH_BOOLEAN":
                if node.name == "PRIMARY":
                    node.solver = self.solver
                    node.inputs[2].default_value = self.use_self
                    node.inputs[3].default_value = self.use_hole_tolerant
                elif node.name == "SECONDARY":
                    secondary = node
                    node.solver = self.solver_secondary
                    node.inputs[2].default_value = self.use_self_secondary
                    node.inputs[3].default_value = self.use_hole_tolerant_secondary

            elif ng_rnd_loc and node.type == "GROUP" and node.node_tree is ng_rnd_loc:
                if (ng_seed := node.inputs[2].default_value) >= seed:
                    seed = ng_seed + 1

            elif node.type == "GROUP_INPUT":
                in_ = node

        for ob in obs:
            if ob not in existing_obs:
                node = self._ob_add(ng, in_, ob)
                node.inputs[2].default_value = seed
                ng.links.new(node.outputs[0], secondary.inputs[1])

        md.show_viewport = True

    def _ob_add(self, ng: NodeGroup, in_: GeometryNode, ob: Object) -> GeometryNode:
        nodes = ng.nodes

        node = nodes.new("GeometryNodeObjectInfo")
        node.inputs[0].default_value = ob
        node.transform_space = "RELATIVE"
        node.location = -400, -250
        node.select = False
        node_output_index = 4

        if ob.type != "MESH":
            node.location = -600, -500

            weld = nodes.new("GeometryNodeMergeByDistance")
            weld.inputs[2].default_value = self.merge_distance
            weld.location = -400, -500
            weld.select = False

            ng.links.new(node.outputs[4], weld.inputs[0])

            node = weld
            node_output_index = 0

        if (ng_rnd_loc := bpy.data.node_groups.get("Randomize Location")) is None:
            ng_rnd_loc = _ng_import(var.ASSET_NODES_FILEPATH, "Randomize Location")

        rnd_loc = nodes.new("GeometryNodeGroup")
        rnd_loc.node_tree = ng_rnd_loc
        rnd_loc.location = -200, node.location.y
        rnd_loc.select = False

        ng.links.new(in_.outputs[1], rnd_loc.inputs[1])
        ng.links.new(node.outputs[node_output_index], rnd_loc.inputs[0])

        return rnd_loc

    @staticmethod
    def remove(md: Modifier, obs: set[Object]) -> None:
        md.show_viewport = False

        nodes = md.node_group.nodes

        for node in nodes[:]:
            if node.type == "OBJECT_INFO":
                ob = node.inputs[0].default_value
                if ob is None or ob in obs:
                    for _node in list(_find_connected(node)):
                        nodes.remove(_node)
                    nodes.remove(node)

        for node in nodes:
            if node.type == "OBJECT_INFO":
                break
        else:
            ob = md.id_data
            ng = md.node_group
            ModGN.cache_del(md)
            ob.modifiers.remove(md)
            bpy.data.node_groups.remove(ng)
            return

        md.show_viewport = True

    @staticmethod
    def has_obs(md: Modifier, obs: set[Object]) -> bool:
        for node in md.node_group.nodes:
            if node.type == "OBJECT_INFO":
                if node.inputs[0].default_value in obs:
                    return True

        return False

    @staticmethod
    def is_gn_mod(md: Modifier) -> bool:
        return md.type == "NODES" and md.node_group and "booltron" in md.node_group

    @staticmethod
    def check_mode(md: Modifier, mode: str) -> bool:
        return md.node_group["booltron"] == mode

    @staticmethod
    def cache(md) -> None:
        if bpy.data.is_saved:
            bpy.ops.object.geometry_node_bake_single(session_uid=md.id_data.session_uid, modifier_name=md.name, bake_id=md.bakes[0].bake_id)

    @staticmethod
    def cache_del(md) -> None:
        if bpy.data.is_saved:
            bpy.ops.object.geometry_node_bake_delete_single(session_uid=md.id_data.session_uid, modifier_name=md.name, bake_id=md.bakes[0].bake_id)
