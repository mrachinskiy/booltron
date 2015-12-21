import bpy
from bpy.types import Operator
from . import helpers


class UNION(Operator):
	'''Performes a boolean union operation'''
	bl_idname = "booltron.union"
	bl_label = "Booltron: Union"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		helpers.union()
		return {'FINISHED'}


class DIFFERENCE(Operator):
	'''Performes a boolean difference operation'''
	bl_idname = "booltron.difference"
	bl_label = "Booltron: Difference"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		helpers.difference()
		return {'FINISHED'}


class INTERSECT(Operator):
	'''Performes a boolean intersect operation'''
	bl_idname = "booltron.intersect"
	bl_label = "Booltron: Intersect"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		helpers.intersect()
		return {'FINISHED'}


class SEPARATE(Operator):
	'''Separates the active object along the intersection of the selected object (can handle only two objects at the time)'''
	bl_idname = "booltron.separate"
	bl_label = "Booltron: Separate"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects) == 2

	def execute(self, context):
		helpers.separate()
		return {'FINISHED'}
