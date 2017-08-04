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
	importlib.reload(preferences)
	importlib.reload(mesh_utils)
	importlib.reload(boolean_methods)
	importlib.reload(operators)
	importlib.reload(ui)
else:
	import bpy

	from . import ui, operators, locale, preferences


classes = (
	preferences.Preferences,

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
