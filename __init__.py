bl_info = {
	'name': 'Booltron',
	'author': 'Mikhail Rachinskiy (jewelcourses.com)',
	'version': (2000,),
	'blender': (2, 74, 0),
	'location': '3D View > Tool Shelf',
	'description': 'Super add-on for super fast booleans.',
	'wiki_url': 'https://github.com/mrachinskiy/booltron#readme',
	'tracker_url': 'https://github.com/mrachinskiy/booltron/issues',
	'category': 'Object'}


if 'bpy' in locals():
	from importlib import reload
	reload(ui)
	reload(operators)
	del reload
else:
	import bpy
	from bpy.types import AddonPreferences
	from bpy.props import EnumProperty
	from . import (ui, operators)


class Preferences(AddonPreferences):
	bl_idname = __package__

	solver = EnumProperty(
		name='Boolean Solver',
		items=(('BMESH', 'BMesh', ''),
		       ('CARVE', 'Carve', '')),
		default='BMESH',
		description='Specify solver for boolean operations')

	def draw(self, context):
		layout = self.layout
		split = layout.split(percentage=0.15)

		col = split.column()
		col.label('Boolean Solver:')

		col = split.column()
		colrow = col.row()
		colrow.alignment = 'LEFT'
		colrow.prop(self, 'solver', text='')
		if bpy.app.version < (2, 78, 0):
			colrow.label('Works only with Blender 2.78 or later', icon='QUESTION')


classes = (
	Preferences,

	ui.ToolShelf,

	operators.UNION,
	operators.DIFFERENCE,
	operators.INTERSECT,
	operators.SLICE,
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
