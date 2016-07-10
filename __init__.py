bl_info = {
	'name': 'Booltron',
	'author': 'Mikhail Rachinskiy (jewelcourses.com)',
	'version': (2000, ),
	'blender': (2, 74, 0),
	'location': '3D View > Tool Shelf',
	'description': 'Super add-on for super fast booleans.',
	'wiki_url': 'https://github.com/mrachinskiy/booltron#readme',
	'tracker_url': 'https://github.com/mrachinskiy/booltron/issues',
	'category': 'Object'}


if 'bpy' in locals():
	from importlib import reload
	reload(operators)
	reload(tools)
	reload(ui)
	del reload
else:
	import bpy
	from . import (operators, ui)


classes = (
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
