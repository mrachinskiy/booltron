# SPDX-FileCopyrightText: 2014-2026 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import bpy
from bpy.types import GeometryNode, Modifier, NodeGroup, NodeSocket, NodeSocketGeometry, Object

from .. import var


def disable_mods(value: bool) -> None:
    for ob in bpy.context.scene.objects:
        if ob.type == "MESH":
            for md in ob.modifiers:
                if md.type == "BOOLEAN" or ModGN.is_gn_mod(md):
                    md.show_viewport = value


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


class ModGN:
    __slots__ = (
        "mode",
        "solver",
        "use_self",
        "use_hole_tolerant",
        "solver_secondary",
        "use_self_secondary",
        "use_hole_tolerant_secondary",
        "merge_distance",
        "use_loc_rnd",
        "loc_offset",
        "seed",
    )

    def __init__(self, mode: str, settings: dict[str, str | float | bool]) -> None:
        self.mode = mode

        for prop in self.__slots__[1:]:
            setattr(self, prop, settings.get(prop))

    def add(self, ob1: Object, obs: list[Object], md: Modifier | None = None, show_viewport: bool = True) -> Modifier:
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
        sock_seed.force_non_field = True

        nodes = ng.nodes

        in_ = nodes.new("NodeGroupInput")
        in_.location.x = -200
        in_.select = False
        in_geo = in_.outputs[sock_geo_in.identifier]
        in_ofst = in_.outputs[sock_ofst.identifier]
        in_seed = in_.outputs[sock_seed.identifier]

        if ob1.type != "MESH":
            in_.location.x = -400

            weld = nodes.new("GeometryNodeMergeByDistance")
            weld.inputs["Distance"].default_value = self.merge_distance
            weld.location.x = -200
            weld.select = False

            ng.links.new(in_geo, weld.inputs["Geometry"])
            in_geo = weld.outputs["Geometry"]

        out = nodes.new("NodeGroupOutput")
        out.location.x = 600
        out.select = False
        out_geo = out.inputs[sock_geo_out.identifier]

        bake = nodes.new("GeometryNodeBake")
        bake.location.x = 400
        bake.select = False
        bake.bake_items.clear()  # VER < 5.0
        bake.bake_items.new("GEOMETRY", "Geometry")

        ng.links.new(bake.outputs["Geometry"], out_geo)

        primary = nodes.new("GeometryNodeMeshBoolean")
        primary.name = "PRIMARY"
        primary.operation = self.mode
        primary.solver = self.solver
        if self.solver == "EXACT":
            primary.inputs["Self Intersection"].default_value = self.use_self
            primary.inputs["Hole Tolerant"].default_value = self.use_hole_tolerant
        primary.select = False

        ng.links.new(in_geo, primary.inputs["Mesh 1" if self.mode == "DIFFERENCE" else "Mesh 2"])

        panel_attr = ng.interface.new_panel("Attributes", default_closed=True)
        sock_attr_name = ng.interface.new_socket("Intersecting Edges", description="Mark intersecting edges", in_out="INPUT", socket_type="NodeSocketString", parent=panel_attr)

        if self.solver == "FLOAT":
            str_len = nodes.new("FunctionNodeStringLength")
            str_len.location.y = 130
            str_len.select = False

            warn = nodes.new("GeometryNodeWarning")
            warn.warning_type = "WARNING"
            warn.inputs["Message"].default_value = "Float solver does not support attributes"
            warn.location = 200, 130
            warn.select = False

            ng.links.new(primary.outputs["Mesh"], bake.inputs["Geometry"])
            ng.links.new(str_len.outputs["Length"], warn.inputs["Show"])
            ng.links.new(in_.outputs[sock_attr_name.identifier], str_len.inputs["String"])
        else:
            attr = nodes.new("GeometryNodeStoreNamedAttribute")
            attr.data_type = "BOOLEAN"
            attr.domain = "EDGE"
            attr.inputs["Value"].default_value = True
            attr.location.x = 200
            attr.select = False

            ng.links.new(primary.outputs["Mesh"], attr.inputs["Geometry"])
            ng.links.new(primary.outputs["Intersecting Edges"], attr.inputs["Selection"])
            ng.links.new(in_.outputs[sock_attr_name.identifier], attr.inputs["Name"])
            ng.links.new(attr.outputs["Geometry"], bake.inputs["Geometry"])

        secondary = nodes.new("GeometryNodeMeshBoolean")
        secondary.name = "SECONDARY"
        secondary.operation = "UNION"
        secondary.solver = self.solver_secondary
        if self.solver_secondary == "EXACT":
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

        if (is_md_new := not md):
            md = ob1.modifiers.new(self.mode.title(), "NODES")
            md.show_viewport = show_viewport
            md.show_in_editmode = False
            md.show_expanded = False

        md.show_group_selector = False

        if self.use_loc_rnd:
            md[sock_ofst.identifier] = self.loc_offset
            md[sock_seed.identifier] = self.seed

        md.node_group = ng
        md.bake_target = "DISK"

        if is_md_new:
            prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
            self.md_input_set(md, sock_attr_name.identifier, prefs.attribute_edge_intersect)

        return md

    def add_and_apply(self, ob1: Object, obs: list[Object], remove_obs: bool = True) -> None:
        md = self.add(ob1, obs, show_viewport=False)
        ng = md.node_group

        with bpy.context.temp_override(object=ob1):
            bpy.ops.object.modifier_apply(modifier=md.name)

        bpy.data.node_groups.remove(ng)

        if remove_obs:
            for ob in obs:
                bpy.data.meshes.remove(ob.data)

    def extend(self, md: Modifier, obs: list[Object]) -> None:
        show_viewport = md.show_viewport
        md.show_viewport = False

        ng = md.node_group
        nodes = ng.nodes

        ng_obs = set()
        for node in nodes:
            if node.type == "OBJECT_INFO" and (ob := node.inputs["Object"].default_value):
                ng_obs.add(ob)
        ng_obs.update(obs)

        bpy.data.node_groups.remove(ng)
        self.add(md.id_data, ng_obs, md=md)

        md.show_viewport = show_viewport

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

        rnd = nodes.new("GeometryNodeGroup")
        rnd.node_tree = _rnd_loc()
        rnd.location = -200, node.location.y
        rnd.select = False

        node_add = nodes.new("FunctionNodeIntegerMath")
        node_add.inputs["Value_001"].default_value = seed
        node_add.location = -200, node.location.y - 155
        node_add.hide = True
        node_add.select = False

        ng.links.new(in_seed, node_add.inputs["Value"])
        ng.links.new(node_add.outputs["Value"], rnd.inputs["Seed"])
        ng.links.new(in_ofst, rnd.inputs["Offset"])
        ng.links.new(node.outputs["Geometry"], rnd.inputs["Geometry"])

        return rnd.outputs["Geometry"]

    @staticmethod
    def remove(md: Modifier, obs: set[Object]) -> bool:
        show_viewport = md.show_viewport
        md.show_viewport = False
        nodes = md.node_group.nodes
        has_obs = False

        for link in nodes["SECONDARY"].inputs["Mesh 2"].links:
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
            md.show_viewport = show_viewport
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
        bpy.ops.object.geometry_node_bake_delete_single(session_uid=md.id_data.session_uid, modifier_name=md.name, bake_id=md.bakes[0].bake_id)

    @staticmethod
    def is_baked(md: Modifier) -> bool:
        return bool(md.bake_directory) and Path(bpy.path.abspath(md.bake_directory)).exists()

    @staticmethod
    def md_input_set(md: Modifier, prop: str, value: Any) -> None:
        if hasattr(md, "properties"):  # VER >= 5.2
            getattr(md.properties.inputs, prop).value = value
        else:
            md[prop] = value


