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

import bpy


def object_prepare():
	bpy.ops.object.make_single_user(type="SELECTED_OBJECTS", object=True, obdata=True)
	bpy.ops.object.convert(target="MESH")


def mesh_cleanup():
	bpy.ops.mesh.select_all(action="SELECT")
	bpy.ops.mesh.remove_doubles(threshold=0.0001)
	bpy.ops.mesh.delete_loose()
	bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_multi_face=False, use_non_contiguous=False, use_verts=False)
	bpy.ops.mesh.fill(use_beauty=True)
	bpy.ops.mesh.select_all(action="SELECT")
	bpy.ops.mesh.normals_make_consistent(inside=False)


def mesh_selection(ob, select_action, context):
	obj = context.active_object
	
	context.scene.objects.active = ob
	bpy.ops.object.mode_set(mode="EDIT")
	mesh_cleanup()
	bpy.ops.mesh.select_all(action=select_action)

	bpy.ops.object.mode_set(mode="OBJECT")
	context.scene.objects.active = obj


def modifier_boolean(obj, ob, mode, context):
	md = obj.modifiers.new('Booltron', 'BOOLEAN')
	md.operation = mode
	md.object = ob
	
	bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Booltron")
	context.scene.objects.unlink(ob)
	bpy.data.objects.remove(ob)


def object_duplicate(ob, context):
	obj = context.active_object

	bpy.ops.object.select_all(action = "DESELECT")
	bpy.ops.object.select_pattern(pattern = ob.name)
	bpy.ops.object.duplicate()
	obj_copy = context.selected_objects[0]

	context.scene.objects.active = obj
	return obj_copy




def union(context):
	mode = 'UNION'
	obj = context.active_object

	object_prepare()
	obj.select = False
	obs = context.selected_objects

	mesh_selection(obj, 'DESELECT', context)
	for ob in obs:
		mesh_selection(ob, 'SELECT', context)
		modifier_boolean(obj, ob, mode, context)
	obj.select = True


def intersect(context):
	mode = 'INTERSECT'
	obj = context.active_object

	object_prepare()
	obj.select = False
	obs = context.selected_objects

	mesh_selection(obj, 'DESELECT', context)
	for ob in obs:
		mesh_selection(ob, 'SELECT', context)
		modifier_boolean(obj, ob, mode, context)
	obj.select = True


def difference(context):
	mode = 'DIFFERENCE'
	obj = context.active_object

	object_prepare()
	obj.select = False
	obs = context.selected_objects
	ob = obs[0]
	
	if len(obs) != 1:
		context.scene.objects.active = ob
		bpy.ops.object.join()
		context.scene.objects.active = obj
	
	mesh_selection(obj, 'DESELECT', context)
	mesh_selection(ob, 'SELECT', context)
	modifier_boolean(obj, ob, mode, context)
	obj.select = True


def separate(context):
	obj = context.active_object

	object_prepare()
	obj.select = False
	obs = context.selected_objects

	for ob in obs:
		context.scene.objects.active = ob
		obj_copy = object_duplicate(obj, context)
		ob_copy = object_duplicate(ob, context)
		mode = 'INTERSECT'

		mesh_selection(obj_copy, 'SELECT', context)
		mesh_selection(ob, 'DESELECT', context)
		modifier_boolean(ob, obj_copy, mode, context)
		mesh_selection(ob, 'INVERT', context)
		context.scene.objects.active = obj
	
	mode = 'DIFFERENCE'
	mesh_selection(ob_copy, 'SELECT', context)
	mesh_selection(obj, 'DESELECT', context)
	modifier_boolean(obj, ob_copy, mode, context)
	obj.select = True