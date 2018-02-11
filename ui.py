from bpy.types import Panel

from .versioning import solver_option

# Extern
from . import addon_updater_ops


class Setup:
	bl_category = 'Booltron'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = 'objectmode'

	@classmethod
	def poll(cls, context):
		return context.active_object is not None


class VIEW3D_PT_Booltron_Options(Panel, Setup):
	bl_label = 'Options'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout

		prefs = context.user_preferences.addons[__package__].preferences

		if solver_option:
			layout.prop(prefs, 'solver', text='')
		layout.prop(prefs, 'method', text='')
		layout.prop(prefs, 'triangulate')
		layout.prop(prefs, 'pos_correct')

		row = layout.row()
		row.enabled = prefs.pos_correct
		row.prop(prefs, 'pos_ofst')


class VIEW3D_PT_Booltron_Tools(Panel, Setup):
	bl_label = 'Tools'

	def draw(self, context):
		layout = self.layout

		# Updater
		# ----------------
		addon_updater_ops.check_for_update_background(context)
		addon_updater_ops.update_notice_box_ui(self, context)
		# ----------------

		obs = len(context.selected_objects)

		col = layout.column(align=True)
		col.enabled = obs > 1
		col.operator('object.booltron_union', text='Union')
		col.operator('object.booltron_difference', text='Difference')
		col.operator('object.booltron_intersect', text='Intersect')

		col = layout.column(align=True)
		col.enabled = obs == 2
		col.operator('object.booltron_slice', text='Slice')
		col.operator('object.booltron_subtract', text='Subtract')
