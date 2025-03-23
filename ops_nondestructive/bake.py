# SPDX-FileCopyrightText: 2014-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import BoolProperty
from bpy.types import Operator


class Bake:
    delete: bool

    def execute(self, context):
        from ..lib.modlib import ModGN

        for ob in context.selected_objects:
            for md in ob.modifiers:
                if ModGN.is_gn_mod(md):
                    if self.delete:
                        ModGN.bake_del(md)
                    else:
                        ModGN.bake(md)

        return {"FINISHED"}

    def invoke(self, context, event):
        if not bpy.data.is_saved:
            self.report({"ERROR"}, "File not saved")
            return {"CANCELLED"}

        return self.execute(context)


class OBJECT_OT_modifier_bake(Bake, Operator):
    bl_label = "Bake Modifier"
    bl_description = "Bake modifier result for selected objects"
    bl_idname = "object.booltron_modifier_bake"

    delete = False


class OBJECT_OT_modifier_bake_del(Bake, Operator):
    bl_label = "Delete Bake"
    bl_description = "Delete modifier bake for selected objects"
    bl_idname = "object.booltron_modifier_bake_del"

    delete = True


class OBJECT_OT_instance_copy(Operator):
    bl_label = "Instance Copy"
    bl_description = "Create instance mesh copy of selected objects"
    bl_idname = "object.booltron_instance_copy"
    bl_options = {"REGISTER", "UNDO"}

    use_instance: BoolProperty(
        name="As Instance",
        description="Shortcut: hold Alt when using the tool",
        options={"SKIP_SAVE"},
    )

    def execute(self, context):
        from ..lib import objectlib

        ob1 = context.object
        obs = context.selected_objects

        if ob1 is None:
            ob1 = obs[0]

        name = f"Instance {ob1.name}"

        ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
        inst_in_socket = ng.interface.new_socket("As Instance", in_out="INPUT", socket_type="NodeSocketBool")
        geo_out_socket = ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

        nodes = ng.nodes

        in_ = nodes.new("NodeGroupInput")
        in_.location.x = -600
        in_.select = False
        in_inst = in_.outputs[inst_in_socket.identifier]

        out = nodes.new("NodeGroupOutput")
        out.location.x = 200
        out.select = False

        j = nodes.new("GeometryNodeJoinGeometry")
        j.select = False

        ng.links.new(j.outputs["Geometry"], out.inputs[geo_out_socket.identifier])

        for ob in obs:
            ob_info = nodes.new("GeometryNodeObjectInfo")
            ob_info.inputs["Object"].default_value = ob
            ob_info.location.x = -400
            ob_info.select = False

            transf = nodes.new("GeometryNodeTransform")
            transf.mode = "MATRIX"
            transf.location.x = -200
            transf.select = False

            ng.links.new(in_inst, ob_info.inputs["As Instance"])
            ng.links.new(ob_info.outputs["Geometry"], transf.inputs["Geometry"])
            ng.links.new(ob_info.outputs["Transform"], transf.inputs["Transform"])
            ng.links.new(transf.outputs["Geometry"], j.inputs["Geometry"])

        me = bpy.data.meshes.new(name)
        ob = bpy.data.objects.new(name, me)
        objectlib.ob_link(ob, ob1.users_collection)
        ob.select_set(True)
        context.view_layer.objects.active = ob

        md = ob.modifiers.new(name, "NODES")
        md[inst_in_socket.identifier] = self.use_instance
        md.show_expanded = False
        md.show_group_selector = False
        md.node_group = ng

        for ob in obs:
            ob.select_set(False)

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects:
            return {"CANCELLED"}

        if event.alt:
            self.use_instance = True

        return self.execute(context)
