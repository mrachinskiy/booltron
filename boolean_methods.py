import bpy

from .mesh_utils import mesh_selection


def boolean_optimized(self):
	scene = bpy.context.scene

	obj = bpy.context.active_object
	obj.select = False
	obs = bpy.context.selected_objects
	ob = obs[0]

	if len(obs) != 1:
		scene.objects.active = ob
		bpy.ops.object.join()
		scene.objects.active = obj

	mesh_selection(self, ob, 'SELECT')
	mesh_selection(self, obj, 'DESELECT')
	boolean_mod(self, obj, ob, self.mode)
	obj.select = True


def boolean_each(self):
	obj = bpy.context.active_object
	obj.select = False
	obs = bpy.context.selected_objects

	mesh_selection(self, obj, 'DESELECT')

	for ob in obs:
		mesh_selection(self, ob, 'SELECT')
		boolean_mod(self, obj, ob, self.mode)

	obj.select = True


def boolean_mod(self, obj, ob, mode, terminate_ob=True):
	md = obj.modifiers.new('Boolean', 'BOOLEAN')
	md.show_viewport = False
	md.show_render = False
	md.operation = mode
	try:
		md.solver = self.solver
	except:
		pass
	md.object = ob
	bpy.ops.object.modifier_apply(modifier='Boolean')

	if terminate_ob:
		bpy.context.scene.objects.unlink(ob) # pre 2.78 compatiblity
		bpy.data.objects.remove(ob)
