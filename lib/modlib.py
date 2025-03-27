# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Iterator
from pathlib import Path

import bpy
from bpy.types import BlendData, GeometryNode, Modifier, NodeGroup, NodeSocket, NodeSocketGeometry, Object

from .. import var


def disable_mods(value: bool) -> None:
    for ob in bpy.context.scene.objects:
        if ob.type == "MESH":
            for md in ob.modifiers:
                if md.type == "BOOLEAN" or ModGN.is_gn_mod(md):
                    md.show_viewport = value


def _ng_import(filepath: Path, ng_name: str) -> BlendData:
    with bpy.data.libraries.load(str(filepath)) as (data_from, data_to):
        data_to.node_groups = [ng_name]
    return data_to.node_groups[0]


def _walk_tree(node: GeometryNode) -> Iterator[GeometryNode]:
    for input_ in node.inputs:
        for link in input_.links:
            if link.from_node.type != "GROUP_INPUT":
                yield link.from_node
                yield from _walk_tree(link.from_node)


def secondary_visibility_set(ob: Object, display_type="TEXTURED") -> None:
    visible = display_type == "TEXTURED"

    ob.display_type = display_type
    ob.hide_render = not visible

    # Common
    ob.visible_camera = visible
    ob.visible_shadow = visible

    # Cycles
    ob.visible_diffuse = visible
    ob.visible_glossy = visible
    ob.visible_transmission = visible
    ob.visible_volume_scatter = visible

    # EEVEE
    ob.hide_probe_volume = not visible
    ob.hide_probe_sphere = not visible
    ob.hide_probe_plane = not visible


