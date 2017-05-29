import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty

from .boolean_methods import boolean_optimized, boolean_each, boolean_mod
from .mesh_utils import objects_prepare, is_manifold, mesh_selection


class Setup:

	solver = EnumProperty(
		name='Boolean Solver',
		items=(('BMESH', 'BMesh', 'BMesh solver is faster, but less stable and cannot handle coplanar geometry'),
		       ('CARVE', 'Carve', 'Carve solver is slower, but more stable and can handle simple cases of coplanar geometry')),
		description='Specify solver for boolean operation',
		options={'SKIP_SAVE'},
		)
	triangulate = BoolProperty(
		name='Triangulate',
		description='Triangulate geometry before boolean operation (can sometimes improve result of a boolean operation)',
		options={'SKIP_SAVE'},
		)

	def __init__(self):
		prefs = bpy.context.user_preferences.addons[__package__].preferences
		self.solver = prefs.solver
		self.triangulate = prefs.triangulate

	def draw(self, context):
		layout = self.layout

		split = layout.row().split()
		split.label('Boolean Solver')
		split.prop(self, 'solver', text='')

		split = layout.row().split()
		split.label('Triangulate')
		split.prop(self, 'triangulate', text='')


class Union(Setup, Operator):
	"""Combine selected objects"""
	bl_label = 'Booltron Union'
	bl_idname = 'object.booltron_union'
	bl_options = {'REGISTER', 'UNDO'}

	mode = 'UNION'

	def execute(self, context):
		objects_prepare()

		boolean_optimized(self)
		manifold = is_manifold(self)

		if manifold:
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.separate(type='LOOSE')
			bpy.ops.object.mode_set(mode='OBJECT')

			if len(context.selected_objects) != 1:
				boolean_each(self)
				is_manifold(self)

		return {'FINISHED'}


class Difference(Setup, Operator):
	"""Subtract selected objects from active object"""
	bl_label = 'Booltron Difference'
	bl_idname = 'object.booltron_difference'
	bl_options = {'REGISTER', 'UNDO'}

	mode = 'DIFFERENCE'

	def execute(self, context):
		objects_prepare()

		boolean_optimized(self)
		is_manifold(self)

		return {'FINISHED'}


class Intersect(Setup, Operator):
	"""Keep the common part of all selected objects"""
	bl_label = 'Booltron Intersect'
	bl_idname = 'object.booltron_intersect'
	bl_options = {'REGISTER', 'UNDO'}

	mode = 'INTERSECT'

	def execute(self, context):
		objects_prepare()

		boolean_each(self)
		is_manifold(self)

		return {'FINISHED'}


class Slice(Setup, Operator):
	"""Slice active object along the volume of selected object"""
	bl_label = 'Booltron Slice'
	bl_idname = 'object.booltron_slice'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		objects_prepare()

		scene = context.scene
		obj = context.active_object
		obj.select = False
		ob = context.selected_objects[0]

		mesh_selection(self, obj, 'DESELECT')
		mesh_selection(self, ob, 'SELECT')

		obj_copy = obj.copy()
		obj_copy.data = obj.data.copy()
		scene.objects.link(obj_copy)

		boolean_mod(self, obj, ob, 'DIFFERENCE', terminate_ob=False)
		manifold = is_manifold(self)

		if manifold:
			scene.objects.active = obj_copy
			boolean_mod(self, obj_copy, ob, 'INTERSECT')
			obj_copy.select = True
			is_manifold(self)

		return {'FINISHED'}


class Subtract(Setup, Operator):
	"""Subtract selected object from active object, subtracted object won't be removed"""
	bl_label = 'Booltron Subtract'
	bl_idname = 'object.booltron_subtract'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		objects_prepare()

		obj = context.active_object
		obj.select = False
		ob = context.selected_objects[0]

		mesh_selection(self, obj, 'DESELECT')
		mesh_selection(self, ob, 'SELECT')

		boolean_mod(self, obj, ob, 'DIFFERENCE', terminate_ob=False)
		is_manifold(self)

		return {'FINISHED'}
