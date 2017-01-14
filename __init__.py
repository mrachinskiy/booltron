bl_info = {
	'name': 'Booltron',
	'author': 'Mikhail Rachinskiy (jewelcourses.com)',
	'version': (2000,),
	'blender': (2, 74, 0),
	'location': '3D View > Tool Shelf',
	'description': 'Super add-on for super fast booleans.',
	'wiki_url': 'https://github.com/mrachinskiy/booltron#readme',
	'tracker_url': 'https://github.com/mrachinskiy/booltron/issues',
	'category': 'Object',
	}


if 'bpy' in locals():
	import importlib
	importlib.reload(ui)
	importlib.reload(operators)
else:
	import bpy
	from bpy.types import AddonPreferences
	from bpy.props import (
		EnumProperty,
		BoolProperty,
		)
	from . import (
		ui,
		operators,
		)


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
		layout = self.layout
		split = layout.split(percentage=0.15)

		col = split.column()
		col.label('Boolean Solver:')
		col.label('Triangulate:')

		col = split.column()
		colrow = col.row()
		colrow.alignment = 'LEFT'
		colrow.prop(self, 'solver', text='')
		if bpy.app.version < (2, 78, 0):
			colrow.label('BMesh solver works only with Blender 2.78 or later', icon='QUESTION')
		col.prop(self, 'triangulate', text='')


classes = (
	Preferences,

	ui.Options,
	ui.Tools,

	operators.UNION,
	operators.DIFFERENCE,
	operators.INTERSECT,
	operators.SUBTRACT,
	)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)


if __name__ == '__main__':
	register()
