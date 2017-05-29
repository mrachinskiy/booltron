import bpy
from bpy.types import Panel


class UI:
	bl_category = 'Booltron'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = 'objectmode'

	@classmethod
	def poll(cls, context):
		return context.active_object is not None


class Options(UI, Panel):
	bl_label = 'Options'
	bl_idname = 'booltron_options'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout

		prefs = context.user_preferences.addons[__package__].preferences

		layout.prop(prefs, 'solver', text='')
		layout.prop(prefs, 'triangulate')


class Tools(UI, Panel):
	bl_label = 'Tools'
	bl_idname = 'booltron_tools'

	def draw(self, context):
		layout = self.layout

		obs = len(context.selected_objects)

		layout.enabled = obs > 1

		col = layout.column(align=True)
		col.operator('object.booltron_union', text='Union')
		col.operator('object.booltron_difference', text='Difference')
		col.operator('object.booltron_intersect', text='Intersect')

		col = layout.column(align=True)
		col.enabled = obs == 2
		col.operator('object.booltron_slice', text='Slice')
		col.operator('object.booltron_subtract', text='Subtract')
