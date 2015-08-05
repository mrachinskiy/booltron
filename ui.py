import bpy
from bpy.types import (Panel, Menu)


class BooltronPanel(Panel):

	bl_label = "Booltron"
	bl_idname = "Booltron Panel"
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
		col.operator("booltron.union", text="Union")
		col.operator("booltron.difference", text="Difference")
		col.operator("booltron.intersect", text="Intersect")

		col.separator()
		col.operator("booltron.separate", text="Separate")


class BooltronPopup(Menu):

	bl_label = "Booltron"
	bl_idname = "Booltron Popup"

	def draw(self, context):
		layout = self.layout
		layout.operator_context = 'INVOKE_REGION_WIN'

		if len(context.selected_objects) < 2:
			layout.enabled = False

		layout.operator("booltron.union", text="Union")
		layout.operator("booltron.difference", text="Difference")
		layout.operator("booltron.intersect", text="Intersect")

		layout.separator()
		layout.operator("booltron.separate", text="Separate")
