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
	from bpy.props import EnumProperty, BoolProperty

	from . import ui, operators


class Preferences(AddonPreferences):
	bl_idname = __package__

	solver = EnumProperty(
		name='Boolean Solver',
		items=(('BMESH', 'BMesh', 'BMesh solver is faster, but less stable and cannot handle coplanar geometry'),
		       ('CARVE', 'Carve', 'Carve solver is slower, but more stable and can handle simple cases of coplanar geometry')),
		default='BMESH',
		description='Specify solver for boolean operations',
		)
	triangulate = BoolProperty(
		name='Triangulate',
		description='Triangulate geometry before boolean operation (can sometimes improve result of a boolean operation)',
		)

	def draw(self, context):
		col = self.layout.column()

		split = col.row().split(percentage=0.15)
		split.label('Boolean Solver:')
		row = split.row()
		row.alignment = 'LEFT'
		row.prop(self, 'solver', text='')
		if bpy.app.version < (2, 78, 0):
			row.label('BMesh solver works only with Blender 2.78 or later', icon='QUESTION')

		split = col.row().split(percentage=0.15)
		split.label('Triangulate:')
		split.prop(self, 'triangulate', text='')


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
