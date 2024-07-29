# SPDX-FileCopyrightText: 2014-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Operator


class Cache:
    clear: bool

    def execute(self, context):
        from ..lib import modlib

        ModGN = modlib.ModGN

        for ob in context.selected_objects:
            for md in ob.modifiers:
                if ModGN.is_gn_mod(md):
                    if self.clear:
                        ModGN.cache_del(md)
                    else:
                        ModGN.cache(md)

        return {"FINISHED"}

    def invoke(self, context, event):
        if not bpy.data.is_saved:
            self.report({"ERROR"}, "File not saved")
            return {"CANCELLED"}

        return self.execute(context)


class OBJECT_OT_nondestructive_cache(Cache, Operator):
    bl_label = "Cache Modifier"
    bl_description = "Cache modifier result for selected objects"
    bl_idname = "object.booltron_nondestructive_cache"

    clear = False


class OBJECT_OT_nondestructive_cache_del(Cache, Operator):
    bl_label = "Clear Cache"
    bl_description = "Clear modifier cache for selected objects"
    bl_idname = "object.booltron_nondestructive_cache_del"

    clear = True


class OBJECT_OT_nondestructive_instance_copy(Operator):
    bl_label = "Instance Copy"
    bl_description = "Create instance mesh copy of selected objects"
    bl_idname = "object.booltron_nondestructive_instance_copy"

    def execute(self, context):
        from ..lib import objectlib

        name = f"Instance {context.object.name}"
        obs = context.selected_objects

        ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
        ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

        nodes = ng.nodes

        out = nodes.new("NodeGroupOutput")
        out.location.x = 200
        out.select = False

        j = nodes.new("GeometryNodeJoinGeometry")
        j.select = False

        ng.links.new(j.outputs[0], out.inputs[0])

        for ob in obs:
            ob_info = nodes.new("GeometryNodeObjectInfo")
            ob_info.inputs[0].default_value = ob
            ob_info.location.x = -400
            ob_info.select = False

            transf = nodes.new("GeometryNodeTransform")
            transf.mode = "MATRIX"
            transf.location.x = -200
            transf.select = False

            ng.links.new(ob_info.outputs[4], transf.inputs[0])
            ng.links.new(ob_info.outputs[0], transf.inputs[4])
            ng.links.new(transf.outputs[0], j.inputs[0])

        me = bpy.data.meshes.new(name)
        ob = bpy.data.objects.new(name, me)
        objectlib.ob_link(ob, context.object.users_collection)
        ob.select_set(True)
        context.view_layer.objects.active = ob

        md = ob.modifiers.new(name, "NODES")
        md.show_expanded = False
        md.node_group = ng

        for ob in obs:
            ob.select_set(False)

        return {"FINISHED"}
