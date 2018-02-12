bl_info = {
	'name': 'Booltron',
	'author': 'Mikhail Rachinskiy (jewelcourses.com)',
	'version': (2, 0, 1),
	'blender': (2, 74, 0),
	'location': '3D View > Tool Shelf',
	'description': 'Super add-on for super fast booleans.',
	'wiki_url': 'https://github.com/mrachinskiy/booltron#readme',
	'tracker_url': 'https://github.com/mrachinskiy/booltron/issues',
	'category': 'Object',
	}


if 'bpy' in locals():
	import importlib
	importlib.reload(versioning)
	importlib.reload(locale)
	importlib.reload(preferences)
	importlib.reload(mesh_utils)
	importlib.reload(boolean_methods)
	importlib.reload(operators)
	importlib.reload(ui)
else:
	import bpy

	from . import ui, operators, locale, preferences

	# Extern
	from . import addon_updater_ops


classes = (
	preferences.PREFS_Booltron_Props,

	ui.VIEW3D_PT_Booltron_Options,
	ui.VIEW3D_PT_Booltron_Tools,

	operators.OBJECT_OT_Booltron_Union,
	operators.OBJECT_OT_Booltron_Difference,
	operators.OBJECT_OT_Booltron_Intersect,
	operators.OBJECT_OT_Booltron_Slice,
	operators.OBJECT_OT_Booltron_Subtract,
	)


def register():
	addon_updater_ops.register(bl_info)

	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.app.translations.register(__name__, locale.lc_reg)


def unregister():
	addon_updater_ops.unregister()

	for cls in classes:
		bpy.utils.unregister_class(cls)

	bpy.app.translations.unregister(__name__)


if __name__ == '__main__':
	register()
