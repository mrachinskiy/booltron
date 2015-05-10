# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2014 Mikhail Rachinskiy
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
	O = bpy.ops.object

	O.make_single_user(type="SELECTED_OBJECTS", object=True, obdata=True)
	O.convert(target="MESH")


def mesh_selection(ob, select_action):
	O = bpy.ops
	ops_ob = O.object
	ops_me = O.mesh
	C = bpy.context
	sce = C.scene
	obj = C.active_object

	sce.objects.active = ob
	ops_ob.mode_set(mode="EDIT")


	def mesh_cleanup():
		ops_me.select_all(action="SELECT")
		ops_me.remove_doubles()
		ops_me.delete_loose()
		ops_me.select_mode(type='EDGE')
		ops_me.select_non_manifold(extend=False, use_wire=False, use_multi_face=False, use_non_contiguous=False, use_verts=False)
		ops_me.fill()
		ops_me.select_all(action="SELECT")
		ops_me.normals_make_consistent()


	mesh_cleanup()
	ops_me.select_all(action=select_action)

	ops_ob.mode_set(mode="OBJECT")
	sce.objects.active = obj


def modifier_boolean(obj, ob, mode):
	md = obj.modifiers.new('Booltron', 'BOOLEAN')
	md.operation = mode
	md.object = ob

	bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Booltron")
	bpy.context.scene.objects.unlink(ob)
	bpy.data.objects.remove(ob)






def union():
	C = bpy.context
	mode = 'UNION'
	obj = C.active_object

	object_prepare()

	obj.select = False
	obs = C.selected_objects

	mesh_selection(obj, 'DESELECT')
	for ob in obs:
		mesh_selection(ob, 'SELECT')
		modifier_boolean(obj, ob, mode)
	obj.select = True


def intersect():
	C = bpy.context
	mode = 'INTERSECT'
	obj = C.active_object

	object_prepare()

	obj.select = False
	obs = C.selected_objects

	mesh_selection(obj, 'DESELECT')
	for ob in obs:
		mesh_selection(ob, 'SELECT')
		modifier_boolean(obj, ob, mode)
	obj.select = True


def difference():
	C = bpy.context
	mode = 'DIFFERENCE'
	obj = C.active_object

	object_prepare()

	obj.select = False
	obs = C.selected_objects
	ob = obs[0]

	if len(obs) != 1:
		C.scene.objects.active = ob
		bpy.ops.object.join()
		C.scene.objects.active = obj

	mesh_selection(obj, 'DESELECT')
	mesh_selection(ob, 'SELECT')
	modifier_boolean(obj, ob, mode)
	obj.select = True


def separate():
	C = bpy.context
	obj = C.active_object

	object_prepare()

	obj.select = False
	obs = C.selected_objects


	def object_duplicate(ob):
		O = bpy.ops.object

		O.select_all(action = "DESELECT")
		O.select_pattern(pattern = ob.name)
		O.duplicate()
		obj_copy = C.selected_objects[0]

		C.scene.objects.active = obj
		return obj_copy


	for ob in obs:
		C.scene.objects.active = ob
		obj_copy = object_duplicate(obj)
		ob_copy = object_duplicate(ob)
		mode = 'INTERSECT'

		mesh_selection(obj_copy, 'SELECT')
		mesh_selection(ob, 'DESELECT')
		modifier_boolean(ob, obj_copy, mode)
		mesh_selection(ob, 'INVERT')
		C.scene.objects.active = obj

	mode = 'DIFFERENCE'
	mesh_selection(ob_copy, 'SELECT')
	mesh_selection(obj, 'DESELECT')
	modifier_boolean(obj, ob_copy, mode)
	obj.select = True
