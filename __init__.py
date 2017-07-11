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
	importlib.reload(mesh_utils)
	importlib.reload(boolean_methods)
	importlib.reload(operators)
	importlib.reload(ui)
else:
	import bpy
	from bpy.types import AddonPreferences
	from bpy.props import EnumProperty, BoolProperty, FloatProperty

	from . import ui, operators


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

		split = layout.row().split(percentage=0.15)
		split.label('Boolean Solver:')
		split.prop(self, 'solver', text='')

		if bpy.app.version < (2, 78, 0):
			split = layout.row().split(percentage=0.15)
			split.row()
			split.label('BMesh solver works only with Blender 2.78 or newer', icon='QUESTION')

		split = layout.row().split(percentage=0.15)
		split.label('Triangulate:')
		split.prop(self, 'triangulate', text='')

		split = layout.row().split(percentage=0.15)
		split.label('Correct Position:')
		split.prop(self, 'pos_correct', text='')

		split = layout.row().split(percentage=0.15)
		split.enabled = self.pos_correct
		split.label('Position Offset:')
		split.prop(self, 'pos_ofst', text='')


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


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)


if __name__ == '__main__':
	register()
