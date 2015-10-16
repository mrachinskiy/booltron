import bpy


def object_prepare():
	ops_ob = bpy.ops.object
	ops_ob.make_single_user(object=True, obdata=True)
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
		ops_me.delete_loose()
		ops_me.select_all(action="SELECT")
		ops_me.remove_doubles(threshold=0.0001)
		ops_me.fill_holes(sides=0)
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

	bpy.ops.object.modifier_apply(modifier="Booltron")
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
