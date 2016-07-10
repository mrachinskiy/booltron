import bpy
from bpy.types import Operator
from . import tools


class UNION(Operator):
	"""Combine selected objects"""
	bl_label = 'Booltron: Union'
	bl_idname = 'booltron.union'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):

		def separate_shels():
			ops_ob = bpy.ops.object
			ops_me = bpy.ops.mesh
			ops_ob.mode_set(mode='EDIT')
			ops_me.separate(type='LOOSE')
			ops_ob.mode_set(mode='OBJECT')

		tools.boolean_optimized('UNION')
		separate_shels()
		if len(bpy.context.selected_objects) != 1:
			tools.boolean_each('UNION')

		return {'FINISHED'}


class DIFFERENCE(Operator):
	"""Subtract selected objects from active object"""
	bl_label = 'Booltron: Difference'
	bl_idname = 'booltron.difference'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		tools.boolean_optimized('DIFFERENCE')
		return {'FINISHED'}


class INTERSECT(Operator):
	"""Keep the common part of all selected objects"""
	bl_label = 'Booltron: Intersect'
	bl_idname = 'booltron.intersect'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		tools.boolean_each('INTERSECT')
		return {'FINISHED'}


class SLICE(Operator):
	"""Slice active object along the volume of selected object, also hides selected object (can handle only two objects at a time)"""
	bl_label = 'Booltron: Slice'
	bl_idname = 'booltron.slice'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects) == 2

	def execute(self, context):
		scene = context.scene
		obj, ob = tools.objects_get()

		def object_duplicate(ob):
			ops_ob = bpy.ops.object
			ops_ob.select_all(action='DESELECT')
			ops_ob.select_pattern(pattern=ob.name)
			ops_ob.duplicate()
			scene.objects.active = obj
			return context.selected_objects[0]

		obj_copy = object_duplicate(obj)
		tools.modifier_boolean(obj, ob, 'DIFFERENCE', delete_not=True)
		scene.objects.active = obj_copy
		tools.modifier_boolean(obj_copy, ob, 'INTERSECT', delete_not=True)

		ob.hide = True
		self.report({'INFO'}, 'Object "%s" is hidden, use "Show Hidden" to make it visible again' % ob.name)
		return {'FINISHED'}


class SUBTRACT(Operator):
	"""Subtract selected object from active object, subtracted object won't be removed (can handle only two objects at a time)"""
	bl_label = 'Booltron: Subtract'
	bl_idname = 'booltron.subtract'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects) == 2

	def execute(self, context):
		obj, ob = tools.objects_get()
		tools.modifier_boolean(obj, ob, 'DIFFERENCE', delete_not=True)
		return {'FINISHED'}
