import bpy
from bpy.types import Operator
from . import helpers


class UNION(Operator):
	'''Combine objects in an additive way'''
	bl_idname = "booltron.union"
	bl_label = "Booltron: Union"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		helpers.union()
		return {'FINISHED'}


class DIFFERENCE(Operator):
	'''Combine objects in a subtractive way'''
	bl_idname = "booltron.difference"
	bl_label = "Booltron: Difference"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		helpers.difference()
		return {'FINISHED'}


class INTERSECT(Operator):
	'''Keep geometry that intersects with each other'''
	bl_idname = "booltron.intersect"
	bl_label = "Booltron: Intersect"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		helpers.intersect()
		return {'FINISHED'}


class SEPARATE(Operator):
	'''Separate active object along the intersection of the selected object (can handle only two objects at the time)'''
	bl_idname = "booltron.separate"
	bl_label = "Booltron: Separate"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects) == 2

	def execute(self, context):
		helpers.separate()
		return {'FINISHED'}
