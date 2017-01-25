import bpy
import bmesh
from bpy.types import Operator
from bpy.props import (
	EnumProperty,
	BoolProperty,
	)


"""
Cannot inherit properties from a base class,
because property order will be random every time in operator redo UI
"""
_solver = EnumProperty(
	name='Boolean Solver',
	items=(('BMESH', 'BMesh', 'BMesh solver is faster, but less stable and cannot handle coplanar geometry'),
	       ('CARVE', 'Carve', 'Carve solver is slower, but more stable and can handle simple cases of coplanar geometry')),
	description='Specify solver for boolean operation',
	options={'SKIP_SAVE'},
	)
_triangulate = BoolProperty(
	name='Triangulate',
	description='Triangulate geometry before boolean operation (can sometimes improve result of a boolean operation)',
	options={'SKIP_SAVE'},
	)


class Mesh:

	def objects_prepare(self):
		bpy.ops.object.make_single_user(object=True, obdata=True)
		bpy.ops.object.convert(target='MESH')

	def is_manifold(self):
		me = self.context.active_object.data
		bm = bmesh.new()
		bm.from_mesh(me)

		for edge in bm.edges:
			if not edge.is_manifold:
				bm.free()
				self.report({'WARNING'}, 'Boolean operation result is non-manifold')
				return False

		bm.free()
		return True

	def mesh_selection(self, ob, select_action):
		scene = self.context.scene
		obj = self.context.active_object
		ops_me = bpy.ops.mesh
		ops_ob = bpy.ops.object

		def mesh_cleanup():
			ops_me.select_all(action='SELECT')
			ops_me.delete_loose()
			ops_me.select_all(action='SELECT')
			ops_me.remove_doubles(threshold=0.0001)
			ops_me.fill_holes(sides=0)
			if self.triangulate:
				ops_me.quads_convert_to_tris()

		scene.objects.active = ob
		ops_ob.mode_set(mode='EDIT')

		mesh_cleanup()
		ops_me.select_all(action=select_action)

		ops_ob.mode_set(mode='OBJECT')
		scene.objects.active = obj


class Booleans(Mesh):
	bl_options = {'REGISTER', 'UNDO'}

	def __init__(self):
		self.context = bpy.context
		prefs = self.context.user_preferences.addons[__package__].preferences
		self.solver = prefs.solver
		self.triangulate = prefs.triangulate

	def boolean_optimized(self):
		scene = self.context.scene
		obj = self.context.active_object

		obj.select = False
		obs = self.context.selected_objects
		ob = obs[0]

		if len(obs) != 1:
			scene.objects.active = ob
			bpy.ops.object.join()
			scene.objects.active = obj

		self.mesh_selection(obj, 'DESELECT')
		self.mesh_selection(ob, 'SELECT')
		self.boolean_mod(obj, ob, self.mode)
		obj.select = True

	def boolean_each(self):
		obj = self.context.active_object

		obj.select = False
		obs = self.context.selected_objects

		self.mesh_selection(obj, 'DESELECT')
		for ob in obs:
			self.mesh_selection(ob, 'SELECT')
			self.boolean_mod(obj, ob, self.mode)
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
			self.context.scene.objects.unlink(ob) # pre 2.78 compatiblity
			bpy.data.objects.remove(ob)


class UNION(Booleans, Operator):
	"""Combine selected objects"""
	bl_label = 'Booltron Union'
	bl_idname = 'object.booltron_union'

	solver = _solver
	triangulate = _triangulate
	mode = 'UNION'

	def execute(self, context):

		def separate_shels():
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.separate(type='LOOSE')
			bpy.ops.object.mode_set(mode='OBJECT')

		self.objects_prepare()

		self.boolean_optimized()
		is_manifold = self.is_manifold()

		if is_manifold:
			separate_shels()
			if len(context.selected_objects) != 1:
				self.boolean_each()
				self.is_manifold()

		return {'FINISHED'}


class DIFFERENCE(Booleans, Operator):
	"""Subtract selected objects from active object"""
	bl_label = 'Booltron Difference'
	bl_idname = 'object.booltron_difference'

	solver = _solver
	triangulate = _triangulate
	mode = 'DIFFERENCE'

	def execute(self, context):
		self.objects_prepare()

		self.boolean_optimized()
		self.is_manifold()

		return {'FINISHED'}


class INTERSECT(Booleans, Operator):
	"""Keep the common part of all selected objects"""
	bl_label = 'Booltron Intersect'
	bl_idname = 'object.booltron_intersect'

	solver = _solver
	triangulate = _triangulate
	mode = 'INTERSECT'

	def execute(self, context):
		self.objects_prepare()

		self.boolean_each()
		self.is_manifold()

		return {'FINISHED'}


class SLICE(Booleans, Operator):
	"""Slice active object along the volume of selected object"""
	bl_label = 'Booltron Slice'
	bl_idname = 'object.booltron_slice'

	solver = _solver
	triangulate = _triangulate

	def execute(self, context):
		self.objects_prepare()

		scene = context.scene
		obj = context.active_object
		obj.select = False
		ob = context.selected_objects[0]

		self.mesh_selection(obj, 'DESELECT')
		self.mesh_selection(ob, 'SELECT')

		obj_copy = obj.copy()
		obj_copy.data = obj.data.copy()
		scene.objects.link(obj_copy)

		self.boolean_mod(obj, ob, 'DIFFERENCE', terminate_ob=False)
		is_manifold = self.is_manifold()

		if is_manifold:
			scene.objects.active = obj_copy
			self.boolean_mod(obj_copy, ob, 'INTERSECT')
			obj_copy.select = True
			self.is_manifold()

		return {'FINISHED'}


class SUBTRACT(Booleans, Operator):
	"""Subtract selected object from active object, subtracted object won't be removed"""
	bl_label = 'Booltron Subtract'
	bl_idname = 'object.booltron_subtract'

	solver = _solver
	triangulate = _triangulate

	def execute(self, context):
		self.objects_prepare()

		obj = context.active_object
		obj.select = False
		ob = context.selected_objects[0]

		self.mesh_selection(obj, 'DESELECT')
		self.mesh_selection(ob, 'SELECT')

		self.boolean_mod(obj, ob, 'DIFFERENCE', terminate_ob=False)
		self.is_manifold()

		return {'FINISHED'}