def _rnd_loc() -> NodeGroup:
    name = ".booltron_rnd_loc"

    if (ng := bpy.data.node_groups.get(name)) is not None:
        return ng

    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.color_tag = "GEOMETRY"

    sock_geo_in = ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    sock_geo_out = ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

    sock_ofst = ng.interface.new_socket("Offset", in_out="INPUT", socket_type="NodeSocketFloat")
    sock_ofst.subtype = "DISTANCE"
    sock_ofst.min_value = 0.0
    sock_ofst.force_non_field = True
    sock_seed = ng.interface.new_socket("Seed", in_out="INPUT", socket_type="NodeSocketInt")
    sock_seed.force_non_field = True

    nodes = ng.nodes

    in_ = nodes.new("NodeGroupInput")
    in_.location.x = -200
    in_.select = False
    in_geo = in_.outputs[sock_geo_in.identifier]
    in_ofst = in_.outputs[sock_ofst.identifier]
    in_seed = in_.outputs[sock_seed.identifier]

    out = nodes.new("NodeGroupOutput")
    out.location.x = 600
    out.select = False
    out_geo = out.inputs[sock_geo_out.identifier]

    sw = nodes.new("GeometryNodeSwitch")
    sw.input_type = "GEOMETRY"
    sw.location.x = 400
    sw.select = False

    ng.links.new(sw.outputs["Output"], out_geo)
    ng.links.new(in_geo, sw.inputs["False"])

    eq = nodes.new("FunctionNodeCompare")
    eq.data_type = "FLOAT"
    eq.operation = "GREATER_THAN"
    eq.location = 200, 100
    eq.select = False

    ng.links.new(eq.outputs["Result"], sw.inputs["Switch"])
    ng.links.new(in_ofst, eq.inputs["A"])

    trfm = nodes.new("GeometryNodeTransform")
    trfm.location = 200, -200
    trfm.select = False
    if "Mode" in trfm.inputs:  # VER < 5.0
        trfm.inputs["Mode"].default_value = "Components"

    ng.links.new(in_geo, trfm.inputs["Geometry"])
    ng.links.new(trfm.outputs["Geometry"], sw.inputs["True"])

    rnd = nodes.new("FunctionNodeRandomValue")
    rnd.data_type = "FLOAT_VECTOR"
    rnd.location.y = -200
    rnd.select = False

    ng.links.new(rnd.outputs["Value"], trfm.inputs["Translation"])
    ng.links.new(in_ofst, rnd.inputs["Max"])
    ng.links.new(in_seed, rnd.inputs["Seed"])

    const_int = nodes.new("FunctionNodeInputInt")
    const_int.location = -200, -400
    const_int.select = False

    ng.links.new(const_int.outputs["Integer"], rnd.inputs["ID"])

    flip_sign = nodes.new("ShaderNodeMath")
    flip_sign.operation = "MULTIPLY"
    flip_sign.location = -200, -200
    flip_sign.select = False
    flip_sign.inputs["Value_001"].default_value = -1.0

    ng.links.new(flip_sign.outputs["Value"], rnd.inputs["Min"])
    ng.links.new(in_ofst, flip_sign.inputs["Value"])

    return ng
