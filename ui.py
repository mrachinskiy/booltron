import bpy
from bpy.types import (Panel, Menu)


class BooltronPanel(Panel):

	bl_label = "Booltron"
	bl_idname = "BOOLTRON_PANEL"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Booltron"

	@classmethod
	def poll(cls, context):
		return (context.active_object and context.mode == 'OBJECT')

	def draw(self, context):
		layout = self.layout

		if len(context.selected_objects) < 2:
			layout.enabled = False

		col = layout.column(align=True)
		col.operator("booltron.union")
		col.operator("booltron.difference")
		col.operator("booltron.intersect")

		col.separator()
		col.operator("booltron.separate")


class BooltronMenu(Menu):

	bl_label = "Booltron"
	bl_idname = "BOOLTRON_MENU"

	def draw(self, context):
		layout = self.layout
		layout.operator_context = 'INVOKE_REGION_WIN'

		if len(context.selected_objects) < 2:
			layout.enabled = False

		layout.operator("booltron.union")
		layout.operator("booltron.difference")
		layout.operator("booltron.intersect")

		layout.separator()
		layout.operator("booltron.separate")
