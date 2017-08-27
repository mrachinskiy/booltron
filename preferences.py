import bpy
from bpy.types import AddonPreferences
from bpy.props import EnumProperty, BoolProperty, FloatProperty, IntProperty

# Extern
from . import addon_updater_ops


class Operator_Props:
	"""Unified add-on and operator settings"""

	solver = EnumProperty(
		name='Boolean Solver',
		description='Specify solver for boolean operations',
		items=(('BMESH', 'BMesh', 'BMesh solver is faster, but less stable and cannot handle coplanar geometry'),
		       ('CARVE', 'Carve', 'Carve solver is slower, but more stable and can handle simple cases of coplanar geometry')),
		default='BMESH',
		)
	method = EnumProperty(
		name='Boolean Method',
		description='Specify boolean method for Union, Difference and Intersect tools (Intersect tool does not support optimized method and will use batch method instead)',
		items=(('OPTIMIZED', 'Optimized', 'A single boolean operation with all objects at once, fastest, but in certain cases gives unpredictable result'),
		       ('BATCH', 'Batch', 'Boolean operation for each selected object one by one, much slower, but overall gives more predictable result'),
		       ('BATCH_CLEANUP', 'Batch + Mesh Cleanup', 'Perform mesh cleanup operation in between boolean operations, slowest, but gives better result in cases where simple batch method fails')),
		default='OPTIMIZED',
		)
	triangulate = BoolProperty(
		name='Triangulate',
		description='Triangulate geometry before boolean operation (in certain cases may improve result of a boolean operation)',
		)
	pos_correct = BoolProperty(
		name='Correct Position',
		description='Shift objects position for a very small amount to avoid coplanar geometry errors during boolean operation (does not affect active object)',
		)
	pos_ofst = FloatProperty(
		name='Position Offset',
		description='Position offset is randomly generated for each object in range [-x, +x] input value',
		default=0.005,
		min=0.0,
		step=0.1,
		precision=3,
		)


class Booltron_Preferences(AddonPreferences, Operator_Props):
	bl_idname = __package__

	"""
	Updater settings
	"""

	auto_check_update = BoolProperty(
		name='Auto-check for Update',
		description='If enabled, auto-check for updates using an interval',
		default=True,
		)
	updater_intrval_months = IntProperty(
		name='Months',
		description='Number of months between checking for updates',
		default=0,
		min=0,
		)
	updater_intrval_days = IntProperty(
		name='Days',
		description='Number of days between checking for updates',
		default=7,
		min=0,
		)
	updater_intrval_hours = IntProperty(
		name='Hours',
		description='Number of hours between checking for updates',
		default=0,
		min=0,
		max=23,
		)
	updater_intrval_minutes = IntProperty(
		name='Minutes',
		description='Number of minutes between checking for updates',
		default=0,
		min=0,
		max=59,
		)

	def draw(self, context):
		layout = self.layout

		split = layout.split(percentage=0.2)
		split.label('Boolean Solver:')

		col = split.column()
		col.prop(self, 'solver', text='')

		if bpy.app.version < (2, 78, 0):
			col.label('BMesh solver works only with Blender 2.78 or newer', icon='QUESTION')

		split = layout.split(percentage=0.2)
		split.label('Boolean Method:')
		split.prop(self, 'method', text='')

		split = layout.split(percentage=0.2)
		split.label('Adjustments:')

		col = split.column()
		col.prop(self, 'triangulate')
		col.prop(self, 'pos_correct')

		row = col.row()
		row.enabled = self.pos_correct
		row.prop(self, 'pos_ofst')

		layout.separator()

		addon_updater_ops.update_settings_ui(self, context)
