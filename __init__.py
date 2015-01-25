# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2012 Mikhail Rachinskiy
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ##### END MIT LICENSE BLOCK #####

bl_info = {
	"name": "Booltron",
	"author": "Mikhail Rachinskiy jewelcourses.com",
	"version": (2000,0),
	"blender": (2, 7, 3),
	"location": "3D View > Tool shelf, Shift-Ctrl-B",
	"description": "Booltron - super addon for super fast booleans",
	"warning": "",
	"wiki_url": "http://jewelcourses.com",
	"tracker_url": "http://jewelcourses.com",
	"category": "3D View"}

if "bpy" in locals():
	import importlib
	importlib.reload(operators)
	importlib.reload(ui)
	importlib.reload(helpers)
else:
	import bpy
	from bpy.types import (Panel, Menu)
	from . import operators
	from . import ui

classes = [
	ui.BooltronPanel,
	ui.BooltronMenu,
	
	operators.OT_UNION,
	operators.OT_DIFFERENCE,
	operators.OT_INTERSECT,
	operators.OT_SEPARATE,
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
		kmi = km.keymap_items.new('wm.call_menu', 'B', 'PRESS', ctrl=True, shift=True)
		kmi.properties.name = "OBJECT_PT_BOOLTRON_MENU"

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		km = kc.keymaps["3D View"]
		for kmi in km.keymap_items:
			if kmi.idname == 'wm.call_menu':
				if kmi.properties.name == "OBJECT_PT_BOOLTRON_MENU":
					km.keymap_items.remove(kmi)
					break

if __name__ == "__main__":
	register()