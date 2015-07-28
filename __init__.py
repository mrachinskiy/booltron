bl_info = {
	"name": "Booltron",
	"author": "Mikhail Rachinskiy (jewelcourses.com)",
	"version": (2000,),
	"blender": (2,7,4),
	"location": "3D View → Tool Shelf (Shift Ctrl B)",
	"description": "Booltron—super add-on for super fast booleans.",
	"wiki_url": "https://github.com/mrachinskiy/blender-addon-booltron",
	"tracker_url": "https://github.com/mrachinskiy/blender-addon-booltron/issues",
	"category": "Mesh"}

if "bpy" in locals():
	import importlib
	importlib.reload(helpers)
	importlib.reload(operators)
	importlib.reload(ui)
else:
	import bpy
	from bpy.types import (Panel, Menu)
	from . import operators
	from . import ui


classes = (
	ui.BooltronPanel,
	ui.BooltronMenu,

	operators.UNION,
	operators.DIFFERENCE,
	operators.INTERSECT,
	operators.SEPARATE,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
		kmi = km.keymap_items.new('wm.call_menu', 'B', 'PRESS', ctrl=True, shift=True)
		kmi.properties.name = 'BOOLTRON_MENU'

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		km = kc.keymaps['3D View']
		for kmi in km.keymap_items:
			if kmi.idname == 'wm.call_menu':
				if kmi.properties.name == 'BOOLTRON_MENU':
					km.keymap_items.remove(kmi)
					break

if __name__ == "__main__":
	register()
