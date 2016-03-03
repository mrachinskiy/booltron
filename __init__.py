bl_info = {
	"name": "Booltron",
	"author": "Mikhail Rachinskiy (jewelcourses.com)",
	"version": (2000,),
	"blender": (2,7,4),
	"location": "3D View → Tool Shelf (F B)",
	"description": "Booltron—super add-on for super fast booleans.",
	"wiki_url": "https://github.com/mrachinskiy/blender-addon-booltron",
	"tracker_url": "https://github.com/mrachinskiy/blender-addon-booltron/issues",
	"category": "Mesh"}

if "bpy" in locals():
	from importlib import reload
	reload(helpers)
	reload(operators)
	reload(ui)
	del reload
else:
	import bpy
	from . import operators
	from . import ui


classes = (
	ui.ToolShelf,
	ui.Popup,

	operators.UNION,
	operators.DIFFERENCE,
	operators.INTERSECT,
	operators.SEPARATE,
)

addon_keymaps = []


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	kc = bpy.context.window_manager.keyconfigs.addon
	km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
	kmi = km.keymap_items.new('wm.call_menu', 'B', 'PRESS', key_modifier='F')
	kmi.properties.name = 'BOOLTRON_POPUP'
	addon_keymaps.append((km, kmi))

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

if __name__ == "__main__":
	register()
