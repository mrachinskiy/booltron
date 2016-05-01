import bpy


def object_prepare():
	ops_ob = bpy.ops.object
	ops_ob.make_single_user(object=True, obdata=True)
	ops_ob.convert(target="MESH")


def mesh_selection(ob, select_action):
	context = bpy.context
	scene = context.scene
	obj = context.active_object
	ops_me = bpy.ops.mesh
	ops_ob = bpy.ops.object

	def mesh_cleanup():
		ops_me.select_all(action="SELECT")
		ops_me.delete_loose()
		ops_me.select_all(action="SELECT")
		ops_me.remove_doubles(threshold=0.0001)
		ops_me.fill_holes(sides=0)
		ops_me.normals_make_consistent()

	scene.objects.active = ob
	ops_ob.mode_set(mode="EDIT")

	mesh_cleanup()
	ops_me.select_all(action=select_action)

	ops_ob.mode_set(mode="OBJECT")
	scene.objects.active = obj


def modifier_boolean(obj, ob, mode, delete_not=False):
	md = obj.modifiers.new("Immediate apply", 'BOOLEAN')
	md.show_viewport = False
	md.show_render = False
	md.operation = mode
	md.object = ob

	bpy.ops.object.modifier_apply(modifier="Immediate apply")
	if delete_not is True:
		return
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


def objects_get():
	context = bpy.context
	obj = context.active_object

	object_prepare()

	obj.select = False
	ob = context.selected_objects[0]

	mesh_selection(obj, 'DESELECT')
	mesh_selection(ob, 'SELECT')

	return obj, ob
