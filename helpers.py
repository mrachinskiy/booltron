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
	ops_ob = bpy.ops.object
	ops_ob.make_single_user(type="SELECTED_OBJECTS", object=True, obdata=True)
	ops_ob.convert(target="MESH")


def mesh_selection(ob, select_action):
	context = bpy.context
	sce = context.scene
	obj = context.active_object
	ops = bpy.ops
	ops_me = bpy.ops.mesh
	ops_ob = ops.object


	def mesh_cleanup():
		ops_me.select_all(action="SELECT")
		ops_me.remove_doubles()
		ops_me.delete_loose()
		ops_me.select_mode(type='EDGE')
		ops_me.select_non_manifold(extend=False, use_wire=False, use_multi_face=False, use_non_contiguous=False, use_verts=False)
		ops_me.fill()
		ops_me.select_all(action="SELECT")
		ops_me.normals_make_consistent()


	sce.objects.active = ob
	ops_ob.mode_set(mode="EDIT")

	mesh_cleanup()
	ops_me.select_all(action=select_action)

	ops_ob.mode_set(mode="OBJECT")
	sce.objects.active = obj


def modifier_boolean(obj, ob, mode):
	md = obj.modifiers.new('Booltron', 'BOOLEAN')
	md.show_viewport = False
	md.show_render = False
	md.operation = mode
	md.object = ob

	bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Booltron")
	bpy.context.scene.objects.unlink(ob)
	bpy.data.objects.remove(ob)


def boolean_optimized(mode):
	context = bpy.context
	obj = context.active_object

	object_prepare()

	obj.select = False
	obs = context.selected_objects
	ob = obs[0]

	if len(obs) != 1:
		context.scene.objects.active = ob
		bpy.ops.object.join()
		context.scene.objects.active = obj

	mesh_selection(obj, 'DESELECT')
	mesh_selection(ob, 'SELECT')
	modifier_boolean(obj, ob, mode)
	obj.select = True


def boolean_each(mode):
	context = bpy.context
	obj = context.active_object

	object_prepare()

	obj.select = False
	obs = context.selected_objects

	mesh_selection(obj, 'DESELECT')
	for ob in obs:
		mesh_selection(ob, 'SELECT')
		modifier_boolean(obj, ob, mode)
	obj.select = True






def union():
	context = bpy.context
	mode = 'UNION'


	def separate():
		ops = bpy.ops
		ops_ob = ops.object
		ops_ob.mode_set(mode="EDIT")
		ops.mesh.separate(type="LOOSE")
		ops_ob.mode_set(mode="OBJECT")


	boolean_optimized(mode)
	separate()
	if len(context.selected_objects) != 1:
		boolean_each(mode)


def intersect():
	mode = 'INTERSECT'
	boolean_each(mode)


def difference():
	mode = 'DIFFERENCE'
	boolean_optimized(mode)


def separate():
	context = bpy.context
	sce = context.scene
	obj = context.active_object


	def object_duplicate(ob):
		ops_ob = bpy.ops.object
		ops_ob.select_all(action="DESELECT")
		ops_ob.select_pattern(pattern=ob.name)
		ops_ob.duplicate()
		return context.selected_objects[0]


	object_prepare()

	obj.select = False
	ob = context.selected_objects[0]

	obj_copy = object_duplicate(obj)
	ob_copy = object_duplicate(ob)

	mode = 'INTERSECT'
	mesh_selection(obj_copy, 'SELECT')
	mesh_selection(ob, 'DESELECT')
	sce.objects.active = ob
	modifier_boolean(ob, obj_copy, mode)

	mode = 'DIFFERENCE'
	mesh_selection(ob_copy, 'SELECT')
	mesh_selection(obj, 'DESELECT')
	sce.objects.active = obj
	modifier_boolean(obj, ob_copy, mode)
	obj.select = True
