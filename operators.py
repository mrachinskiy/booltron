import bpy
from bpy.types import Operator
from bpy.props import EnumProperty


class Booleans:
	bl_options = {'REGISTER', 'UNDO'}

	solver = EnumProperty(
		name='Boolean Solver',
		items=(('BMESH', 'BMesh', ''),
		       ('CARVE', 'Carve', '')),
		description='Specify solver for boolean operation',
		options={'SKIP_SAVE'})

	def __init__(self):
		self.context = bpy.context
		self.solver = self.context.user_preferences.addons[__package__].preferences.solver

	def boolean_optimized(self):
		scene = self.context.scene
		obj = self.context.active_object

		prepare_objects()

		obj.select = False
		obs = self.context.selected_objects
		ob = obs[0]

		if len(obs) != 1:
			scene.objects.active = ob
			bpy.ops.object.join()
			scene.objects.active = obj

		mesh_selection(obj, 'DESELECT')
		mesh_selection(ob, 'SELECT')
		self.boolean_mod(obj, ob, self.mode)
		obj.select = True

	def boolean_each(self):
		obj = self.context.active_object

		prepare_objects()

		obj.select = False
		obs = self.context.selected_objects

		mesh_selection(obj, 'DESELECT')
		for ob in obs:
			mesh_selection(ob, 'SELECT')
			self.boolean_mod(obj, ob, self.mode)
		obj.select = True

	def boolean_mod(self, obj, ob, mode, terminate=True):
		md = obj.modifiers.new('Immediate apply', 'BOOLEAN')
		md.show_viewport = False
		md.show_render = False
		md.operation = mode
		try:
			md.solver = self.solver
		except:
			pass
		md.object = ob

		bpy.ops.object.modifier_apply(modifier='Immediate apply')
		if not terminate:
			return
		self.context.scene.objects.unlink(ob)
		bpy.data.objects.remove(ob)


class UNION(Booleans, Operator):
	"""Combine selected objects"""
	bl_label = 'Union'
	bl_idname = 'booltron.union'

	mode = 'UNION'

	def execute(self, context):

		def separate_shels():
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.separate(type='LOOSE')
			bpy.ops.object.mode_set(mode='OBJECT')

		if self.solver == 'CARVE':
			self.boolean_optimized()
			separate_shels()
			if len(context.selected_objects) != 1:
				self.boolean_each()
		else:
			self.boolean_each()

		return {'FINISHED'}


class DIFFERENCE(Booleans, Operator):
	"""Subtract selected objects from active object"""
	bl_label = 'Difference'
	bl_idname = 'booltron.difference'

	mode = 'DIFFERENCE'

	def execute(self, context):
		if self.solver == 'CARVE':
			self.boolean_optimized()
		else:
			self.boolean_each()
		return {'FINISHED'}


class INTERSECT(Booleans, Operator):
	"""Keep the common part of all selected objects"""
	bl_label = 'Intersect'
	bl_idname = 'booltron.intersect'

	mode = 'INTERSECT'

	def execute(self, context):
		self.boolean_each()
		return {'FINISHED'}


class SLICE(Booleans, Operator):
	"""Slice active object along the volume of selected object, also hides selected object (can handle only two objects at a time)"""
	bl_label = 'Slice'
	bl_idname = 'booltron.slice'

	def execute(self, context):
		scene = context.scene
		obj, ob = get_objects(context)

		def object_duplicate(ob):
			bpy.ops.object.select_all(action='DESELECT')
			bpy.ops.object.select_pattern(pattern=ob.name)
			bpy.ops.object.duplicate()
			scene.objects.active = obj
			return context.selected_objects[0]

		obj_copy = object_duplicate(obj)
		self.boolean_mod(obj, ob, 'DIFFERENCE', terminate=False)
		scene.objects.active = obj_copy
		self.boolean_mod(obj_copy, ob, 'INTERSECT', terminate=False)

		ob.hide = True
		self.report({'INFO'}, 'Object "%s" is hidden, use "Show Hidden" to make it visible again' % ob.name)
		return {'FINISHED'}


class SUBTRACT(Booleans, Operator):
	"""Subtract selected object from active object, subtracted object won't be removed (can handle only two objects at a time)"""
	bl_label = 'Subtract'
	bl_idname = 'booltron.subtract'

	def execute(self, context):
		obj, ob = get_objects(context)
		self.boolean_mod(obj, ob, 'DIFFERENCE', terminate=False)
		return {'FINISHED'}


def prepare_objects():
	bpy.ops.object.make_single_user(object=True, obdata=True)
	bpy.ops.object.convert(target='MESH')


def mesh_selection(ob, select_action):
	context = bpy.context
	scene = context.scene
	obj = context.active_object
	ops_me = bpy.ops.mesh
	ops_ob = bpy.ops.object

	def mesh_cleanup():
		ops_me.select_all(action='SELECT')
		ops_me.delete_loose()
		ops_me.select_all(action='SELECT')
		ops_me.remove_doubles(threshold=0.0001)
		ops_me.fill_holes(sides=0)
		ops_me.normals_make_consistent()

	scene.objects.active = ob
	ops_ob.mode_set(mode='EDIT')

	mesh_cleanup()
	ops_me.select_all(action=select_action)

	ops_ob.mode_set(mode='OBJECT')
	scene.objects.active = obj


def get_objects(context):
	obj = context.active_object

	prepare_objects()

	obj.select = False
	ob = context.selected_objects[0]

	mesh_selection(obj, 'DESELECT')
	mesh_selection(ob, 'SELECT')

	return obj, ob
