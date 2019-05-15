# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Booltron super add-on for super fast booleans.
#  Copyright (C) 2014-2019  Mikhail Rachinskiy
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


class ObjectUtils:

    def object_add(self, name):
        me = bpy.data.meshes.new(name)
        ob = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(ob)
        return ob

    def object_remove(self, ob):
        me = ob.data
        bpy.data.objects.remove(ob)
        bpy.data.meshes.remove(me)

    def object_pos_offset(self, obs):
        for ob in obs:
            x = random.uniform(-self.pos_offset, self.pos_offset)
            y = random.uniform(-self.pos_offset, self.pos_offset)
            z = random.uniform(-self.pos_offset, self.pos_offset)

            ob.matrix_world[0][3] += x
            ob.matrix_world[1][3] += y
            ob.matrix_world[2][3] += z
