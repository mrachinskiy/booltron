import bpy
from bpy.types import (Panel, Menu)


class ToolShelf(Panel):

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

		layout.enabled = len(context.selected_objects) > 1

		col = layout.column(align=True)
		col.operator("booltron.union", text="Union")
		col.operator("booltron.difference", text="Difference")
		col.operator("booltron.intersect", text="Intersect")

		col.separator()
		col.operator("booltron.separate", text="Separate")


class Popup(Menu):

	bl_label = "Booltron"
	bl_idname = "BOOLTRON_POPUP"

	def draw(self, context):
		layout = self.layout
		layout.operator_context = 'INVOKE_REGION_WIN'

		layout.enabled = len(context.selected_objects) > 1

		layout.operator("booltron.union", text="Union")
		layout.operator("booltron.difference", text="Difference")
		layout.operator("booltron.intersect", text="Intersect")

		layout.separator()
		layout.operator("booltron.separate", text="Separate")
