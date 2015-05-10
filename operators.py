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
from bpy.types import Operator
from . import helpers


class UNION(Operator):
	'''Performes a boolean union operation'''
	bl_idname = "booltron.union"
	bl_label = "Union"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		helpers.union()
		return {'FINISHED'}


class DIFFERENCE(Operator):
	'''Performes a boolean difference operation'''
	bl_idname = "booltron.difference"
	bl_label = "Difference"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		helpers.difference()
		return {'FINISHED'}


class INTERSECT(Operator):
	'''Performes a boolean intersect operation'''
	bl_idname = "booltron.intersect"
	bl_label = "Intersect"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		helpers.intersect()
		return {'FINISHED'}


class SEPARATE(Operator):
	'''Separates the active object along the intersection of the selected object (can handle only two objects at the time)'''
	bl_idname = "booltron.separate"
	bl_label = "Separate"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects) == 2

	def execute(self, context):
		helpers.separate()
		return {'FINISHED'}