class ModBoolean:
    __slots__ = (
        "solver",
        "use_self",
        "use_hole_tolerant",
        "threshold",
        "solver_secondary",
        "use_self_secondary",
        "use_hole_tolerant_secondary",
        "threshold_secondary",
    )

    def __init__(self) -> None:
        props = bpy.context.window_manager.booltron.destructive
        for prop in self.__slots__:
            setattr(self, prop, getattr(props, prop))

    def add(self, ob1: Object, ob2: Object, mode: str, remove_ob2: bool = True) -> None:
        md = ob1.modifiers.new(mode.title(), "BOOLEAN")
        md.show_viewport = False
        md.object = ob2

        if mode == "SECONDARY":
            md.operation = "UNION"
            md.solver = self.solver
            md.use_self = self.use_self
            md.use_hole_tolerant = self.use_hole_tolerant
            md.double_threshold = self.threshold
        else:
            md.operation = mode
            md.solver = self.solver_secondary
            md.use_self = self.use_self_secondary
            md.use_hole_tolerant = self.use_hole_tolerant_secondary
            md.double_threshold = self.threshold_secondary

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

    def __init__(self, mode: str, override: dict[str, str | bool] | None = None) -> None:
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

        if override is not None:
            for k, v in override.items():
                setattr(self, k, v)

    def add(self, ob1: Object, obs: list[Object], md: Modifier | None = None) -> Modifier:
        name = f"{ob1.name} {self.mode.title()}"
        ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
        ng["booltron"] = self.mode

        sock_geo_in = ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        sock_geo_out = ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

        panel_rnd = ng.interface.new_panel("Randomize Location", default_closed=True)
        sock_ofst = ng.interface.new_socket("Offset", in_out="INPUT", socket_type="NodeSocketFloat", parent=panel_rnd)
        sock_ofst.subtype = "DISTANCE"
        sock_ofst.min_value = 0.0
        sock_ofst.force_non_field = True
        sock_seed = ng.interface.new_socket("Seed", in_out="INPUT", socket_type="NodeSocketInt", parent=panel_rnd)
        sock_seed.min_value = 0
        sock_seed.force_non_field = True

        nodes = ng.nodes

        in_ = nodes.new("NodeGroupInput")
        in_.location.x = -200
        in_.select = False
        in_geo = in_.outputs[sock_geo_in.identifier]
        in_ofst = in_.outputs[sock_ofst.identifier]
        in_seed = in_.outputs[sock_seed.identifier]

        out = nodes.new("NodeGroupOutput")
        out.location.x = 400
        out.select = False
        out_geo = out.inputs[sock_geo_out.identifier]

        bake = nodes.new("GeometryNodeBake")
        bake.location.x = 200
        bake.select = False

        ng.links.new(bake.outputs["Item_0"], out_geo)

        primary = nodes.new("GeometryNodeMeshBoolean")
        primary.name = "PRIMARY"
        primary.operation = self.mode
        primary.solver = self.solver
        primary.inputs["Self Intersection"].default_value = self.use_self
        primary.inputs["Hole Tolerant"].default_value = self.use_hole_tolerant
        primary.select = False

        ng.links.new(in_geo, primary.inputs["Mesh 1" if self.mode == "DIFFERENCE" else "Mesh 2"])
        ng.links.new(primary.outputs["Mesh"], bake.inputs["Item_0"])

        secondary = nodes.new("GeometryNodeMeshBoolean")
        secondary.name = "SECONDARY"
        secondary.operation = "UNION"
        secondary.solver = self.solver_secondary
        secondary.inputs["Self Intersection"].default_value = self.use_self_secondary
        secondary.inputs["Hole Tolerant"].default_value = self.use_hole_tolerant_secondary
        secondary.location.y = -250
        secondary.select = False

        ng.links.new(secondary.outputs["Mesh"], primary.inputs["Mesh 2"])

        seed = 0
        for ob in obs:
            _out = self._ob_add(ng, ob, in_ofst, in_seed, seed)
            ng.links.new(_out, secondary.inputs["Mesh 2"])
            seed += 1

        if not md:
            md = ob1.modifiers.new(self.mode.title(), "NODES")
        md[sock_ofst.identifier] = self.loc_offset
        md.show_expanded = False
        md.show_in_editmode = False
        md.show_group_selector = False
        md.node_group = ng
        if hasattr(md, "bake_target"):  # VER < Blender 4.3
            md.bake_target = "DISK"

        return md

    def extend(self, md: Modifier, obs: list[Object]) -> None:
        md.show_viewport = False

        ng = md.node_group
        nodes = ng.nodes

        ng_obs = set()
        for node in nodes:
            if node.type == "OBJECT_INFO" and (ob := node.inputs["Object"].default_value):
                ng_obs.add(ob)
        ng_obs.update(obs)

        bpy.data.node_groups.remove(ng)
        self.add(md.id_data, ng_obs, md)

        md.show_viewport = True

    def _ob_add(self, ng: NodeGroup, ob: Object, in_ofst: NodeSocket, in_seed: NodeSocket, seed: int = 0) -> NodeSocketGeometry:
        nodes = ng.nodes

        node = nodes.new("GeometryNodeObjectInfo")
        node.inputs["Object"].default_value = ob
        node.transform_space = "RELATIVE"
        node.location = -400, -250
        node.select = False

        if ob.type != "MESH":
            node.location = -600, -500

            weld = nodes.new("GeometryNodeMergeByDistance")
            weld.inputs["Distance"].default_value = self.merge_distance
            weld.location = -400, -500
            weld.select = False

            ng.links.new(node.outputs["Geometry"], weld.inputs["Geometry"])
            node = weld

        if (ng_rnd := bpy.data.node_groups.get("Randomize Location")) is None:
            ng_rnd = _ng_import(var.ASSET_NODES_FILEPATH, "Randomize Location")

        rnd = nodes.new("GeometryNodeGroup")
        rnd.node_tree = ng_rnd
        rnd.location = -200, node.location.y
        rnd.select = False

        try:  # VER >= 4.3
            node_add = nodes.new("FunctionNodeIntegerMath")
        except:
            node_add = nodes.new("ShaderNodeMath")
        node_add.inputs["Value_001"].default_value = seed
        node_add.location = -200, node.location.y - 150
        node_add.hide = True
        node_add.select = False

        ng.links.new(in_seed, node_add.inputs["Value"])
        ng.links.new(node_add.outputs["Value"], rnd.inputs["Seed"])
        ng.links.new(in_ofst, rnd.inputs["Offset"])
        ng.links.new(node.outputs["Geometry"], rnd.inputs["Geometry"])

        return rnd.outputs["Geometry"]

    @staticmethod
    def remove(md: Modifier, obs: set[Object]) -> bool:
        md.show_viewport = False
        nodes = md.node_group.nodes
        has_obs = False

        for link in nodes["SECONDARY"].inputs["Mesh"].links:
            _del = {x.type: x for x in _walk_tree(link.from_node)}

            if (node := _del.get("OBJECT_INFO")) and (ob := node.inputs["Object"].default_value):
                if ob not in obs:
                    has_obs = True
                    continue
                secondary_visibility_set(ob)

            nodes.remove(link.from_node)
            for node in _del.values():
                nodes.remove(node)

        if has_obs:
            md.show_viewport = True
            return False

        ob = md.id_data
        ng = md.node_group
        ModGN.bake_del(md)
        ob.modifiers.remove(md)
        bpy.data.node_groups.remove(ng)
        return True

    @staticmethod
    def has_obs(md: Modifier, obs: set[Object]) -> bool:
        for node in md.node_group.nodes:
            if node.type == "OBJECT_INFO" and node.inputs["Object"].default_value in obs:
                return True

        return False

    @staticmethod
    def is_gn_mod(md: Modifier) -> bool:
        return md.type == "NODES" and md.node_group and "booltron" in md.node_group

    @staticmethod
    def check_mode(md: Modifier, mode: str) -> bool:
        return md.node_group["booltron"] == mode

    @staticmethod
    def bake(md: Modifier) -> None:
        if bpy.data.is_saved:
            bpy.ops.object.geometry_node_bake_single(session_uid=md.id_data.session_uid, modifier_name=md.name, bake_id=md.bakes[0].bake_id)

    @staticmethod
    def bake_del(md: Modifier) -> None:
        try:  # VER == 4.2; silence poll error message
            bpy.ops.object.geometry_node_bake_delete_single(session_uid=md.id_data.session_uid, modifier_name=md.name, bake_id=md.bakes[0].bake_id)
        except:
            pass

    @staticmethod
    def is_baked(md: Modifier) -> bool:
        return bool(md.bake_directory) and Path(bpy.path.abspath(md.bake_directory)).exists()
