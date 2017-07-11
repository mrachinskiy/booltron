import random

import bpy
import bmesh
from mathutils import Vector


def objects_prepare(self):
	bpy.ops.object.make_single_user(object=True, obdata=True)
	bpy.ops.object.convert(target='MESH')
	bpy.ops.object.transform_apply(scale=True)

	if self.pos_correct:
		obj = bpy.context.active_object
		obj.select = False

		for ob in bpy.context.selected_objects:
			x = random.uniform(-self.pos_ofst, self.pos_ofst)
			y = random.uniform(-self.pos_ofst, self.pos_ofst)
			z = random.uniform(-self.pos_ofst, self.pos_ofst)

			ob.location += Vector((x, y, z))

		obj.select = True


def is_manifold(self):
	me = bpy.context.active_object.data
	bm = bmesh.new()
	bm.from_mesh(me)

	for edge in bm.edges:
		if not edge.is_manifold:
			bm.free()
			self.report({'ERROR'}, 'Boolean operation result is non-manifold')
			return False

	bm.free()
	return True


def mesh_selection(self, ob, select_action):
	scene = bpy.context.scene
	ops_me = bpy.ops.mesh

	active_object = bpy.context.active_object
	scene.objects.active = ob
	bpy.ops.object.mode_set(mode='EDIT')

	ops_me.reveal()

	ops_me.select_all(action='SELECT')
	ops_me.delete_loose()

	ops_me.select_all(action='SELECT')
	ops_me.remove_doubles(threshold=0.0001)

	ops_me.select_all(action='SELECT')
	ops_me.fill_holes(sides=0)

	if self.triangulate:
		ops_me.select_all(action='SELECT')
		ops_me.quads_convert_to_tris()

	ops_me.select_all(action=select_action)

	bpy.ops.object.mode_set(mode='OBJECT')
	scene.objects.active = active_object
