# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2014-2018  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import random

import bpy
from mathutils import Vector


class ObjectUtils:

    def object_add(self, name):
        me = bpy.data.meshes.new(name)
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.objects.link(ob)
        return ob

    def object_remove(self, ob):
        me = ob.data
        bpy.context.scene.objects.unlink(ob)  # pre 2.78 compatibility
        bpy.data.objects.remove(ob)
        bpy.data.meshes.remove(me)

    def object_pos_correct(self, obs):
        for ob in obs:
            x = random.uniform(-self.pos_offset, self.pos_offset)
            y = random.uniform(-self.pos_offset, self.pos_offset)
            z = random.uniform(-self.pos_offset, self.pos_offset)

            ob.location += Vector((x, y, z))
