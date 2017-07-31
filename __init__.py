bl_info = {
	'name': 'Booltron',
	'author': 'Mikhail Rachinskiy (jewelcourses.com)',
	'version': [2000],
	'blender': (2, 74, 0),
	'location': '3D View > Tool Shelf',
	'description': 'Super add-on for super fast booleans.',
	'wiki_url': 'https://github.com/mrachinskiy/booltron#readme',
	'tracker_url': 'https://github.com/mrachinskiy/booltron/issues',
	'category': 'Object',
	}


if 'bpy' in locals():
	import importlib
	importlib.reload(locale)
	importlib.reload(mesh_utils)
	importlib.reload(boolean_methods)
	importlib.reload(operators)
	importlib.reload(ui)
else:
	import bpy
	from bpy.types import AddonPreferences
	from bpy.props import EnumProperty, BoolProperty, FloatProperty
	from bpy.app.translations import pgettext_iface as _

	from . import ui, operators, locale


class Preferences(AddonPreferences):
	bl_idname = __package__

	solver = EnumProperty(
		name='Boolean Solver',
		description='Specify solver for boolean operations',
		items=(('BMESH', 'BMesh', 'BMesh solver is faster, but less stable and cannot handle coplanar geometry'),
		       ('CARVE', 'Carve', 'Carve solver is slower, but more stable and can handle simple cases of coplanar geometry')),
		default='BMESH',
		)
	triangulate = BoolProperty(
		name='Triangulate',
		description='Triangulate geometry before boolean operation (can sometimes improve result of a boolean operation)',
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

	def draw(self, context):
		layout = self.layout

		split = layout.split(percentage=0.15)
		split.label(_('Boolean Solver') + ':')

		col = split.column()
		col.prop(self, 'solver', text='')

		if bpy.app.version < (2, 78, 0):
			col.label('BMesh solver works only with Blender 2.78 or newer', icon='QUESTION')

		split = layout.split(percentage=0.15)
		split.label(_('Adjustments') + ':')

		col = split.column()
		col.prop(self, 'triangulate')
		col.prop(self, 'pos_correct')

		row = col.row()
		row.enabled = self.pos_correct
		row.prop(self, 'pos_ofst')


classes = (
	Preferences,

	ui.Options,
	ui.Tools,

	operators.Union,
	operators.Difference,
	operators.Intersect,
	operators.Slice,
	operators.Subtract,
	)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.app.translations.register(__name__, locale.lc_reg)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	bpy.app.translations.unregister(__name__)


if __name__ == '__main__':
	register()
